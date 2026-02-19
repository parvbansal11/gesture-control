from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from gesture_engine import engine
import json
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gesture123'
socketio = SocketIO(app, cors_allowed_origins="*")

GESTURES_FILE = "gestures.json"

def load_gestures():
    with open(GESTURES_FILE, "r") as f:
        return json.load(f)

def save_gestures(data):
    with open(GESTURES_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/gestures", methods=["GET"])
def get_gestures():
    return jsonify(load_gestures())

@app.route("/api/gestures", methods=["POST"])
def add_gesture():
    data = load_gestures()
    body = request.json
    new_gesture = {
        "id": data["next_id"],
        "name": body["name"],
        "action": body["action"],
        "description": body.get("description", ""),
        "fingers": body.get("fingers", "")
    }
    data["gestures"].append(new_gesture)
    data["next_id"] += 1
    save_gestures(data)
    return jsonify({"success": True, "gesture": new_gesture})

@app.route("/api/gestures/<int:gesture_id>", methods=["DELETE"])
def delete_gesture(gesture_id):
    data = load_gestures()
    data["gestures"] = [g for g in data["gestures"] if g["id"] != gesture_id]
    save_gestures(data)
    return jsonify({"success": True})

@app.route("/api/engine/start", methods=["POST"])
def start_engine():
    engine.start()
    return jsonify({"status": "running"})

@app.route("/api/engine/stop", methods=["POST"])
def stop_engine():
    engine.stop()
    return jsonify({"status": "stopped"})

@app.route("/api/engine/status", methods=["GET"])
def engine_status():
    return jsonify({
        "status": engine.status,
        "last_action": engine.last_action,
        "last_gesture": engine.last_gesture,
        "finger_count": engine.finger_count
    })

@app.route("/api/retrain", methods=["POST"])
def retrain():
    def simulate_training():
        engine.status = "training"
        time.sleep(4)
        engine.status = "stopped"
        socketio.emit("retrain_complete", {"message": "Model retrained successfully!"})
    threading.Thread(target=simulate_training, daemon=True).start()
    return jsonify({"status": "training started"})

@app.route("/api/gestures/record", methods=["POST"])
def record_gesture():
    def do_recording():
        import cv2
        import mediapipe as mp
        mp_hands = mp.solutions.hands
        samples = []
        start_time = time.time()
        cap = cv2.VideoCapture(0)
        with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7) as hands:
            while time.time() - start_time < 3:
                ret, frame = cap.read()
                if not ret:
                    continue
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(frame_rgb)
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        finger_count = len([
                            tip for tip in [8, 12, 16, 20]
                            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y
                        ])
                        samples.append(finger_count)
                time.sleep(0.05)
        cap.release()
        if samples:
            avg = round(sum(samples) / len(samples))
            socketio.emit("record_complete", {"finger_count": avg})
        else:
            socketio.emit("record_complete", {"finger_count": -1})
    threading.Thread(target=do_recording, daemon=True).start()
    return jsonify({"status": "recording started"})

if __name__ == "__main__":
    socketio.run(app, debug=False, port=5000)
