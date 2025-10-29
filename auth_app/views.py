
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from .models import User
import os
from rest_framework.permissions import AllowAny
# from .utils import compare_face
# import face_recognition
import uuid
import os
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser



class RegisterAPI(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "success": True,
                "message": "Compte créé avec succès !",
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "success": True,
                "message": f"Bienvenue {user.username} !",
                "user": UserSerializer(user).data,  # maintenant is_superuser est inclus
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })
        return Response({
            "success": False,
            "message": "Nom d'utilisateur ou mot de passe invalide."
        }, status=status.HTTP_401_UNAUTHORIZED)

class FaceLoginAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        image_file = request.FILES.get("image")
        if not image_file:
            print("[FaceLoginAPI] No image received")
            return Response({"error": "Image required"}, status=400)

        tmp_filename = f"{uuid.uuid4()}.jpg"
        tmp_path = os.path.join(settings.MEDIA_ROOT, "tmp", tmp_filename)
        os.makedirs(os.path.dirname(tmp_path), exist_ok=True)

        # Sauvegarder temporairement
        try:
            with open(tmp_path, "wb") as f:
                for chunk in image_file.chunks():
                    f.write(chunk)
            print(f"[FaceLoginAPI] Image saved temporarily at {tmp_path}")

            # uploaded_image = face_recognition.load_image_file(tmp_path)
            # uploaded_encodings = face_recognition.face_encodings(uploaded_image)

            # if not uploaded_encodings:
            #     print("[FaceLoginAPI] No face detected in uploaded image")
            #     return Response({"error": "No face detected"}, status=400)

            # uploaded_encoding = uploaded_encodings[0]
            print("[FaceLoginAPI] Face detected in uploaded image")

            # Comparer avec toutes les images d'utilisateurs
            users = User.objects.exclude(image__isnull=True)
            print(f"[FaceLoginAPI] Checking {users.count()} users in database")

            for user in users:
                stored_path = os.path.join(settings.MEDIA_ROOT, user.image.name)
                if not os.path.exists(stored_path):
                    print(f"[FaceLoginAPI] Stored image not found for user {user.username}")
                    continue

                # stored_image = face_recognition.load_image_file(stored_path)
                # stored_encodings = face_recognition.face_encodings(stored_image)
                # if not stored_encodings:
                #     print(f"[FaceLoginAPI] No face detected in stored image for user {user.username}")
                #     continue

                # if compare_face(stored_encodings[0].tolist(), tmp_path):
                #     refresh = RefreshToken.for_user(user)
                #     print(f"[FaceLoginAPI] Face match found: {user.username}")
                #     return Response({
                #         "success": True,
                #         "user": UserSerializer(user).data,
                #         "refresh": str(refresh),
                #         "access": str(refresh.access_token)
                #     })

            print("[FaceLoginAPI] No matching face found")
            return Response({"success": False, "message": "No matching face found"}, status=401)

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                print(f"[FaceLoginAPI] Temporary file {tmp_path} removed")

class LogoutAPI(APIView):

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token required"}, status=400)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Nécessite rest_framework_simplejwt.token_blacklist
            return Response({"success": True, "message": "Déconnecté avec succès"})
        except Exception:
            return Response({"error": "Token invalide ou déjà blacklisted"}, status=400)
        


class UserListAPI(APIView):
    permission_classes = [IsAdminUser]  # seulement les superusers

    def get(self, request):
        users = User.objects.all().order_by("-id")
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
class UserDetailAPI(APIView):
    permission_classes = [IsAdminUser]  # seulement superusers

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    # Récupérer un utilisateur
    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    # Éditer un utilisateur
    def put(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            if 'password' in request.data and request.data['password']:
                user.set_password(request.data['password'])
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Supprimer un utilisateur
    def delete(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserProfileAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Récupérer le profil de l'utilisateur connecté
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """
        Mettre à jour le profil de l'utilisateur connecté
        """
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "user": serializer.data})
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)