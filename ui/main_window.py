import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSlider, QProgressBar, QFileDialog, QComboBox, QSpinBox,
    QTabWidget, QFrame, QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QImage, QFont, QColor, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
import cv2
from processors.image_processor import ImageProcessor
from processors.video_processor import VideoProcessor
from utils.config import Config


# ---------------------------------------------------------------------------
#  THEME / STYLESHEET  —  "Aurora Glass" premium dark theme
# ---------------------------------------------------------------------------
APP_STYLESHEET = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0f1117, stop:0.5 #141821, stop:1 #0f1117);
}

QWidget {
    color: #e6e9f0;
    font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', sans-serif;
    font-size: 13px;
}

/* ---------- Title ---------- */
#AppTitle {
    color: #ffffff;
    letter-spacing: 1px;
}

#AppSubtitle {
    color: #7c8aa5;
    font-size: 12px;
    font-weight: 400;
}

/* ---------- Tabs ---------- */
QTabWidget::pane {
    border: 1px solid #262b38;
    border-radius: 14px;
    background: #161a23;
    top: -1px;
    padding: 6px;
}

QTabBar::tab {
    background: transparent;
    color: #8a93a8;
    padding: 10px 26px;
    margin-right: 6px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 13px;
}

QTabBar::tab:hover {
    background: #1f2430;
    color: #c7cfe0;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6e5bf2, stop:1 #8a5bf2);
    color: #ffffff;
}

/* ---------- Cards / Frames ---------- */
#Card {
    background: #181c26;
    border: 1px solid #262b38;
    border-radius: 16px;
}

#SectionLabel {
    color: #9aa3b8;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ---------- File path label ---------- */
#PathLabel {
    background: #11141c;
    border: 1px solid #262b38;
    border-radius: 10px;
    padding: 9px 14px;
    color: #c7cfe0;
}

/* ---------- Preview ---------- */
#PreviewFrame {
    background: #0d1016;
    border: 1px dashed #323849;
    border-radius: 14px;
}

/* ---------- Buttons ---------- */
QPushButton {
    border-radius: 10px;
    padding: 10px 22px;
    font-weight: 600;
    font-size: 13px;
}

#SelectButton {
    background: #232838;
    color: #d6dcea;
    border: 1px solid #323849;
}
#SelectButton:hover {
    background: #2b3144;
    border: 1px solid #6e5bf2;
    color: #ffffff;
}
#SelectButton:pressed {
    background: #1f2430;
}

#ProcessButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6e5bf2, stop:1 #c45bf2);
    color: #ffffff;
    font-size: 14px;
    padding: 13px 26px;
}
#ProcessButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7d6bff, stop:1 #d36bff);
}
#ProcessButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5c4bd1, stop:1 #a84bd1);
}
#ProcessButton:disabled {
    background: #2a2e3a;
    color: #6a7186;
}

/* ---------- Slider ---------- */
QSlider::groove:horizontal {
    height: 6px;
    background: #262b38;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6e5bf2, stop:1 #c45bf2);
    border-radius: 3px;
}
QSlider::handle:horizontal {
    width: 18px;
    height: 18px;
    margin: -7px 0;
    border-radius: 9px;
    background: #ffffff;
    border: 3px solid #6e5bf2;
}
QSlider::handle:horizontal:hover {
    border: 3px solid #c45bf2;
}

/* ---------- Value badge ---------- */
#ValueBadge {
    background: #232838;
    border: 1px solid #323849;
    border-radius: 8px;
    padding: 4px 10px;
    color: #c7cfe0;
    font-weight: 700;
    min-width: 28px;
}

/* ---------- Progress bar ---------- */
QProgressBar {
    background: #11141c;
    border: 1px solid #262b38;
    border-radius: 8px;
    height: 16px;
    text-align: center;
    color: #c7cfe0;
    font-weight: 600;
    font-size: 11px;
}
QProgressBar::chunk {
    border-radius: 8px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6e5bf2, stop:0.5 #a05bf2, stop:1 #c45bf2);
}

/* ---------- Status label ---------- */
#StatusLabel {
    font-weight: 600;
    padding: 4px 2px;
}

/* ---------- Info label ---------- */
#InfoLabel {
    background: #11141c;
    border: 1px solid #262b38;
    border-radius: 10px;
    padding: 9px 14px;
    color: #9aa3b8;
}

QScrollBar:vertical {
    background: #11141c;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #323849;
    border-radius: 5px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover {
    background: #6e5bf2;
}
"""


def make_shadow(blur=24, color="#000000", alpha=160, dx=0, dy=6):
    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(blur)
    c = QColor(color)
    c.setAlpha(alpha)
    effect.setColor(c)
    effect.setOffset(dx, dy)
    return effect


class ProcessingThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, file_path, output_path, blur_intensity, is_video):
        super().__init__()
        self.file_path = file_path
        self.output_path = output_path
        self.blur_intensity = blur_intensity
        self.is_video = is_video

    def run(self):
        try:
            if self.is_video:
                processor = VideoProcessor(progress_callback=self.progress.emit)
                processor.process_video(self.file_path, self.output_path, self.blur_intensity)
            else:
                processor = ImageProcessor()
                image = processor.process_image(self.file_path, self.blur_intensity)
                processor.save_image(image, self.output_path)
                self.progress.emit(100)

            self.finished.emit(self.output_path)

        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FaceBlur Pro — Professional Privacy Suite")
        self.setGeometry(100, 100, 1080, 760)
        self.setMinimumSize(900, 640)

        self.image_processor = ImageProcessor()
        self.video_processor = None
        self.processing_thread = None

        self.setStyleSheet(APP_STYLESHEET)
        self.init_ui()

    # ------------------------------------------------------------------
    def init_ui(self):
        """Initialize UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(18)

        # ---- Header ----
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        logo = QLabel("🛡️")
        logo.setStyleSheet("font-size: 30px;")
        header_layout.addWidget(logo)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title = QLabel("FaceBlur Pro")
        title.setObjectName("AppTitle")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title_box.addWidget(title)

        subtitle = QLabel("Smart face anonymization for images & video")
        subtitle.setObjectName("AppSubtitle")
        title_box.addWidget(subtitle)

        header_layout.addLayout(title_box)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # ---- Tabs ----
        tabs = QTabWidget()

        image_tab = self.create_image_tab()
        tabs.addTab(image_tab, "🖼  Image")

        video_tab = self.create_video_tab()
        tabs.addTab(video_tab, "🎬  Video")

        main_layout.addWidget(tabs)

        central_widget.setLayout(main_layout)

    # ------------------------------------------------------------------
    def _section_label(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("SectionLabel")
        return lbl

    def _card(self):
        frame = QFrame()
        frame.setObjectName("Card")
        frame.setGraphicsEffect(make_shadow(blur=30, alpha=110))
        return frame

    # ------------------------------------------------------------------
    def create_image_tab(self):
        """Create image processing tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(10, 14, 10, 10)

        # File selection card
        file_card = self._card()
        file_card_layout = QVBoxLayout(file_card)
        file_card_layout.setContentsMargins(18, 16, 18, 16)
        file_card_layout.setSpacing(8)
        file_card_layout.addWidget(self._section_label("SOURCE IMAGE"))

        file_layout = QHBoxLayout()
        self.image_path_label = QLabel("No image selected")
        self.image_path_label.setObjectName("PathLabel")
        self.image_path_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        image_btn = QPushButton("📁  Select Image")
        image_btn.setObjectName("SelectButton")
        image_btn.setCursor(Qt.PointingHandCursor)
        image_btn.clicked.connect(self.select_image)
        file_layout.addWidget(self.image_path_label)
        file_layout.addWidget(image_btn)
        file_card_layout.addLayout(file_layout)
        layout.addWidget(file_card)

        # Preview card
        preview_card = self._card()
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(18, 16, 18, 16)
        preview_layout.setSpacing(8)
        preview_layout.addWidget(self._section_label("PREVIEW"))

        self.image_preview = QLabel("Drop or select an image to preview")
        self.image_preview.setObjectName("PreviewFrame")
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setMinimumHeight(300)
        self.image_preview.setStyleSheet(self.image_preview.styleSheet() + "color:#5b6275;")
        preview_layout.addWidget(self.image_preview)
        layout.addWidget(preview_card, stretch=1)

        # Controls card
        controls_card = self._card()
        controls_layout = QVBoxLayout(controls_card)
        controls_layout.setContentsMargins(18, 16, 18, 16)
        controls_layout.setSpacing(10)
        controls_layout.addWidget(self._section_label("BLUR INTENSITY"))

        blur_layout = QHBoxLayout()
        self.image_blur_slider = QSlider(Qt.Horizontal)
        self.image_blur_slider.setRange(5, 100)
        self.image_blur_slider.setValue(Config.BLUR_INTENSITY)
        self.image_blur_slider.setCursor(Qt.PointingHandCursor)
        self.image_blur_value = QLabel(str(Config.BLUR_INTENSITY))
        self.image_blur_value.setObjectName("ValueBadge")
        self.image_blur_value.setAlignment(Qt.AlignCenter)
        self.image_blur_slider.valueChanged.connect(
            lambda: self.image_blur_value.setText(str(self.image_blur_slider.value()))
        )
        blur_layout.addWidget(self.image_blur_slider)
        blur_layout.addWidget(self.image_blur_value)
        controls_layout.addLayout(blur_layout)

        process_btn = QPushButton("✨  Process Image")
        process_btn.setObjectName("ProcessButton")
        process_btn.setCursor(Qt.PointingHandCursor)
        process_btn.clicked.connect(self.process_image)
        controls_layout.addWidget(process_btn)

        self.image_progress = QProgressBar()
        self.image_progress.setTextVisible(True)
        controls_layout.addWidget(self.image_progress)

        self.image_status = QLabel("")
        self.image_status.setObjectName("StatusLabel")
        controls_layout.addWidget(self.image_status)

        layout.addWidget(controls_card)

        widget.setLayout(layout)
        return widget

    # ------------------------------------------------------------------
    def create_video_tab(self):
        """Create video processing tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(10, 14, 10, 10)

        # File selection card
        file_card = self._card()
        file_card_layout = QVBoxLayout(file_card)
        file_card_layout.setContentsMargins(18, 16, 18, 16)
        file_card_layout.setSpacing(8)
        file_card_layout.addWidget(self._section_label("SOURCE VIDEO"))

        file_layout = QHBoxLayout()
        self.video_path_label = QLabel("No video selected")
        self.video_path_label.setObjectName("PathLabel")
        self.video_path_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        video_btn = QPushButton("📁  Select Video")
        video_btn.setObjectName("SelectButton")
        video_btn.setCursor(Qt.PointingHandCursor)
        video_btn.clicked.connect(self.select_video)
        file_layout.addWidget(self.video_path_label)
        file_layout.addWidget(video_btn)
        file_card_layout.addLayout(file_layout)
        layout.addWidget(file_card)

        # Video info card
        info_card = self._card()
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(18, 16, 18, 16)
        info_layout.setSpacing(8)
        info_layout.addWidget(self._section_label("VIDEO INFO"))
        self.video_info = QLabel("—  Select a video to see its details")
        self.video_info.setObjectName("InfoLabel")
        info_layout.addWidget(self.video_info)
        layout.addWidget(info_card)

        layout.addStretch()

        # Controls card
        controls_card = self._card()
        controls_layout = QVBoxLayout(controls_card)
        controls_layout.setContentsMargins(18, 16, 18, 16)
        controls_layout.setSpacing(10)
        controls_layout.addWidget(self._section_label("BLUR INTENSITY"))

        blur_layout = QHBoxLayout()
        self.video_blur_slider = QSlider(Qt.Horizontal)
        self.video_blur_slider.setRange(5, 100)
        self.video_blur_slider.setValue(Config.BLUR_INTENSITY)
        self.video_blur_slider.setCursor(Qt.PointingHandCursor)
        self.video_blur_value = QLabel(str(Config.BLUR_INTENSITY))
        self.video_blur_value.setObjectName("ValueBadge")
        self.video_blur_value.setAlignment(Qt.AlignCenter)
        self.video_blur_slider.valueChanged.connect(
            lambda: self.video_blur_value.setText(str(self.video_blur_slider.value()))
        )
        blur_layout.addWidget(self.video_blur_slider)
        blur_layout.addWidget(self.video_blur_value)
        controls_layout.addLayout(blur_layout)

        process_btn = QPushButton("✨  Process Video")
        process_btn.setObjectName("ProcessButton")
        process_btn.setCursor(Qt.PointingHandCursor)
        process_btn.clicked.connect(self.process_video)
        controls_layout.addWidget(process_btn)

        self.video_progress = QProgressBar()
        self.video_progress.setTextVisible(True)
        controls_layout.addWidget(self.video_progress)

        self.video_status = QLabel("")
        self.video_status.setObjectName("StatusLabel")
        controls_layout.addWidget(self.video_status)

        layout.addWidget(controls_card)

        widget.setLayout(layout)
        return widget

    # ------------------------------------------------------------------
    def _fade_in(self, widget):
        """Small fade-in animation used after a status update for a nicer feel."""
        effect = QGraphicsDropShadowEffect()
        widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"blurRadius")
        anim.setDuration(280)
        anim.setStartValue(0)
        anim.setEndValue(0)
        # Keep a reference so it isn't garbage collected mid-animation
        widget._anim_ref = anim
        anim.start()

    # ------------------------------------------------------------------
    def select_image(self):
        """Select image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Image Files (*.jpg *.jpeg *.png *.bmp);;All Files (*)"
        )

        if file_path:
            self.image_path_label.setText(file_path)
            # Show preview
            pixmap = QPixmap(file_path)
            scaled = pixmap.scaledToHeight(300, Qt.SmoothTransformation)
            self.image_preview.setPixmap(scaled)

    def select_video(self):
        """Select video file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video", "",
            "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*)"
        )

        if file_path:
            self.video_path_label.setText(file_path)
            # Get video info
            cap = cv2.VideoCapture(file_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()

            duration = total_frames / fps
            self.video_info.setText(
                f"🎞  {width}x{height}   •   {fps:.0f} fps   •   {int(duration)}s   •   {total_frames} frames"
            )

    def process_image(self):
        """Process selected image - Auto save to Desktop"""
        if self.image_path_label.text() == "No image selected":
            self.image_status.setText("❌  Please select an image first")
            self.image_status.setStyleSheet("color:#ff6b6b;")
            return

        # Auto filename generate karo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"blurred_image_{timestamp}.png"

        # Desktop path
        desktop = os.path.expanduser("~/Desktop")
        output_path = os.path.join(desktop, filename)

        blur_intensity = self.image_blur_slider.value()
        self.image_status.setText(f"⏳  Processing... ({filename})")
        self.image_status.setStyleSheet("color:#c4a3ff;")
        self.image_progress.setValue(0)

        self.processing_thread = ProcessingThread(
            self.image_path_label.text(),
            output_path,
            blur_intensity,
            False
        )
        self.processing_thread.finished.connect(self.on_image_finished)
        self.processing_thread.error.connect(self.on_image_error)
        self.processing_thread.progress.connect(self.image_progress.setValue)
        self.processing_thread.start()

    def process_video(self):
        """Process selected video - Auto save to Desktop"""
        if self.video_path_label.text() == "No video selected":
            self.video_status.setText("❌  Please select a video first")
            self.video_status.setStyleSheet("color:#ff6b6b;")
            return

        # Auto filename generate karo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"blurred_video_{timestamp}.mp4"

        # Desktop path
        desktop = os.path.expanduser("~/Desktop")
        output_path = os.path.join(desktop, filename)

        blur_intensity = self.video_blur_slider.value()
        self.video_status.setText(f"⏳  Processing... ({filename})")
        self.video_status.setStyleSheet("color:#c4a3ff;")
        self.video_progress.setValue(0)

        self.processing_thread = ProcessingThread(
            self.video_path_label.text(),
            output_path,
            blur_intensity,
            True
        )
        self.processing_thread.finished.connect(self.on_video_finished)
        self.processing_thread.error.connect(self.on_video_error)
        self.processing_thread.progress.connect(self.video_progress.setValue)
        self.processing_thread.start()

    def on_image_finished(self, output_path):
        """Image processing finished"""
        self.image_status.setText(f"✅  Image saved: {output_path}")
        self.image_status.setStyleSheet("color:#5be38a;")
        self.image_progress.setValue(100)

    def on_image_error(self, error):
        """Image processing error"""
        self.image_status.setText(f"❌  Error: {error}")
        self.image_status.setStyleSheet("color:#ff6b6b;")

    def on_video_finished(self, output_path):
        """Video processing finished"""
        self.video_status.setText(f"✅  Video saved: {output_path}")
        self.video_status.setStyleSheet("color:#5be38a;")
        self.video_progress.setValue(100)

    def on_video_error(self, error):
        """Video processing error"""
        self.video_status.setText(f"❌  Error: {error}")
        self.video_status.setStyleSheet("color:#ff6b6b;")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())