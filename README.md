# ✨ Face Blur Studio Pro ✨
Professional, elegant, and user-friendly desktop app for automated face detection and blurring in images and videos. Built with Python, OpenCV, MediaPipe, and PyQt5.

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-00D4FF?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Version-1.0.0-8A2BE2?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/MediaPipe-Enabled-FF6F00?style=for-the-badge&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/FFmpeg-Audio%20Preservation-000000?style=for-the-badge&logo=ffmpeg&logoColor=white" />
</p>

---

## 🌟 Highlights
- Ultra-clean, dark-themed GUI with drag-and-drop
- Multi-face detection (unlimited faces per frame)
- Triple-layer Gaussian blur for complete anonymization
- Real-time preview and progress tracking
- Preserves audio in videos (FFmpeg)
- Group Photo Mode for wide shots and small/distant faces
- Cross-platform: Windows, macOS, Linux

---

## 📚 Table of Contents
- [Overview](#-overview)
- [Screenshots](#-screenshots)
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Best Settings](#-best-settings)
- [Supported Formats](#-supported-formats)
- [Performance](#-performance)
- [Architecture](#-architecture)
- [Build as Executable](#-build-as-executable)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

---

## 🔎 Overview
Face Blur Studio Pro helps creators, professionals, and organizations protect privacy by detecting and blurring faces in photos and videos with precision and speed. Perfect for social media, journalism, research datasets, and GDPR-compliant workflows.

---

## 🖼 Screenshots
- Drag-and-drop file picker
- Live preview with optional debug boxes
- Real-time progress with status messages

Tip: Turn on "Show Debug Boxes" to visualize detected areas during preview.

---

## ✅ Features
- Multi-face detection and blurring
- Dual-pass MediaPipe + Haar fallback (Group Photo Mode)
- Adaptive blur kernel (40% of face size)
- Extended padding (30% horizontal, 40% vertical)
- Preserves PNG transparency and video audio tracks
- Responsive PyQt5 UI with tooltips and progress
- Error handling, cancellation, and temp cleanup

---

## 🛠 Installation

### 1) Clone the repository
```bash
git clone https://github.com/Al-Baddar/face-blur-studio-pro.git
cd face-blur-studio-pro
```

### 2) Install Python dependencies
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install PyQt5 opencv-python mediapipe numpy
```

### 3) Install FFmpeg (optional, for audio preservation)
- Windows: `winget install ffmpeg`
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

### 4) Copy Haar Cascade file (required for Group Photo Mode)
Extract the Haar Cascade XML file from your OpenCV installation:
```bash
python -c "import cv2, shutil; shutil.copy(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml', '.')"
```

This will copy `haarcascade_frontalface_default.xml` to your project directory.

---

## 🚀 Quick Start
```bash
python main.py
```
1. Drag & drop a file or click "Browse Files"
2. Set Confidence and Detection Range
3. Enable "Group Photo Mode" for wide shots
4. Click "Start Blur"
5. Use "Open Output Folder" to view results

---

## 🧭 Usage

- Confidence: Detection threshold (lower = more faces, higher = fewer false positives)
- Detection Range:
  - Short Range (0–2m)
  - Full Range (2–5m) — best for group photos
- Group Photo Mode:
  - Runs dual-pass MediaPipe + Haar fallback
  - Deduplicates and pads face boxes
  - Slightly slower, more accurate for many faces
- Debug Boxes:
  - Visual rectangles drawn over detected faces in preview

---

## 🎯 Best Settings

Wide group photos, small/distant faces:
- Confidence: 25–35%
- Detection Range: Full Range (2–5m)
- Enable: Group Photo Mode
- Optional: Show Debug Boxes

Close-up portraits:
- Confidence: 50–70%
- Detection Range: Short Range (0–2m)
- Group Photo Mode: Off (faster)

---

## 📦 Supported Formats

Images:
- JPG, JPEG, PNG, BMP, WebP, TIFF, TIF
- PNG transparency preserved

Videos:
- MP4, MOV, AVI, MKV, WebM, FLV, WMV
- Audio preserved and merged (AAC 192 kbps) via FFmpeg

---

## ⚡ Performance

| Media Type | Resolution | Speed (approx) | Faces |
|------------|------------|----------------|-------|
| Image      | 1920×1080  | 1–3 sec        | ≤ 50  |
| Video      | 1080p @30  | 0.5–1× realtime| Unlimited |
| Video      | 4K @30     | 0.3–0.7×       | Unlimited |

Note: Performance depends on hardware and settings.

---

## 🧱 Architecture

- Frontend: PyQt5 (dark UI, drag-and-drop, progress)
- Vision: OpenCV + MediaPipe
- Pattern: MVC + QThread + signals/slots
- Engine:
  - Dual MediaPipe detectors (short/full range)
  - Haar cascade fallback for tiny faces
  - Box padding + deduplication
  - Triple Gaussian blur
```
face-blur-studio-pro/
├── main.py                              # GUI
├── face_blur_worker.py                  # Processing engine
├── haarcascade_frontalface_default.xml  # Haar cascade data
├── requirements.txt                     # Dependencies
└── README.md                            # This file
```

---

## 📦 Build as Executable (PyInstaller)

Create a standalone executable that works without Python installation:

### Step 1: Install PyInstaller
```bash
pip install pyinstaller
```

### Step 2: Prepare Haar Cascade File
Ensure `haarcascade_frontalface_default.xml` is in your project root directory (see Installation step 4 above).

### Step 3: Build the Executable

**For Windows:**
```bash
pyinstaller --onefile --windowed --name FaceBlurStudioPro ^
--hidden-import=mediapipe ^
--hidden-import=cv2 ^
--hidden-import=face_blur_worker ^
--collect-data=mediapipe ^
--collect-submodules=mediapipe ^
--add-data "haarcascade_frontalface_default.xml;." ^
main.py
```

**For macOS/Linux:**
```bash
pyinstaller --onefile --windowed --name FaceBlurStudioPro \
--hidden-import=mediapipe \
--hidden-import=cv2 \
--hidden-import=face_blur_worker \
--collect-data=mediapipe \
--collect-submodules=mediapipe \
--add-data "haarcascade_frontalface_default.xml:." \
main.py
```

### Step 4: Locate Your Executable
The executable will be in the `dist/` folder:
```
dist/
└── FaceBlurStudioPro.exe  (Windows)
    or
    FaceBlurStudioPro        (macOS/Linux)
```

### Important Notes:
- **FFmpeg**: Must be installed system-wide for video audio merging. The executable will use the system's FFmpeg installation.
- **First Run**: May take 10-15 seconds to launch due to MediaPipe initialization.
- **Antivirus**: Some antivirus software may flag PyInstaller executables. Add an exception if needed.
- **File Size**: The executable will be ~150-250 MB due to bundled dependencies (OpenCV, MediaPipe, PyQt5).

### Debug Build (if issues occur):
For troubleshooting, create a console version that shows error messages:
```bash
pyinstaller --onefile --console --name FaceBlurStudioPro-Debug ^
--hidden-import=mediapipe ^
--hidden-import=cv2 ^
--hidden-import=face_blur_worker ^
--collect-data=mediapipe ^
--collect-submodules=mediapipe ^
--add-data "haarcascade_frontalface_default.xml;." ^
main.py
```

---

## 🧰 Troubleshooting

- **Faces not detected in wide photos:**
  - Lower confidence to 25–35%
  - Switch to Full Range
  - Enable Group Photo Mode

- **Video has no audio:**
  - Install FFmpeg and ensure `ffmpeg -version` works in terminal

- **PNG transparency lost:**
  - Save to `.png` (the app does this automatically when input is PNG)

- **App not launching:**
  - Use Python 3.8+ and reinstall packages: `pip install -r requirements.txt`
  - Ensure `haarcascade_frontalface_default.xml` is in the project directory

- **Executable crashes on Group Photo Mode:**
  - Verify that `haarcascade_frontalface_default.xml` was bundled correctly
  - Try the debug build to see error messages

- **"Failed to execute script" error (PyInstaller):**
  - Rebuild with `--console` flag to see detailed error messages
  - Check that all hidden imports are included in the build command

---

## 🗺 Roadmap
- Batch processing queue
- Custom effects: mosaic, pixelation, black bars
- Manual selection mode
- GPU acceleration (CUDA/Metal)
- CLI version
- Plugin system
- Export presets

---

## 📜 License
- Application: MIT (recommended; update this section with your chosen license)
- MediaPipe: Apache 2.0 (Google)
- OpenCV: Apache 2.0
- PyQt5: GPLv3 / Commercial

---

## 🙏 Acknowledgements
- Google MediaPipe for robust face detection
- OpenCV for powerful image/video processing
- FFmpeg for reliable audio handling

---

## 👤 Maintainer
- GitHub: [Al-Baddar](https://github.com/Al-Baddar)

If you find this useful, please ⭐ star the repo and consider contributing via issues or pull requests!

---
