# GestureOS 👾
### Gesture-Based Desktop Control System

A real-time hand gesture recognition system that lets you control your desktop using hand gestures through your webcam. Built with a clean web dashboard for managing gestures, monitoring system status, and triggering desktop actions — no mouse or keyboard needed.

---

## Demo
- ▶ Start recognition and show your hand to the webcam
- The system detects finger positions in real time using MediaPipe
- Desktop actions fire automatically based on your gesture

---

## Features
- 📷 Live webcam feed embedded in the dashboard
- 🤖 Real-time hand gesture recognition using MediaPipe + OpenCV
- 🖥️ Desktop control — switch tabs, control volume, play/pause media
- ➕ Add custom gestures with a guided recording flow
- 🗑️ Delete gestures from the library
- ⟳ One-click model retraining with live status feedback
- 📊 Live activity log with WebSocket updates
- 🎨 Clean dark UI inspired by modern design systems

---

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask, Flask-SocketIO |
| Gesture Recognition | MediaPipe, OpenCV |
| Desktop Control | PyAutoGUI, AppleScript |
| Real-time Updates | WebSockets |

---

## Gesture Mapping
| Fingers Up | Action |
|-----------|--------|
| 0 (Fist) | Play / Pause |
| 2 fingers | Previous Tab |
| 3 fingers | Next Tab |
| 5 (Open Palm) | Volume Up |

---

## Installation

**Requirements:** Python 3.11, Mac OS

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/gesture-control.git
cd gesture-control

# Set Python version
pyenv local 3.11.9

# Install dependencies
pip install flask flask-socketio mediapipe==0.10.9 opencv-python pyautogui pillow

# Run the app
python3 main.py
