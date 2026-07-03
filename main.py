import cv2
import mediapipe as mp
import math
import os
import random
import numpy as np
from flower import InstagramFlower

class PollenParticle:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-2.5, 2.5)
        self.vy = random.uniform(-4.0, -1.5)
        self.alpha = 1.0  
        self.fade_speed = random.uniform(0.02, 0.04)
        self.size = random.randint(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= self.fade_speed
        return self.alpha > 0

def get_hand_open_ratio(hand_landmarks, w, h):
    thumb = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
    pinky = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP]
    wrist = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST]
    span = math.hypot(int(thumb.x * w) - int(pinky.x * w), int(thumb.y * h) - int(pinky.y * h))
    scale = math.hypot(int(thumb.x * w) - int(wrist.x * w), int(thumb.y * h) - int(wrist.y * h))
    return max(0.0, min(1.0, (span / max(1.0, scale) - 0.4) / 1.1))

def get_index_pinch_ratio(hand_landmarks, w, h):
    thumb = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
    index = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
    wrist = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST]
    pinch_dist = math.hypot(int(thumb.x * w) - int(index.x * w), int(thumb.y * h) - int(index.y * h))
    scale = math.hypot(int(thumb.x * w) - int(wrist.x * w), int(thumb.y * h) - int(wrist.y * h))
    ratio = pinch_dist / max(1.0, scale)
    return max(0.0, min(1.0, (ratio - 0.15) / 0.85))

def main():
    if not os.path.exists('assets'):
        os.makedirs('assets')

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=2, 
        model_complexity=0, 
        min_detection_confidence=0.7, 
        min_tracking_confidence=0.7
    )
    
    fingertips = [
        mp_hands.HandLandmark.THUMB_TIP,
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ]
    
    flower_system = {tip: InstagramFlower() for tip in fingertips}
    grow_value = 0.0
    bloom_value = 0.0
    
    particles = []
    pollen_triggered = False

    print("Single Asset Bouquet Engine Online! Press 'q' to quit.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        left_hand_present = False
        right_hand_present = False

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_side = handedness.classification[0].label

                if hand_side == "Left":
                    left_hand_present = True
                    current_ratio = get_hand_open_ratio(hand_landmarks, w, h)
                    grow_value = grow_value + 0.07 if current_ratio > 0.4 else grow_value - 0.07
                    grow_value = max(0.0, min(1.0, grow_value))

                elif hand_side == "Right":
                    right_hand_present = True
                    target_bloom = get_index_pinch_ratio(hand_landmarks, w, h)
                    
                    if abs(bloom_value - target_bloom) > 0.02:
                        bloom_value += 0.08 if bloom_value < target_bloom else -0.08
                    bloom_value = max(0.0, min(1.0, bloom_value))

        if not left_hand_present and grow_value > 0: grow_value = max(0.0, grow_value - 0.04)
        if not right_hand_present and bloom_value > 0: bloom_value = max(0.0, bloom_value - 0.04)

        # Draw UI Overlay Elements
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_side = handedness.classification[0].label
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                wx, wy = int(wrist.x * w), int(wrist.y * h)

                if hand_side == "Left":
                    cv2.line(frame, (wx - 40, wy), (wx - 40, wy - 150), (245, 130, 60), 4, cv2.LINE_AA)
                    cv2.putText(frame, f"Grow: {grow_value:.2f}", (wx - 80, wy + 35),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

                elif hand_side == "Right":
                    r_thumb = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    r_index = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    cv2.circle(frame, (int(r_thumb.x * w), int(r_thumb.y * h)), 6, (190, 80, 160), -1, cv2.LINE_AA)
                    cv2.circle(frame, (int(r_index.x * w), int(r_index.y * h)), 6, (190, 80, 160), -1, cv2.LINE_AA)
                    
                    cv2.line(frame, (wx + 40, wy), (wx + 40, wy - 150), (190, 80, 160), 4, cv2.LINE_AA)
                    cv2.putText(frame, f"Bloom: {bloom_value:.2f}", (wx - 10, wy + 35),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

            # Render Bouquet Layers
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                if handedness.classification[0].label == "Left":
                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                    wwx, wwy = int(wrist.x * w), int(wrist.y * h)
                    
                    for tip_id in fingertips:
                        lm = hand_landmarks.landmark[tip_id]
                        flower = flower_system[tip_id]
                        flower.update_bouquet_position(wwx, wwy, int(lm.x * w), int(lm.y * h), grow_value)
                    
                    for tip_id in fingertips:
                        flower_system[tip_id].draw_all_branches(frame, grow_value)
                        
                    for tip_id in fingertips:
                        flower_system[tip_id].draw_all_flowers(frame, grow_value, bloom_value)

                    # Burst Pollen Trigger Mechanics
                    if bloom_value > 0.95 and not pollen_triggered and grow_value > 0.6:
                        pollen_triggered = True
                        for tip_id in fingertips:
                            for i in range(3):
                                hx, hy = flower_system[tip_id].get_sub_branch_endpoints(i, grow_value)
                                for _ in range(3):  
                                    particles.append(PollenParticle(hx, hy))
                    
                    if bloom_value < 0.7:
                        pollen_triggered = False

        # Live Particle Animation Processing Loop
        active_particles = []
        for p in particles:
            if p.update():
                active_particles.append(p)
                overlay = frame.copy()
                cv2.circle(overlay, (int(p.x), int(p.y)), p.size, (180, 80, 255), -1, cv2.LINE_AA)
                cv2.addWeighted(overlay, p.alpha, frame, 1.0 - p.alpha, 0, frame)
        particles = active_particles

        cv2.imshow('Virtual Lotus Bouquet - TouchDesigner Aesthetic', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    hands.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()