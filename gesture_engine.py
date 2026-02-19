import cv2
import mediapipe as mp
import pyautogui
import json
import time
import threading
import subprocess

pyautogui.FAILSAFE = False

mp_hands = mp.solutions.hands

def load_gestures():
    with open("gestures.json", "r") as f:
        return json.load(f)

def count_fingers(hand_landmarks):
    tips = [8, 12, 16, 20]
    fingers_up = 0
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fingers_up += 1
    for tip in tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers_up += 1
    return fingers_up

def perform_action(action):
    print(f"Performing action: {action}")
    if action == "prev_tab":
        pyautogui.hotkey("command", "shift", "tab")
    elif action == "next_tab":
        pyautogui.hotkey("command", "tab")
    elif action == "media_pause":
        pyautogui.press("space")
    elif action == "volume_up":
        subprocess.call(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"])
    elif action == "volume_down":
        subprocess.call(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"])
    elif action == "next_track":
        subprocess.call(["osascript", "-e", "tell application \"Music\" to next track"])
    elif action == "prev_track":
        subprocess.call(["osascript", "-e", "tell application \"Music\" to previous track"])

def recognize_gesture(finger_count):
    mapping = {
        0: "media_pause",
        2: "prev_tab",
        3: "next_tab",
        5: "volume_up",
    }
    return mapping.get(finger_count, None)

class GestureEngine:
    def __init__(self):
        self.running = False
        self.status = "stopped"
        self.last_action = None
        self.last_gesture = None
        self.finger_count = -1
        self.thread = None
        self.cooldown = 2

    def start(self):
        if not self.running:
            self.running = True
            self.status = "running"
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        self.status = "stopped"

    def _run(self):
        last_action_time = 0
        cap = cv2.VideoCapture(0)
        with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7) as hands:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.05)
                    continue

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(frame_rgb)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        finger_count = count_fingers(hand_landmarks)
                        action = recognize_gesture(finger_count)

                        self.finger_count = finger_count
                        self.last_gesture = f"{finger_count} fingers"

                        current_time = time.time()
                        if action and (current_time - last_action_time) > self.cooldown:
                            perform_action(action)
                            self.last_action = action
                            last_action_time = current_time

                time.sleep(0.05)
        cap.release()

engine = GestureEngine()
