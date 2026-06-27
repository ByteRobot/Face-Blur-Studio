import cv2
import numpy as np
from models.face_detector import FaceDetector
from processors.face_tracker import FaceTracker
from utils.config import Config
import os
import subprocess
import tempfile

class VideoProcessor:
    def __init__(self, progress_callback=None):
        self.detector = FaceDetector()
        self.tracker = FaceTracker()
        self.progress_callback = progress_callback
    
    def process_video(self, input_path, output_path, blur_intensity=Config.BLUR_INTENSITY):
        """
        Process video and blur all faces with tracking
        Audio preserve hota hai
        """
        # Temporary files
        temp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name
        audio_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False).name
        
        try:
            # Step 1: Extract audio
            print("🔊 Extracting audio...")
            audio_extracted = self._extract_audio(input_path, audio_file)
            
            # Step 2: Process video (blur faces)
            print("🎬 Processing video frames...")
            self._blur_video(input_path, temp_video, blur_intensity)
            
            # Step 3: Merge audio + video
            print("🔗 Merging audio with video...")
            if audio_extracted and os.path.getsize(audio_file) > 0:
                self._merge_audio_video(temp_video, audio_file, output_path)
            else:
                print("⚠️ Audio not found, saving video without audio...")
                import shutil
                shutil.copy(temp_video, output_path)
            
            print("✅ Video processing complete!")
            return output_path
        
        except Exception as e:
            print(f"❌ Error: {e}")
            raise
        
        finally:
            # Cleanup temp files
            if os.path.exists(temp_video):
                try:
                    os.remove(temp_video)
                except:
                    pass
            if os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                except:
                    pass
    
    def _extract_audio(self, input_path, audio_output):
        """Extract audio from video using FFmpeg"""
        cmd = [
            'ffmpeg', '-i', input_path,
            '-q:a', '9',
            '-y',
            audio_output
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if os.path.exists(audio_output) and os.path.getsize(audio_output) > 0:
                print(f"   ✅ Audio extracted successfully")
                return True
            else:
                print(f"   ⚠️ Audio extraction failed")
                return False
        except subprocess.TimeoutExpired:
            print("   ⚠️ Audio extraction timeout")
            return False
        except Exception as e:
            print(f"   ⚠️ Audio extraction error: {e}")
            return False
    
    def _blur_video(self, input_path, output_path, blur_intensity):
        """Blur faces in video"""
        cap = cv2.VideoCapture(input_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {input_path}")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"   Resolution: {width}x{height} | FPS: {fps} | Frames: {total_frames}")
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            raise ValueError(f"Cannot create video writer for: {output_path}")
        
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Detect faces
            detections = self.detector.detect_faces(frame)
            
            # Track faces
            tracked_faces = self.tracker.update(detections)
            
            # Blur all tracked faces
            for face_id, face_data in tracked_faces.items():
                x1, y1, x2, y2 = face_data['bbox']
                
                # Ensure coordinates are within frame
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(width, x2), min(height, y2)
                
                if x2 > x1 and y2 > y1:
                    # Extract and blur
                    face_region = frame[y1:y2, x1:x2]
                    blurred_face = cv2.blur(face_region, (blur_intensity, blur_intensity))
                    frame[y1:y2, x1:x2] = blurred_face
            
            # Write frame
            out.write(frame)
            
            frame_count += 1
            
            # Progress callback
            if self.progress_callback:
                progress = (frame_count / total_frames) * 100
                self.progress_callback(int(progress))
        
        cap.release()
        out.release()
        print(f"   ✅ Video blurred: {frame_count} frames processed")
    
    def _merge_audio_video(self, video_path, audio_path, output_path):
        """Merge audio with video using FFmpeg"""
        cmd = [
            'ffmpeg', '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest',
            '-y',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print(f"   ✅ Audio merged successfully")
            else:
                print(f"   ⚠️ Merge completed with warnings")
        except subprocess.TimeoutExpired:
            print(f"   ⚠️ Merge timeout")
        except Exception as e:
            print(f"   ⚠️ Merge error: {e}")