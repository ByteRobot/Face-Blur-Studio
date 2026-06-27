# Configuration settings

class Config:
    # Model settings
    FACE_DETECTION_MODEL = "yolov8n.pt"
    CONFIDENCE_THRESHOLD = 0.5
    
    # Video settings
    MAX_RESOLUTION = (1920, 1080)
    TARGET_FPS = 30
    
    # Blur settings
    BLUR_INTENSITY = 25
    BLUR_INTENSITY_MIN = 5
    BLUR_INTENSITY_MAX = 100  # ← Increased from 50 to 100
    
    # UI settings
    PREVIEW_WIDTH = 640
    PREVIEW_HEIGHT = 480
    
    # Supported formats
    IMAGE_FORMATS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    VIDEO_FORMATS = ('.mp4', '.avi', '.mov', '.mkv', '.flv')