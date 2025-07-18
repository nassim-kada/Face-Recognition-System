# Enhanced Face Recognition Access Control System

A modern, GUI-based face recognition access control system for secure user management and real-time access logging. Built with Python, OpenCV, face_recognition, and Tkinter.

## Features
- **Face Recognition**: Real-time face detection and recognition using webcam.
- **Admin Panel**: Secure login for administrators to manage users and view access logs.
- **User Management**: Add, edit, and delete users with face image capture.
- **Access Logs**: Automatic logging of all access attempts (granted/denied) with timestamps.
- **Encodings Management**: Regenerate face encodings as needed.
- **Modern GUI**: User-friendly interface built with Tkinter.

## Project Structure
```
├── database_manager.py        # Handles SQLite database operations
├── enhanced_encoder.py        # Face encoding generation and management
├── run_face_recognition.py    # Real-time face recognition logic
├── main_gui.py                # Main GUI application (Tkinter)
├── requirements.txt           # Python dependencies
├── EncodedImages.p            # Pickled face encodings (auto-generated)
├── img/
│   └── Modes/                 # User face images (auto-managed)
├── README.md                  # Project documentation
```

## Installation
1. **Clone the repository**
2. **Create a virtual environment** (recommended):
   ```sh
   python3 -m venv myenv
   source myenv/bin/activate
   ```
3. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

## Usage
1. **Run the main GUI**:
   ```sh
   python main_gui.py
   ```
2. **Default Admin Login**:
   - Username: `admin`
   - Password: `admin123`
3. **Add users** via the Admin Panel (capture face images for recognition).
4. **Use the CHECK button** to start real-time face recognition.
5. **Monitor access logs** in the Admin Panel.

## Requirements
- Python 3.8+
- Webcam
- Linux, Windows, or macOS

## Dependencies
See `requirements.txt` for all Python packages:
- opencv-python
- face-recognition
- face-recognition-models
- numpy
- pillow
- tk
- sqlite3 (usually included with Python)

## Notes
- All user face images are stored in `img/Modes/`.
- Face encodings are stored in `EncodedImages.p` (auto-generated).
- The database is `face_recognition.db` (auto-generated).
- For best results, use clear, front-facing face images.
- If you got problem while installing face_recognition you have to make sure that cMake and dlib are correctly installed in your pc 



---

<p align="center">
  <b>🤝 Feel free to contribute or reach out:</b><br>
  <a href="mailto:kadanassim42@gmail.com">kadanassim42@gmail.com</a>
</p>