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

Tip: Turn on “Show Debug Boxes” to visualize detected areas during preview.

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

---

## 🚀 Quick Start
```bash
python main.py
```
1. Drag & drop a file or click “Browse Files”
2. Set Confidence and Detection Range
3. Enable “Group Photo Mode” for wide shots
4. Click “Start Blur”
5. Use “Open Output Folder” to view results

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
├── main.py                 # GUI
├── face_blur_worker.py     # Processing engine (detectors, blur, video/audio)
├── requirements.txt        # Dependencies
└── README.md               # This file
```

---

## 📦 Build as Executable (PyInstaller)
Create a portable app:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --name "FaceBlurStudioPro" --windowed main.py
```

The executable will be in the `dist/` folder. Ensure FFmpeg is installed system-wide for audio merging.

---

## 🧰 Troubleshooting

- Faces not detected in wide photos:
  - Lower confidence to 25–35%
  - Switch to Full Range
  - Enable Group Photo Mode
- Video has no audio:
  - Install FFmpeg and ensure `ffmpeg -version` works
- PNG transparency lost:
  - Save to `.png` (the app does this automatically when input is PNG)
- App not launching:
  - Use Python 3.8+ and reinstall packages: `pip install -r requirements.txt`

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