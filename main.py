import cv2
import mediapipe as mp
import math
from flower import InstagramFlower

def get_hand_open_ratio(hand_landmarks, w, h):
    """Calculates general hand openness for the Left Grow Hand."""
    thumb = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
    pinky = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP]
    wrist = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST]
    span = math.hypot(int(thumb.x * w) - int(pinky.x * w), int(thumb.y * h) - int(pinky.y * h))
    scale = math.hypot(int(thumb.x * w) - int(wrist.x * w), int(thumb.y * h) - int(wrist.y * h))
    return max(0.0, min(1.0, (span / max(1.0, scale) - 0.4) / 1.1))

def get_index_pinch_ratio(hand_landmarks, w, h):
    """Calculates bloom purely based on the Right Hand's Thumb-to-Index spacing."""
    thumb = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
    index = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
    wrist = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST]
    
    # Distance between thumb and index tip
    pinch_dist = math.hypot(int(thumb.x * w) - int(index.x * w), int(thumb.y * h) - int(index.y * h))
    # Normalize against wrist size so moving closer/further from camera doesn't break it
    scale = math.hypot(int(thumb.x * w) - int(wrist.x * w), int(thumb.y * h) - int(wrist.y * h))
    
    ratio = pinch_dist / max(1.0, scale)
    # Scale nicely between a pinch (0) and open fingers (1)
    return max(0.0, min(1.0, (ratio - 0.15) / 0.85))

def main():
    cap = cv2.VideoCapture(0)
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.75, min_tracking_confidence=0.75)
    
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
                
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
                wx, wy = int(wrist.x * w), int(wrist.y * h)
                ix, iy = int(index_mcp.x * w), int(index_mcp.y * h)

                if hand_side == "Left":
                    left_hand_present = True
                    current_ratio = get_hand_open_ratio(hand_landmarks, w, h)
                    # Smooth tracking interpolation
                    grow_value = grow_value + 0.07 if current_ratio > 0.4 else grow_value - 0.07
                    grow_value = max(0.0, min(1.0, grow_value))
                    
                    # Left Grow Line Indicator
                    cv2.line(frame, (wx - 30, wy), (ix - 30, wy - 120), (245, 130, 60), 4, cv2.LINE_AA)
                    cv2.putText(frame, f"Grow: {grow_value:.2f}", (wx - 70, wy + 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

                elif hand_side == "Right":
                    right_hand_present = True
                    # NEW: Get bloom ratio STRICTLY from index finger & thumb pinch gesture
                    target_bloom = get_index_pinch_ratio(hand_landmarks, w, h)
                    
                    # Smoothly transition bloom values
                    if abs(bloom_value - target_bloom) > 0.02:
                        bloom_value += 0.08 if bloom_value < target_bloom else -0.08
                    bloom_value = max(0.0, min(1.0, bloom_value))
                    
                    # Highlight tracking explicitly on right Index + Thumb tips to look cool
                    r_thumb = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    r_index = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    cv2.circle(frame, (int(r_thumb.x * w), int(r_thumb.y * h)), 7, (190, 80, 160), -1)
                    cv2.circle(frame, (int(r_index.x * w), int(r_index.y * h)), 7, (190, 80, 160), -1)
                    
                    # Right Bloom Line Indicator
                    cv2.line(frame, (wx + 30, wy), (ix + 30, wy - 120), (190, 80, 160), 4, cv2.LINE_AA)
                    cv2.putText(frame, f"Bloom: {bloom_value:.2f}", (wx - 20, wy + 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

            # Draw flowers on Left hand
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                if handedness.classification[0].label == "Left":
                    for tip_id in fingertips:
                        lm = hand_landmarks.landmark[tip_id]
                        flower = flower_system[tip_id]
                        flower.update_position(int(lm.x * w), int(lm.y * h), grow_value)
                        flower.draw(frame, grow_value, bloom_value)

        if not left_hand_present and grow_value > 0: grow_value = max(0.0, grow_value - 0.04)
        if not right_hand_present and bloom_value > 0: bloom_value = max(0.0, bloom_value - 0.04)

        cv2.imshow('Virtual Lotus Gestures - Index Control Mode', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    hands.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()