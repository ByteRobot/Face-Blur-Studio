import PyInstaller.__main__
import sys
import os

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--name=FaceBlur-Pro',
    '--icon=icon.ico',
    '--add-data=models:models',
    '--add-data=models/yolov8n.pt:models',
    '--add-data=processors:processors',
    '--add-data=ui:ui',
    '--add-data=utils:utils',
    '--hidden-import=ultralytics',
    '--hidden-import=torch',
    '--hidden-import=cv2',
    '--hidden-import=PyQt5',
    '--collect-all=ultralytics',
    '--collect-all=torch',
])
print("\n✅ .exe file created successfully!")
print("📁 Location: dist/FaceBlur-Pro.exe")
