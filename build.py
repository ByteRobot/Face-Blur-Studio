import PyInstaller.__main__
import sys
import os

# PyInstaller command
PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--name=FaceBlur-Pro',
    # '--icon=icon.ico',  # ← Yeh line remove kar do
    '--add-data=models:models',
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