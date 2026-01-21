"""
Face Blur Studio Pro - Enhanced UI
Adds:
- Group Photo Mode (dual-pass + Haar fallback)
- Debug Boxes (show detected regions in preview)
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QProgressBar, QSlider, QComboBox, QMessageBox,
    QGroupBox, QGridLayout, QCheckBox
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QImage, QFont
import cv2
from face_blur_worker import BlurWorker


class FaceBlurStudioPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.input_path = None
        self.output_path = None
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Face Blur Studio Pro v1.0.0")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet(self.get_dark_theme())

        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)

        title = QLabel("Face Blur Studio Pro")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #00D4FF; padding: 20px;")
        main.addWidget(title)

        main.addWidget(self.create_file_selection_group())
        main.addWidget(self.create_settings_group())
        main.addWidget(self.create_preview_group())

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: 2px solid #555; border-radius: 5px;
                           text-align: center; background-color: #2b2b2b; color: white; }
            QProgressBar::chunk { background-color: #00D4FF; }
        """)
        main.addWidget(self.progress_bar)

        main.addLayout(self.create_control_buttons())

        self.status_label = QLabel("Ready - Drop a file or click Browse")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #888; padding: 10px;")
        main.addWidget(self.status_label)

        self.setAcceptDrops(True)

    def create_file_selection_group(self):
        group = QGroupBox("File Selection")
        layout = QVBoxLayout(group)

        self.drop_label = QLabel("📁 Drag & Drop File Here\nor Click Browse")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("""
            QLabel { border: 3px dashed #555; border-radius: 10px; padding: 40px;
                     font-size: 16px; color: #aaa; background-color: #1e1e1e; }
        """)
        self.drop_label.setMinimumHeight(120)
        layout.addWidget(self.drop_label)

        browse = QPushButton("Browse Files")
        browse.clicked.connect(self.browse_file)
        browse.setStyleSheet(self.button_style())
        layout.addWidget(browse)

        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #00D4FF; padding: 5px;")
        layout.addWidget(self.file_label)

        return group

    def create_settings_group(self):
        group = QGroupBox("Detection Settings")
        grid = QGridLayout(group)

        grid.addWidget(QLabel("Confidence Threshold:"), 0, 0)
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setMinimum(20)
        self.confidence_slider.setMaximum(95)
        self.confidence_slider.setValue(50)
        self.confidence_slider.setTickPosition(QSlider.TicksBelow)
        self.confidence_slider.setTickInterval(5)
        self.confidence_slider.valueChanged.connect(lambda v: self.conf_lbl.setText(f"{v}%"))
        grid.addWidget(self.confidence_slider, 0, 1)

        self.conf_lbl = QLabel("50%")
        self.conf_lbl.setStyleSheet("color: #00D4FF; font-weight: bold;")
        grid.addWidget(self.conf_lbl, 0, 2)

        grid.addWidget(QLabel("Detection Range:"), 1, 0)
        self.range_combo = QComboBox()
        self.range_combo.addItems(["Short Range (0-2m)", "Full Range (2-5m)"])
        self.range_combo.setStyleSheet("QComboBox { background-color: #2b2b2b; color: white; border: 1px solid #555; padding: 5px; }")
        grid.addWidget(self.range_combo, 1, 1, 1, 2)

        # New options
        self.group_mode_cb = QCheckBox("Group Photo Mode (more accurate, slower)")
        self.group_mode_cb.setChecked(True)
        grid.addWidget(self.group_mode_cb, 2, 0, 1, 3)

        self.debug_cb = QCheckBox("Show Debug Boxes in Preview")
        self.debug_cb.setChecked(False)
        grid.addWidget(self.debug_cb, 3, 0, 1, 3)

        return group

    def create_preview_group(self):
        group = QGroupBox("Preview")
        layout = QVBoxLayout(group)
        self.preview_label = QLabel("Preview will appear here")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel { border: 2px solid #555; background-color: #1e1e1e;
                     color: #666; min-height: 300px; }
        """)
        self.preview_label.setScaledContents(False)
        layout.addWidget(self.preview_label)
        return group

    def create_control_buttons(self):
        row = QHBoxLayout()
        self.start_btn = QPushButton("🚀 Start Blur")
        self.start_btn.clicked.connect(self.start_processing)
        self.start_btn.setEnabled(False)
        self.start_btn.setStyleSheet(self.button_style("#00D4FF"))
        self.start_btn.setMinimumHeight(50)
        row.addWidget(self.start_btn)

        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.cancel_processing)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setStyleSheet(self.button_style("#FF4444"))
        self.cancel_btn.setMinimumHeight(50)
        row.addWidget(self.cancel_btn)

        self.open_folder_btn = QPushButton("📂 Open Output Folder")
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.setStyleSheet(self.button_style("#44FF44"))
        self.open_folder_btn.setMinimumHeight(50)
        row.addWidget(self.open_folder_btn)
        return row

    def browse_file(self):
        filt = "Media Files (*.jpg *.jpeg *.png *.bmp *.webp *.tiff *.tif *.mp4 *.mov *.avi *.mkv *.webm *.flv *.wmv)"
        path, _ = QFileDialog.getOpenFileName(self, "Select File", "", filt)
        if path:
            self.load_file(path)

    def load_file(self, path):
        self.input_path = path
        filename = os.path.basename(path)
        self.file_label.setText(f"Selected: {filename}")
        self.drop_label.setText(f"✅ {filename}")
        self.start_btn.setEnabled(True)
        self.status_label.setText("File loaded - Ready to process")

        base, ext = os.path.splitext(path)
        if ext.lower() in {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv'}:
            self.output_path = f"{base}_blurred.mp4"
        else:
            self.output_path = f"{base}_blurred{ext}"

    def start_processing(self):
        if not self.input_path:
            return
        confidence = self.confidence_slider.value() / 100.0
        model_selection = self.range_combo.currentIndex()
        group_mode = self.group_mode_cb.isChecked()
        debug = self.debug_cb.isChecked()

        self.worker = BlurWorker(
            self.input_path, self.output_path, confidence, model_selection,
            group_mode=group_mode, debug=debug
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.processing_finished)
        self.worker.error.connect(self.processing_error)
        self.worker.preview.connect(self.update_preview)

        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Processing...")

        self.worker.start()

    def cancel_processing(self):
        if self.worker:
            self.worker.cancel()
            self.status_label.setText("Cancelling...")
            self.cancel_btn.setEnabled(False)

    def update_progress(self, v):
        self.progress_bar.setValue(v)
        self.status_label.setText(f"Processing... {v}%")

    def update_preview(self, image):
        h, w = image.shape[:2]
        if image.ndim == 3 and image.shape[2] == 4:
            qimg = QImage(image.data, w, h, 4 * w, QImage.Format_RGBA8888)
        elif image.ndim == 3:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            qimg = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888)
        else:
            qimg = QImage(image.data, w, h, w, QImage.Format_Grayscale8)
        pix = QPixmap.fromImage(qimg)
        self.preview_label.setPixmap(pix.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def processing_finished(self, out_path):
        self.progress_bar.setValue(100)
        self.status_label.setText(f"✅ Complete! Saved: {os.path.basename(out_path)}")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.open_folder_btn.setEnabled(True)
        QMessageBox.information(self, "Success", f"Processing complete!\n\nOutput saved to:\n{out_path}")

    def processing_error(self, msg):
        self.status_label.setText(f"❌ Error: {msg}")
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"Processing failed:\n{msg}")

    def open_output_folder(self):
        if self.output_path and os.path.exists(self.output_path):
            folder = os.path.dirname(os.path.abspath(self.output_path))
            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                os.system(f'open "{folder}"')
            else:
                os.system(f'xdg-open "{folder}"')

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            self.load_file(urls[0].toLocalFile())

    def get_dark_theme(self):
        return """
            QMainWindow { background-color: #1e1e1e; }
            QWidget { background-color: #1e1e1e; color: white; font-family: Arial; font-size: 13px; }
            QGroupBox { border: 2px solid #555; border-radius: 5px; margin-top: 10px; padding-top: 10px;
                        font-weight: bold; color: #00D4FF; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QLabel { color: white; }
            QSlider::groove:horizontal { border: 1px solid #555; height: 8px; background: #2b2b2b; border-radius: 4px; }
            QSlider::handle:horizontal { background: #00D4FF; border: 1px solid #00D4FF; width: 18px; margin: -5px 0; border-radius: 9px; }
        """

    def button_style(self, color="#555"):
        return f"""
            QPushButton {{
                background-color: {color}; color: white; border: none; padding: 10px;
                border-radius: 5px; font-weight: bold; font-size: 14px;
            }}
            QPushButton:hover {{ background-color: {color}dd; }}
            QPushButton:pressed {{ background-color: {color}aa; }}
            QPushButton:disabled {{ background-color: #2b2b2b; color: #555; }}
        """


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    win = FaceBlurStudioPro()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()