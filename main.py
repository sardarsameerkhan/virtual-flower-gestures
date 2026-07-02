import cv2
import mediapipe as mp
import math
from flower import VirtualFlower

def get_distance(p1, p2, w, h):
    """Utility to calculate distance in pixels between two landmarks."""
    return math.hypot(int(p1.x * w) - int(p2.x * w), int(p1.y * h) - int(p2.y * h))

def main():
    cap = cv2.VideoCapture(0)
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    
    # Define tracking IDs for the tips of all 5 fingers
    fingertips = [
        mp_hands.HandLandmark.THUMB_TIP,
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ]
    
    # Assign a dedicated VirtualFlower instance to each finger
    flowers = {tip: VirtualFlower() for tip in fingertips}

    print("Virtual Instagram Filter Activated! Open your hand to bloom flowers.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                
                # Check gesture status: Measure distance between thumb tip and pinky tip
                thumb = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                pinky = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                
                spread_dist = get_distance(thumb, pinky, w, h)
                hand_scale = get_distance(thumb, wrist, w, h) # Account for hand distance from camera
                
                # Normalize openness ratio (independent of how close your hand is to camera)
                open_ratio = spread_dist / max(1.0, hand_scale)
                
                # Threshold to recognize an open hand gesture
                is_hand_open = open_ratio > 0.8
                
                # Update and render each flower right over the fingertips
                for tip_id in fingertips:
                    lm = hand_landmarks.landmark[tip_id]
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    
                    flower = flowers[tip_id]
                    flower.update(cx, cy, is_hand_open, open_ratio)
                    flower.draw(frame)
                    
                # Render screen stats layout matching the reference
                label = "Status: Growing & Blooming" if is_hand_open else "Status: Waiting for Gesture"
                cv2.putText(frame, label, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 100), 2, cv2.LINE_AA)

        cv2.imshow('Virtual Instagram Flowers', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    hands.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()