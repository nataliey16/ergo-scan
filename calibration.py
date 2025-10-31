# import cv2
# import mediapipe as mp
# import time
# import json
# import tkinter as tk
# from threading import Thread
# from tkinter import messagebox
# from PIL import Image, ImageTk

# # Initialize MediaPipe Pose
# mp_drawing = mp.solutions.drawing_utils
# mp_pose = mp.solutions.pose

# POSES = [
#     {"name": "T-Pose", "instruction": "Stand tall with your arms extended horizontally (like a T)."},
#     {"name": "Neutral Standing", "instruction": "Stand naturally with your arms relaxed by your sides."},
#     {"name": "Seated Neutral", "instruction": "Sit comfortably with your back straight and feet flat."}
# ]

# FULL_BODY_VISIBLE_THRESHOLD = 0.9  # % of keypoints visible
# FULL_BODY_HOLD_TIME = 2            # seconds to hold full body visibility
# COUNTDOWN_TIME = 10                # seconds countdown for scanning
# OUTPUT_FILE = "calibration_data.json"


# class BodyCalibrationInstructions:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Body Calibration Instructions")
#         self.root.geometry("800x700")
#         self.root.configure(bg="white")

#         # Title at the top
#         self.title_label = tk.Label(
#             root,
#             text="Ergo Scan Body Calibration",
#             font=("Arial", 20, "bold"),
#             fg="black",
#             bg="white",
#             wraplength=700,
#             justify="center"
#         )
#         self.title_label.pack(side="top", pady=(10, 0))

#         # Video feed
#         self.video_label = tk.Label(root, bg="black")
#         self.video_label.pack(pady=10)

#         # Instructions
#         self.instruction_text = tk.StringVar()
#         self.instruction_label = tk.Label(
#             root,
#             textvariable=self.instruction_text,
#             font=("Arial", 16),
#             fg="black",
#             bg="white",
#             wraplength=700,
#             justify="center"
#         )
#         self.instruction_label.pack(pady=5)

#         # Countdown
#         self.countdown_text = tk.StringVar()
#         self.countdown_label = tk.Label(
#             root,
#             textvariable=self.countdown_text,
#             font=("Arial", 32, "bold"),
#             fg="black",
#             bg="white"
#         )
#         self.countdown_label.pack(pady=5)

#         # Start button
#         self.start_button = tk.Button(
#             root,
#             text="Start Calibration",
#             font=("Arial", 14),
#             bg="#2196F3",
#             fg="white",
#             width=20,
#             height=2,
#             command=self.start_calibration
#         )
#         self.start_button.pack(pady=20)

#         # Pose detection setup
#         self.cap = None
#         self.pose_detector = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
#         self.running = False
#         self.current_pose_index = 0
#         self.visible_start_time = None
#         self.countdown_start_time = None
#         self.calibration_data = {}

#     def start_calibration(self):
#         self.start_button.config(state=tk.DISABLED)
#         self.running = True
#         self.instruction_text.set("Position yourself so your entire body (head to toe) is visible.")
#         Thread(target=self.run_camera, daemon=True).start()

#     def run_camera(self):
#         self.cap = cv2.VideoCapture(0)
#         if not self.cap.isOpened():
#             self.instruction_text.set("Unable to access camera.")
#             return

#         while self.running and self.current_pose_index < len(POSES):
#             ret, frame = self.cap.read()
#             if not ret:
#                 continue

#             frame = cv2.flip(frame, 1)
#             rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             results = self.pose_detector.process(rgb_frame)

#             # Draw landmarks if detected
#             if results.pose_landmarks:
#                 mp_drawing.draw_landmarks(
#                     frame,
#                     results.pose_landmarks,
#                     mp_pose.POSE_CONNECTIONS,
#                     mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
#                     mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
#                 )

#             # Convert to ImageTk for Tkinter display
#             img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             img = cv2.resize(img, (640, 480))
#             imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
#             self.video_label.imgtk = imgtk
#             self.video_label.configure(image=imgtk)

#             # Check full body visibility
#             if results.pose_landmarks:
#                 landmarks = results.pose_landmarks.landmark
#                 avg_visibility = sum(lm.visibility for lm in landmarks) / len(landmarks)
#                 ys = [lm.y for lm in landmarks]
#                 full_body_in_frame = (min(ys) > 0 and max(ys) < 1)

#                 if avg_visibility > FULL_BODY_VISIBLE_THRESHOLD and full_body_in_frame:
#                     if self.visible_start_time is None:
#                         self.visible_start_time = time.time()
#                     elif time.time() - self.visible_start_time >= FULL_BODY_HOLD_TIME:
#                         if self.countdown_start_time is None:
#                             self.countdown_start_time = time.time()
#                 else:
#                     self.visible_start_time = None
#                     self.countdown_start_time = None
#             else:
#                 self.visible_start_time = None
#                 self.countdown_start_time = None

#             # Countdown and data capture
#             if self.countdown_start_time:
#                 elapsed = time.time() - self.countdown_start_time
#                 remaining = int(COUNTDOWN_TIME - elapsed)
#                 if remaining > 0:
#                     self.countdown_text.set(f"{remaining}s")
#                     self.instruction_text.set(
#                         f"Hold still for {POSES[self.current_pose_index]['name']}:\n"
#                         f"{POSES[self.current_pose_index]['instruction']}"
#                     )
#                 else:
#                     # Save pose data
#                     landmarks_data = [
#                         {"x": lm.x, "y": lm.y, "z": lm.z, "visibility": lm.visibility}
#                         for lm in results.pose_landmarks.landmark
#                     ]
#                     self.calibration_data[POSES[self.current_pose_index]['name']] = landmarks_data

#                     with open(OUTPUT_FILE, "w") as f:
#                         json.dump(self.calibration_data, f, indent=4)

#                     # Move to next pose
#                     self.current_pose_index += 1
#                     self.visible_start_time = None
#                     self.countdown_start_time = None
#                     self.countdown_text.set("")

#                     if self.current_pose_index < len(POSES):
#                         self.instruction_text.set(
#                             f"Prepare for {POSES[self.current_pose_index]['name']}:\n"
#                             f"{POSES[self.current_pose_index]['instruction']}"
#                         )
#                     continue

#             # Update instructions
#             if not self.countdown_start_time and self.current_pose_index < len(POSES):
#                 self.instruction_text.set(
#                     f"Position yourself for {POSES[self.current_pose_index]['name']}:\n"
#                     f"{POSES[self.current_pose_index]['instruction']}\n"
#                     f"Ensure your full body is visible."
#                 )

#             self.root.update()

#         # Calibration done
#         self.running = False
#         if self.cap:
#             self.cap.release()

#         self.video_label.configure(image='')
#         self.instruction_text.set("✅ Calibration complete! All poses captured.")
#         self.countdown_text.set("")
#         messagebox.showinfo("Calibration Done", f"Calibration complete. Data saved to {OUTPUT_FILE}.")
#         self.start_button.config(state=tk.NORMAL)


# # Run the Tkinter app
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = BodyCalibrationInstructions(root)
#     root.mainloop()
import cv2
import mediapipe as mp
import time
import json
import tkinter as tk
from threading import Thread
from tkinter import messagebox
from PIL import Image, ImageTk

# Initialize MediaPipe Pose
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

POSES = [
    {"name": "T-Pose", "instruction": "Stand tall with your arms extended horizontally (like a T)."},
    {"name": "Neutral Standing", "instruction": "Stand naturally with your arms relaxed by your sides."},
    {"name": "Seated Neutral", "instruction": "Sit comfortably with your back straight and feet flat."}
]

FULL_BODY_VISIBLE_THRESHOLD = 0.9
FULL_BODY_HOLD_TIME = 2
COUNTDOWN_TIME = 10
OUTPUT_FILE = "calibration_data.json"


class BodyCalibrationInstructions:
    def __init__(self, root):
        self.root = root
        self.root.title("Ergo Scan Body Calibration")
        self.root.geometry("800x700")
        self.root.configure(bg="white")

        # Store pose detection setup variables
        self.cap = None
        self.pose_detector = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.running = False
        self.current_pose_index = 0
        self.visible_start_time = None
        self.countdown_start_time = None
        self.calibration_data = {}

        # Initialize first page (pre-calibration instructions)
        self.show_instructions_page()

    # ---------------------------
    # PRE-CALIBRATION PAGE
    # ---------------------------
    def show_instructions_page(self):
        self.clear_window()

        title = tk.Label(
            self.root,
            text="Welcome to Ergo Scan Calibration",
            font=("Arial", 22, "bold"),
            fg="black",
            bg="white"
        )
        title.pack(pady=(40, 20))

        info_text = (
            "Before we begin, here’s what will happen:\n\n"
            "You’ll go through 3 calibration poses:\n"
            "   • T-Pose – arms extended horizontally\n"
            "   • Neutral Standing – arms relaxed at your sides\n"
            "   • Seated Neutral – sitting upright, feet flat\n\n"
            "The camera will automatically detect when your full body is visible.\n\n"
            "Once detected, a 10-second countdown will start — stay still during this time.\n\n"
            "Calibration data for each pose will be saved automatically.\n\n"
            " Please ensure:\n"
            "   • You are in a well-lit space.\n"
            "   • Your full body (head to toe) fits in the camera view.\n"
            "   • There is minimal background movement.\n"
        )

        label = tk.Label(
            self.root,
            text=info_text,
            font=("Arial", 14),
            fg="black",
            bg="white",
            justify="left",
            wraplength=700
        )
        label.pack(pady=(0, 20))

        start_button = tk.Button(
            self.root,
            text="Continue to Calibration",
            font=("Arial", 16),
            bg="#2196F3",
            fg="white",
            width=25,
            height=2,
            command=self.show_calibration_page
        )
        start_button.pack(pady=(30, 20))

    # ---------------------------
    # CALIBRATION PAGE
    # ---------------------------
    def show_calibration_page(self):
        self.clear_window()

        # Title
        self.title_label = tk.Label(
            self.root,
            text="Ergo Scan Body Calibration",
            font=("Arial", 20, "bold"),
            fg="black",
            bg="white",
            wraplength=700,
            justify="center"
        )
        self.title_label.pack(side="top", pady=(20, 0))

        # Video feed
        self.video_label = tk.Label(self.root, bg="black")
        self.video_label.pack(pady=10)

        # Instruction label
        self.instruction_text = tk.StringVar()
        self.instruction_label = tk.Label(
            self.root,
            textvariable=self.instruction_text,
            font=("Arial", 16),
            fg="black",
            bg="white",
            wraplength=700,
            justify="center"
        )
        self.instruction_label.pack(pady=5)

        # Countdown label
        self.countdown_text = tk.StringVar()
        self.countdown_label = tk.Label(
            self.root,
            textvariable=self.countdown_text,
            font=("Arial", 32, "bold"),
            fg="black",
            bg="white"
        )
        self.countdown_label.pack(pady=5)

        # Start button
        self.start_button = tk.Button(
            self.root,
            text="Start Calibration",
            font=("Arial", 14),
            bg="#2196F3",
            fg="white",
            width=20,
            height=2,
            command=self.start_calibration
        )
        self.start_button.pack(pady=20)

    def start_calibration(self):
        self.start_button.config(state=tk.DISABLED)
        self.running = True
        self.instruction_text.set("Position yourself so your entire body (head to toe) is visible.")
        Thread(target=self.run_camera, daemon=True).start()

    # ---------------------------
    # CAMERA CALIBRATION LOOP
    # ---------------------------
    def run_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.instruction_text.set("Unable to access camera.")
            return

        while self.running and self.current_pose_index < len(POSES):
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose_detector.process(rgb_frame)

            # Draw pose landmarks
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                )

            # Convert to ImageTk
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (640, 480))
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

            # Check if full body is visible
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                avg_visibility = sum(lm.visibility for lm in landmarks) / len(landmarks)
                ys = [lm.y for lm in landmarks]
                full_body_in_frame = (min(ys) > 0 and max(ys) < 1)

                if avg_visibility > FULL_BODY_VISIBLE_THRESHOLD and full_body_in_frame:
                    if self.visible_start_time is None:
                        self.visible_start_time = time.time()
                    elif time.time() - self.visible_start_time >= FULL_BODY_HOLD_TIME:
                        if self.countdown_start_time is None:
                            self.countdown_start_time = time.time()
                else:
                    self.visible_start_time = None
                    self.countdown_start_time = None
            else:
                self.visible_start_time = None
                self.countdown_start_time = None

            # Countdown + Capture
            if self.countdown_start_time:
                elapsed = time.time() - self.countdown_start_time
                remaining = int(COUNTDOWN_TIME - elapsed)
                if remaining > 0:
                    self.countdown_text.set(f"{remaining}s")
                    self.instruction_text.set(
                        f"Hold still for {POSES[self.current_pose_index]['name']}:\n"
                        f"{POSES[self.current_pose_index]['instruction']}"
                    )
                else:
                    # Save pose landmarks
                    landmarks_data = [
                        {"x": lm.x, "y": lm.y, "z": lm.z, "visibility": lm.visibility}
                        for lm in results.pose_landmarks.landmark
                    ]
                    self.calibration_data[POSES[self.current_pose_index]['name']] = landmarks_data
                    with open(OUTPUT_FILE, "w") as f:
                        json.dump(self.calibration_data, f, indent=4)

                    # Next pose
                    self.current_pose_index += 1
                    self.visible_start_time = None
                    self.countdown_start_time = None
                    self.countdown_text.set("")

                    if self.current_pose_index < len(POSES):
                        self.instruction_text.set(
                            f"Prepare for {POSES[self.current_pose_index]['name']}:\n"
                            f"{POSES[self.current_pose_index]['instruction']}"
                        )
                    continue

            # Update instructions
            if not self.countdown_start_time and self.current_pose_index < len(POSES):
                self.instruction_text.set(
                    f"Position yourself for {POSES[self.current_pose_index]['name']}:\n"
                    f"{POSES[self.current_pose_index]['instruction']}\n"
                    f"Ensure your full body is visible."
                )

            self.root.update()

        # Finish
        self.running = False
        if self.cap:
            self.cap.release()

        self.video_label.configure(image='')
        self.instruction_text.set("Calibration complete! All poses captured.")
        self.countdown_text.set("")
        messagebox.showinfo("Calibration Done", f"Calibration complete. Data saved to {OUTPUT_FILE}.")
        self.start_button.config(state=tk.NORMAL)

    # Utility: clear the window before switching views
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


# Run the Tkinter app
if __name__ == "__main__":
    root = tk.Tk()
    app = CalibrationApp(root)
    root.mainloop()
