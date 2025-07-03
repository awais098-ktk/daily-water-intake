# Troubleshooting Guide for Water Intake Tracker

If you're experiencing issues with the Water Intake Tracker application, this guide will help you resolve common problems.

## Connection Refused Error

If you see "127.0.0.1 refused to connect" or "ERR_CONNECTION_REFUSED":

1. **Check if the application is running**:
   - Look for a command prompt window showing the Flask server
   - If it's not running, start it with `python run.py` or by double-clicking `run.bat`

2. **Use the correct port**:
   - The application now runs on port 8080 instead of 5000
   - Make sure you're accessing http://127.0.0.1:8080 in your browser
   - If you need to use a different port, you can change it in `run.py`

3. **Check for port conflicts**:
   - Another application might be using port 8080
   - If that's the case, edit `run.py` to use a different port (e.g., 8081, 8082, etc.)

4. **Firewall issues**:
   - Make sure your firewall isn't blocking the application
   - Try temporarily disabling the firewall to test

## Database Issues

If you're having problems with the database:

1. **Reset the database**:
   - Delete the `water_tracker/water_tracker.db` file
   - Restart the application to create a fresh database

2. **Check file permissions**:
   - Make sure the application has write permissions to the directory

## UI Glitches

If the UI is glitching or not displaying correctly:

1. **Clear browser cache**:
   - Press Ctrl+F5 to force refresh the page
   - Or clear your browser cache completely

2. **Try a different browser**:
   - Some features may work better in Chrome, Firefox, or Edge

3. **Check for JavaScript errors**:
   - Open browser developer tools (F12) and check the console for errors

## Missing Features

If some features are not working:

1. **Container Recognition**:
   - Requires OpenCV to be installed: `pip install opencv-python`

2. **OCR Label Reading**:
   - Requires Tesseract OCR to be installed
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki

3. **Voice Input**:
   - Requires FFmpeg to be installed
   - Download from: https://ffmpeg.org/download.html
   - Also requires SpeechRecognition: `pip install SpeechRecognition`

## Avatar Generation Issues

If avatar generation is not working:

1. **Using simple avatars**:
   - Run `python water_tracker/generate_simple_avatars.py`
   - This uses PIL instead of Cairo

2. **Check image directories**:
   - Make sure the `water_tracker/static/images/avatars` directory exists

## Performance Issues

If the application is slow or unresponsive:

1. **Check system resources**:
   - Make sure you have enough RAM and CPU available

2. **Reduce database size**:
   - If you've been using the app for a long time, consider resetting the database

3. **Update your browser**:
   - Older browsers may have performance issues with modern web applications

## Still Having Issues?

If you're still experiencing problems:

1. **Check the logs**:
   - Look at the command prompt window for error messages
   - Check your browser console (F12) for JavaScript errors

2. **Try a clean installation**:
   - Delete and re-clone the repository
   - Install all dependencies fresh
   - Create a new database

3. **System requirements**:
   - Python 3.7 or higher is recommended
   - Modern web browser (Chrome, Firefox, Edge)
   - At least 4GB of RAM
