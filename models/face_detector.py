import cv2
from ultralytics import YOLO
import torch
from utils.config import Config
import os

class FaceDetector:
    def __init__(self):
        # Check GPU availability
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        print(f"🔄 Loading YOLOv8 Face Detection Model...")
        print(f"   Device: {self.device}")
        print(f"   (First time may take 1-2 minutes for download)")
        
        # Load YOLOv8 face detection model
        # YOLO automatically downloads if not present
        self.model = YOLO(Config.FACE_DETECTION_MODEL)
        self.model.to(self.device)
        
        print(f"✅ Model loaded successfully!")
    
    def detect_faces(self, frame):
        """
        Detect faces in frame
        Returns: list of face bounding boxes (x1, y1, x2, y2, confidence)
        """
        results = self.model(frame, conf=Config.CONFIDENCE_THRESHOLD, device=self.device, verbose=False)
        
        faces = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                conf = box.conf[0].item()
                faces.append({
                    'bbox': (x1, y1, x2, y2),
                    'confidence': conf
                })
        
        return faces