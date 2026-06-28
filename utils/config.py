import sys
import os

def resource_path(relative_path):
    """PyInstaller .exe ke andar bhi sahi path dega"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Config:
    # Model settings
    FACE_DETECTION_MODEL = resource_path(os.path.join("models", "yolov8n.pt"))
    CONFIDENCE_THRESHOLD = 0.5
    
    # Video settings
    MAX_RESOLUTION = (1920, 1080)
    TARGET_FPS = 30
    
    # Blur settings
    BLUR_INTENSITY = 25
    BLUR_INTENSITY_MIN = 5
    BLUR_INTENSITY_MAX = 100
    
    # UI settings
    PREVIEW_WIDTH = 640
    PREVIEW_HEIGHT = 480
    
    # Supported formats
    IMAGE_FORMATS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    VIDEO_FORMATS = ('.mp4', '.avi', '.mov', '.mkv', '.flv')
