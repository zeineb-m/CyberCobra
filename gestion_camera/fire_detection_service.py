"""
Fire Detection Service using YOLOv8 AI Model
This service provides real-time fire and smoke detection capabilities
"""

import cv2
import numpy as np
from PIL import Image
import io
import base64
from pathlib import Path

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("WARNING: ultralytics not installed. Fire detection will use fallback method.")


class FireDetectionService:
    """
    Advanced Fire Detection Service using YOLOv8 for object detection
    Falls back to color-based heuristic if YOLO is unavailable
    """
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        
        if YOLO_AVAILABLE:
            try:
                # Try to load a pre-trained YOLO model
                # YOLOv8n is the fastest, YOLOv8x is the most accurate
                self.model = YOLO('yolov8n.pt')  # Nano model for speed
                self.model_loaded = True
                print("✅ YOLOv8 model loaded successfully")
            except Exception as e:
                print(f"⚠️ Could not load YOLO model: {e}")
                print("Will use heuristic detection method")
        
    def detect_fire_in_image(self, image_data, confidence_threshold=0.3):
        """
        Detect fire and smoke in an image
        Uses color-based heuristic detection (more reliable for flames)
        Falls back to YOLOv8 if available for additional validation
        
        Args:
            image_data: Image file data (bytes, PIL Image, or file path)
            confidence_threshold: Minimum confidence for detection (0.0 to 1.0)
            
        Returns:
            dict: {
                'fire_detected': bool,
                'smoke_detected': bool,
                'detections': list of detection objects,
                'confidence': float,
                'annotated_image': PIL Image with bounding boxes
            }
        """
        
        # PRIMARY: Use heuristic method (more reliable for fire detection)
        heuristic_result = self.detect_fire_heuristic(image_data)
        
        # If fire detected by heuristic, return immediately
        if heuristic_result['fire_detected']:
            return heuristic_result
        
        # SECONDARY: Try YOLO if no fire detected by heuristic
        # Load image
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        elif isinstance(image_data, str):
            image = Image.open(image_data)
        else:
            image = image_data
            
        # Convert PIL to numpy array for OpenCV
        img_array = np.array(image)
        if len(img_array.shape) == 2:  # Grayscale
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
        elif img_array.shape[2] == 4:  # RGBA
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
            
        fire_detected = False
        smoke_detected = False
        detections = []
        max_confidence = 0.0
        annotated_image = image.copy()
        
        if self.model_loaded and self.model:
            try:
                # Run YOLOv8 inference
                results = self.model(img_array, conf=confidence_threshold)
                
                # Process results
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        # Get box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0].cpu().numpy())
                        cls = int(box.cls[0].cpu().numpy())
                        class_name = result.names[cls].lower()
                        
                        # Check for fire/smoke related classes
                        fire_keywords = ['fire', 'flame', 'burning']
                        smoke_keywords = ['smoke', 'fog', 'haze']
                        
                        is_fire = any(keyword in class_name for keyword in fire_keywords)
                        is_smoke = any(keyword in class_name for keyword in smoke_keywords)
                        
                        if is_fire:
                            fire_detected = True
                            max_confidence = max(max_confidence, conf)
                            color = (255, 0, 0)  # Red for fire
                        elif is_smoke:
                            smoke_detected = True
                            max_confidence = max(max_confidence, conf)
                            color = (128, 128, 128)  # Gray for smoke
                        else:
                            continue
                            
                        detections.append({
                            'class': class_name,
                            'confidence': conf,
                            'bbox': [float(x1), float(y1), float(x2), float(y2)]
                        })
                        
                        # Draw bounding box
                        img_array = cv2.rectangle(
                            img_array,
                            (int(x1), int(y1)),
                            (int(x2), int(y2)),
                            color,
                            3
                        )
                        
                        # Add label
                        label = f"{class_name}: {conf:.2f}"
                        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                        img_array = cv2.rectangle(
                            img_array,
                            (int(x1), int(y1) - 20),
                            (int(x1) + w, int(y1)),
                            color,
                            -1
                        )
                        img_array = cv2.putText(
                            img_array,
                            label,
                            (int(x1), int(y1) - 5),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (255, 255, 255),
                            2
                        )
                
                annotated_image = Image.fromarray(img_array)
                
            except Exception as e:
                print(f"Error in YOLO detection: {e}")
                # Already checked heuristic, return those results
                return heuristic_result
        
        # If YOLO found nothing and heuristic found nothing, return heuristic result
        if not fire_detected and not smoke_detected:
            return heuristic_result
            
        return {
            'fire_detected': fire_detected,
            'smoke_detected': smoke_detected,
            'detections': detections,
            'confidence': max_confidence,
            'annotated_image': annotated_image
        }
    
    def detect_fire_heuristic(self, image_data):
        """
        Fallback fire detection using color-based heuristic method
        Detects fire by analyzing HSV color space for fire-like colors
        Enhanced sensitivity for detecting flames, candles, and small fires
        """
        
        # Load image
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        elif isinstance(image_data, str):
            image = Image.open(image_data)
        else:
            image = image_data
            
        # Convert to OpenCV format
        img_array = np.array(image)
        if len(img_array.shape) == 2:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        elif img_array.shape[2] == 4:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        else:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
        # Convert to HSV color space for better color detection
        hsv = cv2.cvtColor(img_array, cv2.COLOR_BGR2HSV)
        
        # Also convert to LAB for luminosity analysis (bright flames)
        lab = cv2.cvtColor(img_array, cv2.COLOR_BGR2LAB)
        
        # Define fire color ranges in HSV - MORE SENSITIVE
        # Red flames (low hue)
        lower_fire1 = np.array([0, 50, 100])      # Lower saturation threshold for dimmer fires
        upper_fire1 = np.array([10, 255, 255])
        
        # Red flames (high hue wrap-around)
        lower_fire2 = np.array([170, 50, 100])
        upper_fire2 = np.array([180, 255, 255])
        
        # Orange flames
        lower_fire3 = np.array([10, 50, 100])
        upper_fire3 = np.array([25, 255, 255])
        
        # Yellow flames (very bright)
        lower_fire4 = np.array([25, 50, 150])
        upper_fire4 = np.array([35, 255, 255])
        
        # White-hot flames (low saturation, high value)
        lower_fire5 = np.array([0, 0, 200])
        upper_fire5 = np.array([180, 50, 255])
        
        # Create masks for all fire colors
        mask1 = cv2.inRange(hsv, lower_fire1, upper_fire1)
        mask2 = cv2.inRange(hsv, lower_fire2, upper_fire2)
        mask3 = cv2.inRange(hsv, lower_fire3, upper_fire3)
        mask4 = cv2.inRange(hsv, lower_fire4, upper_fire4)
        mask5 = cv2.inRange(hsv, lower_fire5, upper_fire5)
        
        # Combine all masks
        fire_mask = cv2.bitwise_or(mask1, mask2)
        fire_mask = cv2.bitwise_or(fire_mask, mask3)
        fire_mask = cv2.bitwise_or(fire_mask, mask4)
        fire_mask = cv2.bitwise_or(fire_mask, mask5)
        
        # Apply morphological operations to reduce noise
        kernel = np.ones((3, 3), np.uint8)
        fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_OPEN, kernel)
        fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_CLOSE, kernel)
        
        # Calculate fire pixel percentage
        total_pixels = fire_mask.shape[0] * fire_mask.shape[1]
        fire_pixels = cv2.countNonZero(fire_mask)
        fire_percentage = (fire_pixels / total_pixels) * 100
        
        # More sensitive threshold - detect even small flames
        fire_detected = fire_percentage > 0.5  # Lowered from 2% to 0.5% for better sensitivity
        
        # Find contours for bounding boxes
        contours, _ = cv2.findContours(fire_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        annotated_img = img_array.copy()
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 50:  # Much lower threshold (was 500) - detect even small flames like candles
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate confidence based on area and brightness
                area_score = min(area / 1000, 1.0)
                percentage_score = min(fire_percentage / 5, 1.0)
                confidence = max(area_score, percentage_score)
                confidence = min(confidence, 0.99)
                
                detections.append({
                    'class': 'fire',
                    'confidence': confidence,
                    'bbox': [float(x), float(y), float(x + w), float(y + h)]
                })
                
                # Draw bounding box - thicker and more visible
                color = (0, 0, 255)  # Red in BGR
                cv2.rectangle(annotated_img, (x, y), (x + w, y + h), color, 3)
                
                # Add background for label text
                label = f"FIRE: {confidence:.1%}"
                (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                cv2.rectangle(
                    annotated_img,
                    (x, y - label_h - 10),
                    (x + label_w + 10, y),
                    color,
                    -1
                )
                
                # Add label text
                cv2.putText(
                    annotated_img,
                    label,
                    (x + 5, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )
        
        # Convert back to RGB for PIL
        annotated_img = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
        annotated_image = Image.fromarray(annotated_img)
        
        return {
            'fire_detected': fire_detected,
            'smoke_detected': False,  # Heuristic method doesn't detect smoke
            'detections': detections,
            'confidence': fire_percentage / 100,
            'annotated_image': annotated_image
        }
    
    def image_to_base64(self, image):
        """Convert PIL Image to base64 string"""
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str


# Global instance
fire_detector = FireDetectionService()
