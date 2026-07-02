import cv2
import mediapipe as mp
import math
from flower import InstagramFlower

def get_hand_metrics(hand_landmarks, w, h):
    """Calculates an expansion metric between the thumb and pinky tip relative to hand size."""
    thumb = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
    pinky = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP]
    wrist = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST]
    
    # Absolute pixel distances
    span = math.hypot(int(thumb.x * w) - int(pinky.x * w), int(thumb.y * h) - int(pinky.y * h))
    scale = math.hypot(int(thumb.x * w) - int(wrist.x * w), int(thumb.y * h) - int(wrist.y * h))
    
    # Normalize ratio to a strict 0.0 - 1.0 window
    ratio = span / max(1.0, scale)
    normalized = (ratio - 0.4) / 1.1
    return max(0.0, min(1.0, normalized))

def main():
    cap = cv2.VideoCapture(0)
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.75, min_tracking_confidence=0.75)
    
    # The 5 fingertips on the target hand where flowers sprout
    fingertips = [
        mp_hands.HandLandmark.THUMB_TIP,
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ]
    
    # Instantiating the flower templates exclusively for the growing hand
    flower_system = {tip: InstagramFlower() for tip in fingertips}
    
    # Independent variables driven by matching hands
    grow_value = 0.0
    bloom_value = 0.0

    print("Premium Interactive AR Filter active! Press 'q' to close.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # Flag trackers to watch if hands leave camera range
        left_hand_present = False
        right_hand_present = False

        if results.multi_hand_landmarks and results.multi_handedness:
            # Pass 1: Extract hand identities and compute dynamic variables
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_side = handedness.classification[0].label # "Left" or "Right"
                current_ratio = get_hand_metrics(hand_landmarks, w, h)
                
                # Fetch reference points for drawing side-aligned indicator tracking lines
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
                
                wx, wy = int(wrist.x * w), int(wrist.y * h)
                ix, iy = int(index_mcp.x * w), int(index_mcp.y * h)

                if hand_side == "Left":
                    left_hand_present = True
                    # Left hand drives Growth
                    grow_value = grow_value + 0.06 if current_ratio > 0.4 else grow_value - 0.06
                    grow_value = max(0.0, min(1.0, grow_value))
                    
                    # Draw Blue Tracking Line next to Left Hand
                    cv2.line(frame, (wx - 30, wy), (ix - 30, wy - 120), (245, 130, 60), 4, cv2.LINE_AA)
                    cv2.putText(frame, f"Grow: {grow_value:.2f}", (wx - 70, wy + 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

                elif hand_side == "Right":
                    right_hand_present = True
                    # Right hand drives Bloom
                    bloom_value = bloom_value + 0.06 if current_ratio > 0.4 else bloom_value - 0.06
                    bloom_value = max(0.0, min(1.0, bloom_value))
                    
                    # Draw Purple Tracking Line next to Right Hand
                    cv2.line(frame, (wx + 30, wy), (ix + 30, wy - 120), (190, 80, 160), 4, cv2.LINE_AA)
                    cv2.putText(frame, f"Bloom: {bloom_value:.2f}", (wx - 20, wy + 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

            # Pass 2: Map and draw the flowers exclusively onto the Left Hand fingertips
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_side = handedness.classification[0].label
                
                if hand_side == "Left":
                    for tip_id in fingertips:
                        lm = hand_landmarks.landmark[tip_id]
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        
                        flower = flower_system[tip_id]
                        flower.update_position(cx, cy, grow_value)
                        flower.draw(frame, grow_value, bloom_value)

        # Decay metrics smoothly back to 0 if a hand drops out of the camera view box
        if not left_hand_present and grow_value > 0: grow_value = max(0.0, grow_value - 0.03)
        if not right_hand_present and bloom_value > 0: bloom_value = max(0.0, bloom_value - 0.03)

        cv2.imshow('Virtual Lotus Gestures - Procedural AR Mode', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    hands.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()