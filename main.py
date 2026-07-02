import cv2
import mediapipe as mp

def main():
    cap = cv2.VideoCapture(0)
    
    # 1. Initialize MediaPipe Hands tools
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    
    # Configure the hands detection module
    hands = mp_hands.Hands(
        static_image_mode=False,        # False means track smoothly like video frames
        max_num_hands=2,                # Track up to two hands
        min_detection_confidence=0.7,   # 70% confidence needed to detect a hand initially
        min_tracking_confidence=0.7    # 70% confidence needed to keep tracking it
    )

    print("AI Hand Tracking started! Raise your hand to the camera. Press 'q' to exit.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape  # Fetch frame dimensions (height, width, channels)

        # MediaPipe requires RGB images, but OpenCV processes frames in BGR format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame and find hands
        results = hands.process(rgb_frame)

        # If any hands are detected on screen
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw the standard skeleton lines connecting the 21 dots
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Extract the Index Finger Tip coordinate (Landmark index #8)
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                
                # Convert normalized coordinates (0.0 to 1.0) into actual pixel locations on your screen
                cx, cy = int(index_tip.x * w), int(index_tip.y * h)
                
                # Draw a custom glowing circle right on your index finger tip
                cv2.circle(frame, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

        # Display output window
        cv2.imshow('Virtual Flowers Project - Hand Tracking', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources safely
    hands.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()