import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install required packages
packages = [
    "flask",
    "flask-sqlalchemy",
    "flask-login",
    "werkzeug",
    "pillow",
    "requests",
    "pytesseract",
    "numpy",
    "matplotlib",
    "SpeechRecognition",
    "pydub"
]

for package in packages:
    print(f"Installing {package}...")
    install(package)

print("\nAll packages installed successfully!")
