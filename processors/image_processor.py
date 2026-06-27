import cv2
import numpy as np
from models.face_detector import FaceDetector
from utils.config import Config

class ImageProcessor:
    def __init__(self):
        self.detector = FaceDetector()
    
    def process_image(self, image_path, blur_intensity=Config.BLUR_INTENSITY):
        """
        Process image and blur all faces
        Returns: processed image
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Cannot read image: {image_path}")
        
        # Detect faces
        faces = self.detector.detect_faces(image)
        
        # Blur faces
        for face in faces:
            x1, y1, x2, y2 = face['bbox']
            
            # Extract face region
            face_region = image[y1:y2, x1:x2]
            
            # Apply blur
            blurred_face = cv2.blur(face_region, (blur_intensity, blur_intensity))
            
            # Replace original with blurred
            image[y1:y2, x1:x2] = blurred_face
        
        return image
    
    def save_image(self, image, output_path):
        """Save processed image"""
        cv2.imwrite(output_path, image)
        return output_path