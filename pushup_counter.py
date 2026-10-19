
import cv2
import mediapipe as mp
import math
import numpy as np

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils


def calculate_angle(a, b, c):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    c = np.array(c, dtype=float)

    ba = a - b
    bc = c - b

    denominator = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denominator == 0:
        return 0

    cosine = np.dot(ba, bc) / denominator
    cosine = np.clip(cosine, -1.0, 1.0)
    return math.degrees(math.acos(cosine))


cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise SystemExit("Camera unavailable. Close other camera apps.")

reps = 0
stage = "UP"
message = "Show your upper body from the side"

try:
    with mp_pose.Pose(
        model_complexity=0,
        min_detection_confidence=0.4,
        min_tracking_confidence=0.4
    ) as pose:

        while True:
            success, frame = cap.read()

            if not success:
                print("Could not read camera frame.")
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)

            if result.pose_landmarks:
                # Draw skeleton even if some landmarks are less visible
                mp_draw.draw_landmarks(
                    frame,
                    result.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

                landmarks = result.pose_landmarks.landmark
                ids = mp_pose.PoseLandmark

                shoulder = landmarks[ids.RIGHT_SHOULDER.value]
                elbow = landmarks[ids.RIGHT_ELBOW.value]
                wrist = landmarks[ids.RIGHT_WRIST.value]

                visible = all(
                    p.visibility > 0.35
                    for p in [shoulder, elbow, wrist]
                )

                if visible:
                    elbow_angle = calculate_angle(
                        (shoulder.x, shoulder.y),
                        (elbow.x, elbow.y),
                        (wrist.x, wrist.y)
                    )

                    # Simple repetition state machine
                    if elbow_angle < 90 and stage == "UP":
                        stage = "DOWN"
                    elif elbow_angle > 150 and stage == "DOWN":
                        reps += 1
                        stage = "UP"

                    message = "Arm detected"
                    cv2.putText(
                        frame,
                        f"Elbow angle: {int(elbow_angle)}",
                        (20, 130),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 255), 2
                    )
                else:
                    message = "Move arm into clear view"

            else:
                message = "No pose detected - move back"

            cv2.putText(
                frame, f"Push-ups: {reps}",
                (20, 45), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 0), 2
            )
            cv2.putText(
                frame, f"Stage: {stage}",
                (20, 85), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (255, 255, 255), 2
            )
            cv2.putText(
                frame, message,
                (20, frame.shape[0] - 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (0, 200, 255), 2
            )

            cv2.imshow("Sports Talent Assessment", frame)

            # Q or closing the window exits cleanly
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

            if cv2.getWindowProperty(
                "Sports Talent Assessment",
                cv2.WND_PROP_VISIBLE
            ) < 1:
                break

finally:
    cap.release()
    cv2.destroyAllWindows()
