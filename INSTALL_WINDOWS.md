# Windows Installation Guide

## Installing PyAudio (Required for Microphone Input)

PyAudio requires compilation on Windows, which needs Microsoft Visual C++ Build Tools. Here are two easy ways to install it:

### Option 1: Using pipwin (Recommended - Easiest)

1. Install pipwin:
   ```bash
   pip install pipwin
   ```

2. Install PyAudio using pipwin (uses pre-built wheels):
   ```bash
   pipwin install pyaudio
   ```

### Option 2: Download Pre-built Wheel

1. Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

2. Download the wheel file matching your Python version:
   - For Python 3.11 (64-bit): `PyAudio-0.2.11-cp311-cp311-win_amd64.whl`
   - For Python 3.10 (64-bit): `PyAudio-0.2.11-cp310-cp310-win_amd64.whl`
   - For Python 3.9 (64-bit): `PyAudio-0.2.11-cp39-cp39-win_amd64.whl`
   - (Adjust for your Python version and architecture)

3. Install the wheel:
   ```bash
   pip install PyAudio-0.2.11-cp311-cp311-win_amd64.whl
   ```
   (Replace with the filename you downloaded)

### Option 3: Install Visual C++ Build Tools (If you want to compile)

1. Download and install Microsoft C++ Build Tools:
   https://visualstudio.microsoft.com/visual-cpp-build-tools/

2. Then install normally:
   ```bash
   pip install pyaudio
   ```

## Quick Install Script

After installing pipwin, you can run:
```bash
pip install pipwin
pipwin install pyaudio
pip install -r requirements.txt
```

This will install all dependencies including PyAudio without needing build tools!

