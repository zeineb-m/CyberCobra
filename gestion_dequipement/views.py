from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.shortcuts import get_object_or_404
from PIL import Image, ImageFilter
import io
import os
import numpy as np
import cv2
from .models import Equipement
from .serializers import EquipementSerializer


class ImageHashMixin:
    """Mixin containing all image processing and hashing logic"""
    
    # --- Helpers for perceptual hashing ---
    def _average_hash(self, img: Image.Image, hash_size: int = 8) -> str:
        """Return 64-bit average hash as 16-hex string."""
        # Use BICUBIC for compatibility
        resample_method = Image.BICUBIC if hasattr(Image, 'BICUBIC') else 3
        img = img.convert('L').resize((hash_size, hash_size), resample_method)
        pixels = list(img.getdata())
        avg = sum(pixels) / len(pixels) if pixels else 0
        bits = ''.join('1' if p > avg else '0' for p in pixels)
        # Convert bits to hex
        return f"{int(bits, 2):016x}"

    def _dct2(self, a: np.ndarray) -> np.ndarray:
        # Type-II DCT implemented via FFT (orthonormalized)
        # This avoids SciPy dependency
        return np.real(np.fft.fft2(a))

    def _salient_crop(self, img: Image.Image) -> Image.Image:
        """Crop around the most salient (edgy) region to focus on the held object.
        Falls back to center-crop if edges are weak.
        """
        resample_method = Image.BICUBIC if hasattr(Image, 'BICUBIC') else 3
        g = img.convert('L').resize((256, 256), resample_method)
        arr = np.asarray(g, dtype=np.float32)
        # Sobel kernels
        Kx = np.array([[1,0,-1],[2,0,-2],[1,0,-1]], dtype=np.float32)
        Ky = np.array([[1,2,1],[0,0,0],[-1,-2,-1]], dtype=np.float32)
        # Convolve (valid via padding same)
        from numpy.lib.stride_tricks import as_strided
        def conv2(a, k):
            kh, kw = k.shape
            pad_h, pad_w = kh//2, kw//2
            ap = np.pad(a, ((pad_h,pad_h),(pad_w,pad_w)), mode='edge')
            H, W = a.shape
            # sliding windows
            shape = (H, W, kh, kw)
            strides = (ap.strides[0], ap.strides[1], ap.strides[0], ap.strides[1])
            sub = as_strided(ap, shape=shape, strides=strides)
            return np.einsum('ijkl,kl->ij', sub, k)
        gx = conv2(arr, Kx)
        gy = conv2(arr, Ky)
        mag = np.hypot(gx, gy)
        # Threshold top percentile of gradients
        th = np.percentile(mag, 80)
        mask = mag >= th
        # bounding box of mask
        coords = np.argwhere(mask)
        if coords.size == 0:
            # center crop 70%
            side = int(min(arr.shape)*0.7)
            y0 = (arr.shape[0]-side)//2
            x0 = (arr.shape[1]-side)//2
            return g.crop((x0, y0, x0+side, y0+side))
        (ymin, xmin) = coords.min(0)
        (ymax, xmax) = coords.max(0)
        # add margin
        h, w = arr.shape
        margin_y = int(0.08*h)
        margin_x = int(0.08*w)
        y0 = max(0, ymin - margin_y)
        x0 = max(0, xmin - margin_x)
        y1 = min(h-1, ymax + margin_y)
        x1 = min(w-1, xmax + margin_x)
        return g.crop((x0, y0, x1, y1))

    def _phash(self, img: Image.Image, hash_size: int = 8, highfreq_factor: int = 4) -> str:
        # Perceptual hash using DCT of grayscale + salient crop
        resample_method = Image.BICUBIC if hasattr(Image, 'BICUBIC') else 3
        img = self._salient_crop(img)
        img = img.convert('L')
        # slight blur to reduce noise
        img = img.filter(ImageFilter.GaussianBlur(radius=1))
        size = hash_size * highfreq_factor
        img = img.resize((size, size), resample_method)
        pixels = np.asarray(img, dtype=np.float32)
        # DCT approximation via FFT (good enough for hash comparisons)
        dct = self._dct2(pixels)
        dctlow = dct[:hash_size, :hash_size]
        # ignore the DC coefficient at (0,0)
        dctlow_flat = dctlow.flatten()
        med = np.median(dctlow_flat[1:]) if dctlow_flat.size > 1 else 0
        bits = ''.join('1' if v > med else '0' for v in dctlow_flat)
        return f"{int(bits, 2):0{hash_size*hash_size//4}x}"

    def _compute_multiple_phashes(self, img: Image.Image) -> dict:
        """Compute multiple phashes with different crops/transforms for robustness."""
        hashes = {}
        # Original salient crop
        hashes['salient'] = self._phash(img)
        # Center crop only (no saliency)
        resample_method = Image.BICUBIC if hasattr(Image, 'BICUBIC') else 3
        w, h = img.size
        side = int(min(w, h) * 0.75)
        x0 = (w - side) // 2
        y0 = (h - side) // 2
        center_crop = img.crop((x0, y0, x0+side, y0+side))
        hashes['center'] = self._phash_nocrop(center_crop)
        # Wider center crop
        side2 = int(min(w, h) * 0.85)
        x1 = (w - side2) // 2
        y1 = (h - side2) // 2
        wider_crop = img.crop((x1, y1, x1+side2, y1+side2))
        hashes['wide'] = self._phash_nocrop(wider_crop)
        # Slight rotations
        for angle in [-20, -10, 10, 20]:
            rot = img.rotate(angle, expand=True, resample=resample_method)
            hashes[f'rot{angle}'] = self._phash(rot)
        return hashes
    
    def _phash_nocrop(self, img: Image.Image, hash_size: int = 8, highfreq_factor: int = 4) -> str:
        """pHash without saliency crop - just resize and DCT."""
        resample_method = Image.BICUBIC if hasattr(Image, 'BICUBIC') else 3
        img = img.convert('L')
        img = img.filter(ImageFilter.GaussianBlur(radius=1))
        size = hash_size * highfreq_factor
        img = img.resize((size, size), resample_method)
        pixels = np.asarray(img, dtype=np.float32)
        dct = self._dct2(pixels)
        dctlow = dct[:hash_size, :hash_size]
        dctlow_flat = dctlow.flatten()
        med = np.median(dctlow_flat[1:]) if dctlow_flat.size > 1 else 0
        bits = ''.join('1' if v > med else '0' for v in dctlow_flat)
        return f"{int(bits, 2):0{hash_size*hash_size//4}x}"

    def _file_average_hash(self, file_obj) -> str:
        if isinstance(file_obj, (InMemoryUploadedFile, TemporaryUploadedFile)):
            image = Image.open(file_obj)
        else:
            image = Image.open(io.BytesIO(file_obj.read()))
        return self._average_hash(image)

    def _path_average_hash(self, path: str) -> str:
        with Image.open(path) as im:
            return self._average_hash(im)

    def _hamming_distance_hex64(self, h1: str, h2: str) -> int:
        try:
            x = int(h1, 16) ^ int(h2, 16)
            return x.bit_count()
        except Exception:
            return 64
    
    def _orb_feature_match(self, img1: Image.Image, img2: Image.Image) -> float:
        """
        Use ORB features to match two images - rotation and scale invariant.
        Returns a similarity score (0-100, higher is better match).
        """
        try:
            # Convert PIL to opencv
            cv_img1 = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2GRAY)
            cv_img2 = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2GRAY)
            
            # Initialize ORB detector
            orb = cv2.ORB_create(nfeatures=500)
            
            # Find keypoints and descriptors
            kp1, des1 = orb.detectAndCompute(cv_img1, None)
            kp2, des2 = orb.detectAndCompute(cv_img2, None)
            
            if des1 is None or des2 is None or len(kp1) < 10 or len(kp2) < 10:
                return 0.0
            
            # BFMatcher with Hamming distance
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            matches = bf.knnMatch(des1, des2, k=2)
            
            # Apply ratio test (Lowe's ratio test)
            good_matches = []
            for pair in matches:
                if len(pair) == 2:
                    m, n = pair
                    if m.distance < 0.75 * n.distance:
                        good_matches.append(m)
            
            # Compute similarity score
            if len(good_matches) > 0:
                # Normalize by the number of keypoints
                score = (len(good_matches) / min(len(kp1), len(kp2))) * 100
                return min(score, 100.0)
            return 0.0
        except Exception:
            return 0.0

    def _compute_and_save_hashes(self, instance):
        """Helper to compute and save image hashes for an equipment instance"""
        try:
            if instance.image and hasattr(instance.image, 'path') and os.path.exists(instance.image.path):
                instance.image_hash = self._path_average_hash(instance.image.path)
                with Image.open(instance.image.path) as im:
                    instance.phash = self._phash(im)
                instance.save(update_fields=['image_hash', 'phash'])
        except Exception:
            pass


class EquipementListCreateAPIView(ImageHashMixin, APIView):
    """
    GET: List all equipements
    POST: Create a new equipement
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        equipements = Equipement.objects.all()
        serializer = EquipementSerializer(equipements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = EquipementSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            # Compute hash if image provided
            self._compute_and_save_hashes(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EquipementDetailAPIView(ImageHashMixin, APIView):
    """
    GET: Retrieve a single equipement
    PUT: Update an equipement (full update)
    PATCH: Partial update an equipement
    DELETE: Delete an equipement
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_object(self, pk):
        return get_object_or_404(Equipement, pk=pk)

    def get(self, request, pk):
        equipement = self.get_object(pk)
        serializer = EquipementSerializer(equipement)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        equipement = self.get_object(pk)
        serializer = EquipementSerializer(equipement, data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            # If new image uploaded, recompute hash
            if 'image' in request.FILES:
                self._compute_and_save_hashes(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        equipement = self.get_object(pk)
        serializer = EquipementSerializer(equipement, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            # If new image uploaded, recompute hash
            if 'image' in request.FILES:
                self._compute_and_save_hashes(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        equipement = self.get_object(pk)
        # Optional: remove image file from disk
        try:
            if equipement.image and hasattr(equipement.image, 'path') and os.path.exists(equipement.image.path):
                os.remove(equipement.image.path)
        except Exception:
            pass
        equipement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EquipementRecognizeAPIView(ImageHashMixin, APIView):
    """
    POST: Recognize equipment from uploaded image
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """
        Recognition v2: Try perceptual hash match against stored equipment images.
        If a close match is found, return that equipment's saved statut.
        Otherwise, fall back to brightness heuristic.
        """
        file = request.FILES.get("image")
        if not file:
            return Response({"detail": "image is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1) Try ORB feature matching (rotation & scale invariant)
            uploaded = Image.open(file)
            uploaded_g = uploaded.convert('L')
            
            best_orb = None  # (equip, score)
            candidates = Equipement.objects.all()
            for eq in candidates:
                if not eq.image or not hasattr(eq.image, 'path') or not os.path.exists(eq.image.path):
                    continue
                try:
                    ref_img = Image.open(eq.image.path)
                    orb_score = self._orb_feature_match(uploaded, ref_img)
                    if orb_score > 25:  # Minimum 25% match
                        if best_orb is None or orb_score > best_orb[1]:
                            best_orb = (eq, orb_score)
                except Exception:
                    continue
            
            # If ORB found a strong match, use it
            if best_orb is not None and best_orb[1] >= 30:
                eq, orb_score = best_orb
                return Response({
                    "statut": eq.statut,
                    "matched_id": eq.id_equipement,
                    "orb_score": round(orb_score, 1),
                    "strategy": "orb-feature-match",
                })
            
            # 2) Fallback to phash matching
            up_hash = self._average_hash(uploaded_g)
            up_hashes = self._compute_multiple_phashes(uploaded)

            best = None  # (equip, score, dist_p, method)
            for eq in candidates:
                # lazy backfill if missing
                if (not eq.image_hash or not eq.phash) and eq.image and hasattr(eq.image, 'path') and os.path.exists(eq.image.path):
                    try:
                        eq.image_hash = eq.image_hash or self._path_average_hash(eq.image.path)
                        eq.phash = eq.phash or self._phash(Image.open(eq.image.path))
                        eq.save(update_fields=['image_hash', 'phash'])
                    except Exception:
                        pass
                if not eq.phash:
                    continue
                
                # Try all computed hashes and pick the minimum distance
                min_dist = 999
                best_method = "none"
                for method, h in up_hashes.items():
                    d = self._hamming_distance_hex64(h, eq.phash)
                    if d < min_dist:
                        min_dist = d
                        best_method = method
                
                if best is None or min_dist < best[1]:
                    best = (eq, min_dist, best_method)

            if best is not None:
                eq, dist_p, method = best
                # More aggressive threshold - if distance <= 24, consider it a match
                if dist_p <= 24:
                    return Response({
                        "statut": eq.statut,
                        "matched_id": eq.id_equipement,
                        "distance_phash": int(dist_p),
                        "strategy": "phash-match",
                        "method": method,
                    })

            # 2) Fallback: brightness heuristic
            img = uploaded_g
            histogram = img.histogram()
            pixels = sum(histogram)
            avg = (sum(i * count for i, count in enumerate(histogram)) / pixels) if pixels else 0
            if avg >= 140:
                statut = Equipement.Statut.AUTORISE
                confidence = 0.6
            elif avg <= 90:
                statut = Equipement.Statut.INTERDIT
                confidence = 0.6
            else:
                statut = Equipement.Statut.SOUMIS
                confidence = 0.55

            return Response({
                "statut": statut,
                "confidence": confidence,
                "avg_brightness": round(avg, 2),
                "strategy": "brightness-fallback",
            })
        except Exception as exc:
            return Response({"detail": f"failed to analyze image: {exc}"}, status=status.HTTP_400_BAD_REQUEST)
