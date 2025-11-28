# import cv2
# import mediapipe as mp
# import json
# import math

# mp_pose = mp.solutions.pose
# mp_drawing = mp.solutions.drawing_utils

# def angle(p1, p2):
#     dx = p2["x"] - p1["x"]
#     dy = p2["y"] - p1["y"]
#     return math.degrees(math.atan2(dy, dx))

# def to_pixel(lm, w, h):
#     return int(lm.x * w), int(lm.y * h)

# # LOAD CALIBRATION
# with open("calibration_data.json", "r") as f:
#     calib = json.load(f)

# baseline = calib["Neutral Standing"]

# baseline_neck = angle(baseline["left_shoulder"], baseline["left_ear"])
# baseline_torso = angle(baseline["left_hip"], baseline["left_shoulder"])

# # THRESHOLDS
# NECK_THRESHOLD = 12
# TORSO_THRESHOLD = 10

# pose = mp_pose.Pose(
#     model_complexity=1,
#     smooth_landmarks=True,
#     min_detection_confidence=0.5,
#     min_tracking_confidence=0.5
# )

# cap = cv2.VideoCapture(0)

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     frame = cv2.flip(frame, 1)
#     h, w, _ = frame.shape
#     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = pose.process(rgb)

#     if results.pose_landmarks:
#         lm = results.pose_landmarks.landmark

#         # -------------------------
#         # SIDE VIEW DETECTION (using z-axis depth difference)
#         # -------------------------
#         z_left = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].z
#         z_right = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].z
#         z_diff = abs(z_left - z_right)

#         side_view = z_diff > 0.10  # ← If facing sideways, shoulders differ in depth

#         if not side_view:
#             cv2.putText(frame, "TURN SIDEWAYS (SIDE VIEW REQUIRED)", (30,50),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
#             mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
#             cv2.imshow("Posture Detection Test", frame)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
#             continue

#         # Draw pose for visualization
#         mp_drawing.draw_landmarks(
#             frame,
#             results.pose_landmarks,
#             mp_pose.POSE_CONNECTIONS,
#             mp_drawing.DrawingSpec(color=(0,255,0), thickness=2),
#             mp_drawing.DrawingSpec(color=(0,0,255), thickness=2)
#         )

#         # Convert relevant landmarks to pixel + dict
#         sh = lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
#         ear = lm[mp_pose.PoseLandmark.LEFT_EAR.value]
#         hip = lm[mp_pose.PoseLandmark.LEFT_HIP.value]

#         px_sh = to_pixel(sh, w, h)
#         px_ear = to_pixel(ear, w, h)
#         px_hip = to_pixel(hip, w, h)

#         live = {
#             "left_shoulder": {"x": sh.x, "y": sh.y},
#             "left_ear": {"x": ear.x, "y": ear.y},
#             "left_hip": {"x": hip.x, "y": hip.y}
#         }

#         # -------------------------
#         # DRAW AXIS LINES
#         # -------------------------
#         # neck axis (shoulder → ear)
#         cv2.line(frame, px_sh, px_ear, (0,255,255), 3)

#         # torso axis (hip → shoulder)
#         cv2.line(frame, px_hip, px_sh, (255,255,0), 3)

#         # vertical reference line (ideal posture line through hip)
#         cv2.line(frame,
#                  (px_hip[0], px_hip[1] - 200),
#                  (px_hip[0], px_hip[1] + 200),
#                  (0,255,0), 2)

#         # -------------------------
#         # ANGLES
#         # -------------------------
#         neck_angle = angle(live["left_shoulder"], live["left_ear"])
#         torso_angle = angle(live["left_hip"], live["left_shoulder"])

#         neck_diff = abs(neck_angle - baseline_neck)
#         torso_diff = abs(torso_angle - baseline_torso)

#         # -------------------------
#         # POSTURE CLASSIFICATION
#         # -------------------------
#         bad_posture = neck_diff > NECK_THRESHOLD or torso_diff > TORSO_THRESHOLD
#         color = (0,0,255) if bad_posture else (0,255,0)
#         status = "BAD" if bad_posture else "GOOD"

#         cv2.putText(frame, f"Posture: {status}", (30,50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
#         cv2.putText(frame, f"Neck Δ: {neck_diff:.1f}°", (30,100),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
#         cv2.putText(frame, f"Torso Δ: {torso_diff:.1f}°", (30,140),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)

#     else:
#         cv2.putText(frame, "NO BODY DETECTED", (30,50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 3)

#     cv2.imshow("Posture Detection Test", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()
import cv2
import mediapipe as mp
import json
import math
import time

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# -----------------------------
# Utility Functions
# -----------------------------

def angle(p1, p2):
    """Return angle between two points in degrees."""
    dx = p2["x"] - p1["x"]
    dy = p2["y"] - p1["y"]
    return math.degrees(math.atan2(dy, dx))

def load_calibration():
    with open("calibration_data.json", "r") as f:
        return json.load(f)

# -----------------------------
# Load Calibration Baselines
# -----------------------------

calib = load_calibration()

# Choose which pose to use as baseline
# Front-view → Neutral Standing
# Side-view → "Left Side Neutral Standing" or "Right Side Neutral Standing"
if "Neutral Standing" in calib:
    baseline = calib["Neutral Standing"]
elif "Left Side Neutral Standing" in calib:
    baseline = calib["Left Side Neutral Standing"]
elif "Right Side Neutral Standing" in calib:
    baseline = calib["Right Side Neutral Standing"]
else:
    raise ValueError("No valid baseline pose found in calibration JSON.")

# Compute baseline angles
baseline_neck = angle(baseline["left_shoulder"], baseline["left_ear"])
baseline_torso = angle(baseline["left_hip"], baseline["left_shoulder"])

# For front view, also record shoulder alignment
baseline_shoulders = None
if "right_shoulder" in baseline:
    baseline_shoulders = angle(baseline["left_shoulder"], baseline["right_shoulder"])

# -----------------------------
# Real-time Posture Detection
# -----------------------------

pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

        lm = {
            name: {"x": l.x, "y": l.y, "z": l.z, "visibility": l.visibility}
            for name, l in zip(baseline.keys(), results.pose_landmarks.landmark)
        }

        # Compute current posture angles
        curr_neck = angle(lm["left_shoulder"], lm["left_ear"])
        curr_torso = angle(lm["left_hip"], lm["left_shoulder"])

        neck_dev = abs(curr_neck - baseline_neck)
        torso_dev = abs(curr_torso - baseline_torso)

        # Shoulder alignment only if front view
        shoulder_dev = None
        if baseline_shoulders is not None:
            curr_shoulders = angle(lm["left_shoulder"], lm["right_shoulder"])
            shoulder_dev = abs(curr_shoulders - baseline_shoulders)

        # -----------------------------
        # Ergonomic Judgement
        # -----------------------------

        def classify(deg):
            if deg <= 10:
                return "Good"
            elif deg <= 20:
                return "Acceptable"
            else:
                return "Poor"

        neck_status = classify(neck_dev)
        torso_status = classify(torso_dev)
        shoulder_status = classify(shoulder_dev) if shoulder_dev is not None else None

        # Display results on screen
        cv2.putText(frame, f"Neck deviation: {neck_dev:.1f}°  [{neck_status}]",
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0,255,0) if neck_status=="Good" else (0,255,255) if neck_status=="Acceptable" else (0,0,255),
                    2)

        cv2.putText(frame, f"Torso deviation: {torso_dev:.1f}°  [{torso_status}]",
                    (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0,255,0) if torso_status=="Good" else (0,255,255) if torso_status=="Acceptable" else (0,0,255),
                    2)

        if shoulder_status:
            cv2.putText(frame, f"Shoulder tilt: {shoulder_dev:.1f}°  [{shoulder_status}]",
                        (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0,255,0) if shoulder_status=="Good" else (0,255,255) if shoulder_status=="Acceptable" else (0,0,255),
                        2)

    cv2.imshow("Posture Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
