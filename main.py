import cv2

def main():
    # Initialize the webcam (0 is typically the default built-in camera)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open the webcam. Please check your camera connection.")
        return

    print("Webcam successfully started! Press 'q' on your keyboard to close the window.")

    while cap.isOpened():
        # Capture frame-by-frame from the camera
        success, frame = cap.read()
        if not success:
            print("Error: Empty frame received from camera.")
            continue

        # Flip the frame horizontally so it acts like a mirror (selfie view)
        # This makes hand gestures much more natural to control!
        frame = cv2.flip(frame, 1)

        # Open a window and display the live camera frame
        cv2.imshow('Virtual Flowers Project - Test View', frame)

        # Wait for 1 millisecond. If the user presses 'q', break out of the loop.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the camera and close all windows safely
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()