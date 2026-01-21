"""
Face Blur Worker - Enhanced Processing Engine
- Dual-pass MediaPipe detection
- Haar cascade fallback for small/distant faces
- Box padding and deduplication
- EXE-friendly resource loading
"""

import cv2
import mediapipe as mp
import numpy as np
import os
import sys
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal


def _resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller EXE."""
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller EXE mode
        return os.path.join(sys._MEIPASS, relative_path)
    # Normal Python mode
    return os.path.join(os.path.abspath("."), relative_path)


def _ensure_odd(n: int) -> int:
    return n + 1 if n % 2 == 0 else n


def _pad_box(x, y, w, h, img_w, img_h, pad_x=0.30, pad_y=0.40):
    px = int(w * pad_x)
    py = int(h * pad_y)
    x2 = min(img_w, x + w + px)
    y2 = min(img_h, y + h + py)
    x1 = max(0, x - px)
    y1 = max(0, y - py)
    return x1, y1, x2 - x1, y2 - y1


def _iou(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ax2, ay2 = ax + aw, ay + ah
    bx2, by2 = bx + bw, by + bh
    inter_w = max(0, min(ax2, bx2) - max(ax, bx))
    inter_h = max(0, min(ay2, by2) - max(ay, by))
    inter = inter_w * inter_h
    union = aw * ah + bw * bh - inter
    return inter / union if union > 0 else 0.0


def _dedup_boxes(boxes, iou_thresh=0.35):
    kept = []
    for b in boxes:
        if all(_iou(b, k) < iou_thresh for k in kept):
            kept.append(b)
    return kept


class FaceBlurrer:
    """Core face detection and blur logic with dual-pass + fallback."""

    def __init__(self, confidence=0.5, model_selection=0, group_mode=False):
        self.group_mode = group_mode
        self.mp_face_detection = mp.solutions.face_detection
        # Primary detector (UI-selected)
        self.det_primary = self.mp_face_detection.FaceDetection(
            min_detection_confidence=confidence,
            model_selection=model_selection
        )
        # Secondary (dual-pass) for group mode
        self.det_secondary = None
        if group_mode:
            other_model = 1 - int(model_selection)
            self.det_secondary = self.mp_face_detection.FaceDetection(
                min_detection_confidence=max(0.2, confidence - 0.15),
                model_selection=other_model
            )
        # Haar fallback for tiny faces (EXE-safe loading)
        self.haar = None
        if group_mode:
            try:
                # Try loading from bundled resource first
                haar_path = _resource_path("haarcascade_frontalface_default.xml")
                self.haar = cv2.CascadeClassifier(haar_path)
                
                # Verify it loaded correctly
                if self.haar.empty():
                    # Fallback to OpenCV's built-in path
                    haar_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                    self.haar = cv2.CascadeClassifier(haar_path)
                    
                    # Final check
                    if self.haar.empty():
                        self.haar = None
            except Exception:
                # If all else fails, disable Haar cascade
                self.haar = None

    def _collect_mediapipe_boxes(self, image):
        h, w = image.shape[:2]
        boxes = []
        for detector in [self.det_primary, self.det_secondary]:
            if detector is None:
                continue
            results = detector.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            if not results.detections:
                continue
            for d in results.detections:
                rb = d.location_data.relative_bounding_box
                x = int(rb.xmin * w)
                y = int(rb.ymin * h)
                bw = int(rb.width * w)
                bh = int(rb.height * h)
                # Skip invalid
                if bw <= 0 or bh <= 0:
                    continue
                boxes.append((x, y, bw, bh))
        return boxes

    def _collect_haar_boxes(self, image):
        if self.haar is None:
            return []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ih, iw = gray.shape[:2]
        # Dynamic minimum size ~2% of smallest dimension
        min_side = max(20, int(min(ih, iw) * 0.02))
        faces = self.haar.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(min_side, min_side)
        )
        return [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in faces]

    def detect_boxes(self, image):
        """Return padded, deduplicated face boxes."""
        ih, iw = image.shape[:2]
        boxes = self._collect_mediapipe_boxes(image)
        if self.group_mode:
            boxes += self._collect_haar_boxes(image)
        # Pad and clip
        padded = [_pad_box(x, y, w, h, iw, ih) for (x, y, w, h) in boxes]
        # Deduplicate
        return _dedup_boxes(padded)

    def detect_and_blur_faces(self, image):
        """Apply triple Gaussian blur to every detected box."""
        boxes = self.detect_boxes(image)
        for (x, y, w, h) in boxes:
            face = image[y:y + h, x:x + w]
            if face.size == 0:
                continue
            k = _ensure_odd(max(3, int(0.4 * max(w, h))))
            blurred = cv2.GaussianBlur(face, (k, k), 0)
            blurred = cv2.GaussianBlur(blurred, (k, k), 0)
            blurred = cv2.GaussianBlur(blurred, (k, k), 0)
            image[y:y + h, x:x + w] = blurred
        return image, boxes

    def cleanup(self):
        if self.det_primary:
            self.det_primary.close()
        if self.det_secondary:
            self.det_secondary.close()


class BlurWorker(QThread):
    """Background worker for processing files."""

    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    preview = pyqtSignal(np.ndarray)

    def __init__(self, input_path, output_path, confidence, model_selection, group_mode=False, debug=False):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.confidence = confidence
        self.model_selection = model_selection
        self.group_mode = group_mode
        self.debug = debug
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True

    def run(self):
        try:
            ext = os.path.splitext(self.input_path)[1].lower()
            image_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.tif'}
            video_exts = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv'}
            if ext in image_exts:
                self.process_image()
            elif ext in video_exts:
                self.process_video()
            else:
                self.error.emit(f"Unsupported file format: {ext}")
        except Exception as e:
            self.error.emit(f"Processing error: {str(e)}")

    def process_image(self):
        img = cv2.imread(self.input_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            self.error.emit("Failed to load image")
            return

        self.progress.emit(15)
        blurrer = FaceBlurrer(self.confidence, self.model_selection, self.group_mode)

        has_alpha = (img.ndim == 3 and img.shape[2] == 4)
        if has_alpha:
            alpha = img[:, :, 3]
            bgr = img[:, :, :3]
        else:
            bgr = img

        self.progress.emit(40)
        blurred_bgr, boxes = blurrer.detect_and_blur_faces(bgr.copy())
        self.progress.emit(75)

        if has_alpha:
            final_img = cv2.merge([blurred_bgr, alpha])
        else:
            final_img = blurred_bgr

        # Save
        if self.output_path.lower().endswith('.png'):
            cv2.imwrite(self.output_path, final_img, [cv2.IMWRITE_PNG_COMPRESSION, 0])
        else:
            cv2.imwrite(self.output_path, final_img, [cv2.IMWRITE_JPEG_QUALITY, 100])

        # Preview (with optional debug boxes)
        preview = self.create_preview(final_img, boxes if self.debug else [])
        self.preview.emit(preview)

        blurrer.cleanup()
        self.progress.emit(100)
        self.finished.emit(self.output_path)

    def process_video(self):
        cap = cv2.VideoCapture(self.input_path)
        if not cap.isOpened():
            self.error.emit("Failed to open video")
            return

        fps = int(max(1, cap.get(cv2.CAP_PROP_FPS)))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total = int(max(1, cap.get(cv2.CAP_PROP_FRAME_COUNT)))

        temp_video = os.path.splitext(self.output_path)[0] + "_temp.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))

        blurrer = FaceBlurrer(self.confidence, self.model_selection, self.group_mode)

        sent_preview = False
        frame_idx = 0

        while True:
            if self.is_cancelled:
                break
            ret, frame = cap.read()
            if not ret:
                break
            blurred, boxes = blurrer.detect_and_blur_faces(frame)
            out.write(blurred)

            if not sent_preview:
                preview = self.create_preview(blurred, boxes if self.debug else [])
                self.preview.emit(preview)
                sent_preview = True

            frame_idx += 1
            self.progress.emit(int((frame_idx / total) * 80))

        cap.release()
        out.release()
        blurrer.cleanup()

        if self.is_cancelled:
            self.cleanup_temp_files(temp_video)
            return

        self.progress.emit(90)
        self.merge_audio(temp_video)
        self.progress.emit(100)
        self.finished.emit(self.output_path)

    def merge_audio(self, temp_video):
        try:
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            cmd = [
                'ffmpeg', '-y',
                '-i', temp_video,
                '-i', self.input_path,
                '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '192k',
                '-map', '0:v:0',
                '-map', '1:a:0?',
                '-shortest',
                self.output_path
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            os.remove(temp_video)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback: keep temp video without audio merge
            if os.path.exists(self.output_path):
                try: os.remove(self.output_path)
                except: pass
            os.rename(temp_video, self.output_path)

    def create_preview(self, image, boxes=None, max_w=800):
        h, w = image.shape[:2]
        vis = image.copy()
        # Draw debug boxes on preview only
        if boxes:
            for (x, y, bw, bh) in boxes:
                cv2.rectangle(vis, (x, y), (x + bw, y + bh), (0, 255, 255), 2)
        if w > max_w:
            scale = max_w / w
            vis = cv2.resize(vis, (max_w, int(h * scale)))
        return vis

    def cleanup_temp_files(self, *files):
        for f in files:
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass