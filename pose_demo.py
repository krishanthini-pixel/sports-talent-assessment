import cv2
import mediapipe as mp

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

# Open the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera not available. Check camera permissions.")
    raise SystemExit

print("Pose detection started! Press Q to quit.")

try:
    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:

        while True:
            success, frame = cap.read()

            if not success:
                print("Unable to read webcam frame.")
                break

            # Mirror the webcam image
            frame = cv2.flip(frame, 1)

            # Convert image from BGR to RGB
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect body landmarks
            result = pose.process(rgb)

            if result.pose_landmarks:
                mp_draw.draw_landmarks(
                    frame,
                    result.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

                message = "Body Detected!"
                color = (0, 255, 0)
            else:
                message = "No Pose Detected"
                color = (0, 0, 255)

            cv2.putText(
                frame,
                message,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                color,
                2
            )

            cv2.imshow("Sports Talent Assessment", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

finally:
    cap.release()
    cv2.destroyAllWindows()
