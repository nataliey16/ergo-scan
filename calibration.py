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

# ---------------------------
# POSE DEFINITIONS
# ---------------------------

FRONT_VIEW_POSES = [
    {"name": "T-Pose", "instruction": "Stand tall with your arms extended horizontally (like a T)."},
    {"name": "Neutral Standing", "instruction": "Stand naturally with your arms relaxed by your sides."},
    {"name": "Seated Neutral", "instruction": "Sit comfortably with your back straight and feet flat."}
]

LEFT_SIDE_VIEW_POSES = [
    {
        "name": "Left Side Neutral Standing",
        "instruction": "Stand sideways to the camera with your LEFT side facing it. Keep arms relaxed and posture natural."
    },
    {
        "name": "Left Side Seated Neutral",
        "instruction": "Sit sideways to the camera with your LEFT side facing it, back straight, and feet flat on the floor."
    }
]

RIGHT_SIDE_VIEW_POSES = [
    {
        "name": "Right Side Neutral Standing",
        "instruction": "Stand sideways to the camera with your RIGHT side facing it. Keep arms relaxed and posture natural."
    },
    {
        "name": "Right Side Seated Neutral",
        "instruction": "Sit sideways to the camera with your RIGHT side facing it, back straight, and feet flat on the floor."
    }
]

# MediaPipe pose landmark names
POSE_LANDMARKS = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer", "right_eye_inner", "right_eye",
    "right_eye_outer", "left_ear", "right_ear", "mouth_left", "mouth_right",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_pinky", "right_pinky",
    "left_index", "right_index", "left_thumb", "right_thumb",
    "left_hip", "right_hip", "left_knee", "right_knee",
    "left_ankle", "right_ankle", "left_heel", "right_heel",
    "left_foot_index", "right_foot_index"
]

FULL_BODY_VISIBLE_THRESHOLD = 0.9    # used for front view mode
FULL_BODY_HOLD_TIME = 2
COUNTDOWN_TIME = 10
OUTPUT_FILE = "calibration_data.json"


class BodyCalibrationInstructions:
    def __init__(self, root):
        self.root = root
        self.root.title("Ergo Scan Body Calibration")
        self.root.geometry("800x750")
        self.root.configure(bg="white")

        # Pose detection setup
        self.cap = None
        self.pose_detector = mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.running = False
        self.current_pose_index = 0
        self.visible_start_time = None
        self.countdown_start_time = None
        self.calibration_data = {}

        # Current pose list (changes depending on mode)
        self.poses = FRONT_VIEW_POSES.copy()

        # Mode: front / left_side / right_side
        self.mode = tk.StringVar(value="front")

        # Start with instruction page
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
        title.pack(pady=(30, 10))

        info_text = (
            "Before we begin, here’s what will happen:\n\n"
            "Default (Front View Calibration):\n"
            "  • T-Pose – arms extended horizontally\n"
            "  • Neutral Standing – arms relaxed at your sides\n"
            "  • Seated Neutral – sitting upright, feet flat\n\n"
            "Side View Calibration (Left/Right):\n"
            "  • Side Neutral Standing – sideways to the camera\n"
            "  • Side Seated Neutral – seated sideways to the camera\n\n"
            "The camera will automatically detect when your body is clearly visible.\n"
            "Once detected, a 10-second countdown will start — stay still during this time.\n"
            "Calibration data for each pose will be saved automatically.\n\n"
            "Please ensure:\n"
            "  • You are in a well-lit space.\n"
            "  • Your body fits in the camera view.\n"
            "  • There is minimal background movement.\n"
        )

        label = tk.Label(
            self.root,
            text=info_text,
            font=("Arial", 13),
            fg="black",
            bg="white",
            justify="left",
            wraplength=740
        )
        label.pack(pady=(0, 10))

        # Mode selection
        mode_frame = tk.Frame(self.root, bg="white")
        mode_frame.pack(pady=(10, 10))

        mode_label = tk.Label(
            mode_frame,
            text="Select Camera Position / Calibration Mode:",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="black"
        )
        mode_label.pack(anchor="w", pady=(0, 5))

        rb_frame = tk.Frame(mode_frame, bg="white")
        rb_frame.pack()

        tk.Radiobutton(
            rb_frame,
            text="Front View (camera in front)",
            font=("Arial", 13),
            variable=self.mode,
            value="front",
            bg="white",
            anchor="w"
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            rb_frame,
            text="Left Side View (camera on your left)",
            font=("Arial", 13),
            variable=self.mode,
            value="left_side",
            bg="white",
            anchor="w"
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            rb_frame,
            text="Right Side View (camera on your right)",
            font=("Arial", 13),
            variable=self.mode,
            value="right_side",
            bg="white",
            anchor="w"
        ).pack(side="left", padx=5)

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
        start_button.pack(pady=(20, 20))

    # ---------------------------
    # CALIBRATION PAGE
    # ---------------------------
    def show_calibration_page(self):
        self.clear_window()

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

        self.video_label = tk.Label(self.root, bg="black")
        self.video_label.pack(pady=10)

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

        self.countdown_text = tk.StringVar()
        self.countdown_label = tk.Label(
            self.root,
            textvariable=self.countdown_text,
            font=("Arial", 32, "bold"),
            fg="black",
            bg="white"
        )
        self.countdown_label.pack(pady=5)

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
        # Select pose set based on calibration mode
        mode = self.mode.get()
        if mode == "front":
            self.poses = FRONT_VIEW_POSES
        elif mode == "left_side":
            self.poses = LEFT_SIDE_VIEW_POSES
        elif mode == "right_side":
            self.poses = RIGHT_SIDE_VIEW_POSES
        else:
            # fallback to front
            self.poses = FRONT_VIEW_POSES

        # Reset state
        self.current_pose_index = 0
        self.visible_start_time = None
        self.countdown_start_time = None
        # Keep existing calibration_data so multiple runs can append, or reset if you prefer:
        # self.calibration_data = {}

        self.start_button.config(state=tk.DISABLED)
        self.running = True
        self.instruction_text.set(
            "Position yourself so your entire body (for this view) is clearly visible."
        )
        Thread(target=self.run_camera, daemon=True).start()

    # ---------------------------
    # CAMERA LOOP
    # ---------------------------
    def run_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.instruction_text.set("Unable to access camera.")
            return

        while self.running and self.current_pose_index < len(self.poses):
            ret, frame = self.cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose_detector.process(rgb_frame)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                )

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (640, 480))
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

            mode = self.mode.get()

            # Visibility check
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                ys = [lm.y for lm in landmarks]
                full_body_in_frame = (min(ys) > 0 and max(ys) < 1)

                condition_ok = False

                if mode == "front":
                    # Original logic: high average visibility + full body in frame
                    avg_visibility = sum(lm.visibility for lm in landmarks) / len(landmarks)
                    condition_ok = avg_visibility > FULL_BODY_VISIBLE_THRESHOLD and full_body_in_frame
                else:
                    # Side modes: use a more forgiving rule
                    # Require at least N landmarks with good visibility
                    visible_landmarks = [lm for lm in landmarks if lm.visibility > 0.7]
                    condition_ok = len(visible_landmarks) >= 12 and full_body_in_frame

                if condition_ok:
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

            # Countdown
            if self.countdown_start_time:
                elapsed = time.time() - self.countdown_start_time
                remaining = int(COUNTDOWN_TIME - elapsed)
                if remaining > 0:
                    self.countdown_text.set(f"{remaining}s")
                    self.instruction_text.set(
                        f"Hold still for {self.poses[self.current_pose_index]['name']}:\n"
                        f"{self.poses[self.current_pose_index]['instruction']}"
                    )
                else:
                    # Save pose landmarks with names
                    labeled_landmarks = {
                        POSE_LANDMARKS[i]: {
                            "x": lm.x,
                            "y": lm.y,
                            "z": lm.z,
                            "visibility": lm.visibility
                        }
                        for i, lm in enumerate(results.pose_landmarks.landmark)
                        if i < len(POSE_LANDMARKS)
                    }

                    pose_name = self.poses[self.current_pose_index]['name']
                    self.calibration_data[pose_name] = labeled_landmarks

                    with open(OUTPUT_FILE, "w") as f:
                        json.dump(self.calibration_data, f, indent=4)

                    # Move to next pose
                    self.current_pose_index += 1
                    self.visible_start_time = None
                    self.countdown_start_time = None
                    self.countdown_text.set("")

                    if self.current_pose_index < len(self.poses):
                        self.instruction_text.set(
                            f"Prepare for {self.poses[self.current_pose_index]['name']}:\n"
                            f"{self.poses[self.current_pose_index]['instruction']}"
                        )
                    continue

            # Default instruction while waiting
            if not self.countdown_start_time and self.current_pose_index < len(self.poses):
                self.instruction_text.set(
                    f"Position yourself for {self.poses[self.current_pose_index]['name']}:\n"
                    f"{self.poses[self.current_pose_index]['instruction']}\n"
                    f"Ensure your body is clearly visible for this camera view."
                )

            self.root.update()

        # End calibration
        self.running = False
        if self.cap:
            self.cap.release()

        self.video_label.configure(image='')
        self.instruction_text.set("Calibration complete! All poses captured.")
        self.countdown_text.set("")
        
        # Process calibration data through normalization system
        self.process_calibration_with_normalization()
        
        messagebox.showinfo("Calibration Done", f"Calibration complete. Data saved to {OUTPUT_FILE}.\nNormalized results displayed in terminal.")
        self.start_button.config(state=tk.NORMAL)

    def process_calibration_with_normalization(self):
        """Process the completed calibration data through the normalization system."""
        try:
            # Import the integration components
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), 'normalization'))
            from data_normalizer import DataNormalizer
            
            print("\n" + "="*60)
            print("🎯 PROCESSING CALIBRATION DATA THROUGH NORMALIZATION")
            print("="*60)
            
            # Create normalizer instance
            normalizer = DataNormalizer()
            print("🔧 Created DataNormalizer instance")
            
            # Process each pose
            for pose_name, pose_data in self.calibration_data.items():
                print(f"\n{'─'*40}")
                print(f"🧍 Processing: {pose_name}")
                print(f"{'─'*40}")
                
                # Extract landmarks and names
                landmarks = []
                landmark_names = []
                
                for landmark_name, data in pose_data.items():
                    if 'x' in data and 'y' in data and 'z' in data:
                        x, y, z = data['x'], data['y'], data['z']
                        landmarks.append((x, y, z))
                        landmark_names.append(landmark_name)
                
                if landmarks:
                    print(f"📊 Original {pose_name}: {len(landmarks)} landmarks")
                    
                    # Calculate original ranges
                    x_coords = [pt[0] for pt in landmarks]
                    y_coords = [pt[1] for pt in landmarks]
                    z_coords = [pt[2] for pt in landmarks]
                    
                    print(f"   • X range: [{min(x_coords):.3f}, {max(x_coords):.3f}]")
                    print(f"   • Y range: [{min(y_coords):.3f}, {max(y_coords):.3f}]")
                    print(f"   • Z range: [{min(z_coords):.3f}, {max(z_coords):.3f}]")
                    
                    # Normalize the landmarks
                    print(f"\n🔧 Normalizing {len(landmarks)} landmarks...")
                    normalized = normalizer.normalize_landmarks(landmarks)
                    
                    if normalized:
                        print(f"✅ Normalization successful!")
                        
                        # Display normalized results
                        print(f"\n🎯 {pose_name} - Normalized Results:")
                        print(f"   • Landmarks processed: {len(normalized)}")
                        
                        # Calculate normalized statistics
                        norm_x = [pt[0] for pt in normalized]
                        norm_y = [pt[1] for pt in normalized]
                        norm_z = [pt[2] for pt in normalized]
                        
                        print(f"   • X range: [{min(norm_x):.3f}, {max(norm_x):.3f}]")
                        print(f"   • Y range: [{min(norm_y):.3f}, {max(norm_y):.3f}]")
                        print(f"   • Z range: [{min(norm_z):.3f}, {max(norm_z):.3f}]")
                        
                        # Calculate and display center of mass
                        center_x = sum(norm_x) / len(norm_x)
                        center_y = sum(norm_y) / len(norm_y)
                        center_z = sum(norm_z) / len(norm_z)
                        print(f"   • Center of mass: ({center_x:.3f}, {center_y:.3f}, {center_z:.3f})")
                        
                        # Display individual landmarks with names
                        print("   • Individual normalized landmarks:")
                        for i, (x, y, z) in enumerate(normalized):
                            if i < len(landmark_names):
                                name = landmark_names[i]
                                formatted_name = name.replace('_', ' ').title()
                                print(f"     {formatted_name:<20} ({x:6.3f}, {y:6.3f}, {z:6.3f})")
                    else:
                        print(f"❌ Normalization failed for {pose_name}")
                else:
                    print(f"❌ No valid landmarks found for {pose_name}")
            
            print(f"\n🏁 Calibration normalization processing completed!")
            
        except Exception as e:
            print(f"❌ Error processing calibration data: {e}")
            import traceback
            print(f"📝 Error details: {traceback.format_exc()}")

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


# Run the Tkinter app
if __name__ == "__main__":
    root = tk.Tk()
    app = BodyCalibrationInstructions(root)
    root.mainloop()
