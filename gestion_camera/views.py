from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Camera
from .serializers import CameraSerializer
from .fire_detection_service import fire_detector
from PIL import Image
import io


class CameraListCreateAPIView(APIView):
    """
    GET: List all cameras
    POST: Create a new camera
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request):
        cameras = Camera.objects.all()
        serializer = CameraSerializer(cameras, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CameraSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CameraDetailAPIView(APIView):
    """
    GET: Retrieve a single camera
    PUT: Update a camera (full update)
    PATCH: Partial update a camera
    DELETE: Delete a camera
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    def get_object(self, pk):
        return get_object_or_404(Camera, pk=pk)

    def get(self, request, pk):
        camera = self.get_object(pk)
        serializer = CameraSerializer(camera)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        camera = self.get_object(pk)
        serializer = CameraSerializer(camera, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        camera = self.get_object(pk)
        serializer = CameraSerializer(camera, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        camera = self.get_object(pk)
        camera.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FireDetectionAPIView(APIView):
    """
    POST: Detect fire in uploaded image using AI
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            # Get uploaded image
            image_file = request.FILES.get('image')
            if not image_file:
                return Response(
                    {'error': 'No image provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Read image data
            image_data = image_file.read()
            
            # Detect fire using AI service
            result = fire_detector.detect_fire_in_image(image_data)
            
            # Convert annotated image to base64 for response
            annotated_image_base64 = None
            if result['annotated_image']:
                annotated_image_base64 = fire_detector.image_to_base64(result['annotated_image'])
            
            # Determine alert level
            alert_level = 'NORMAL'
            if result['fire_detected'] and result['smoke_detected']:
                alert_level = 'CRITICAL'
            elif result['fire_detected']:
                alert_level = 'HIGH'
            elif result['smoke_detected']:
                alert_level = 'HIGH'
            
            # Create response message
            if result['fire_detected'] or result['smoke_detected']:
                detected_items = []
                if result['fire_detected']:
                    detected_items.append('🔥 FIRE')
                if result['smoke_detected']:
                    detected_items.append('💨 SMOKE')
                message = f"⚠️ ALERT: {' and '.join(detected_items)} detected! Confidence: {result['confidence']:.1%}"
            else:
                message = "✅ No fire or smoke detected. Environment is safe."
            
            return Response({
                'success': True,
                'fire_detected': result['fire_detected'],
                'smoke_detected': result['smoke_detected'],
                'confidence': result['confidence'],
                'detections': result['detections'],
                'annotated_image_base64': annotated_image_base64,
                'alert_level': alert_level,
                'message': message
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Fire detection failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FireDetectionHeuristicAPIView(APIView):
    """
    POST: Detect fire using color-based heuristic method (fallback)
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            # Get uploaded image
            image_file = request.FILES.get('image')
            if not image_file:
                return Response(
                    {'error': 'No image provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Read image data
            image_data = image_file.read()
            
            # Detect fire using heuristic method
            result = fire_detector.detect_fire_heuristic(image_data)
            
            # Convert annotated image to base64
            annotated_image_base64 = None
            if result['annotated_image']:
                annotated_image_base64 = fire_detector.image_to_base64(result['annotated_image'])
            
            # Determine alert level
            alert_level = 'HIGH' if result['fire_detected'] else 'NORMAL'
            
            # Create response message
            message = "🔥 Fire-like colors detected!" if result['fire_detected'] else "✅ No fire detected."
            
            return Response({
                'success': True,
                'fire_detected': result['fire_detected'],
                'smoke_detected': result['smoke_detected'],
                'confidence': result['confidence'],
                'detections': result['detections'],
                'annotated_image_base64': annotated_image_base64,
                'alert_level': alert_level,
                'message': message,
                'method': 'heuristic'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Fire detection failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
