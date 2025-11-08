#!/usr/bin/env python3
"""
ErgoScan Unified Calibration System

This module provides a complete calibration system that captures MediaPipe pose landmarks
and automatically processes them through the normalization system with clean terminal output.

Features:
- Interactive GUI calibration interface
- Real-time pose detection and validation
- Automatic normalization processing
- Comprehensive terminal output with named landmarks
- Clean, organized code structure

Author: ErgoScan Development Team
"""

import cv2
import mediapipe as mp
import time
import json
import tkinter as tk
from threading import Thread
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys
import traceback
from typing import Dict, List, Tuple, Optional, Any

# Import normalization module
sys.path.append(os.path.join(os.path.dirname(__file__), 'normalization'))
from data_normalizer import DataNormalizer


class CalibrationConfig:
    """Configuration constants for the calibration system."""
    
    # Pose configurations
    POSES = [
        {
            "name": "T-Pose", 
            "instruction": "Stand tall with your arms extended horizontally (like a T).",
            "tips": "Keep your arms parallel to the ground and hold steady."
        },
        {
            "name": "Neutral Standing", 
            "instruction": "Stand naturally with your arms relaxed by your sides.",
            "tips": "Let your arms hang naturally and maintain good posture."
        },
        {
            "name": "Seated Neutral", 
            "instruction": "Sit comfortably with your back straight and feet flat.",
            "tips": "Keep your feet flat on the floor and sit up straight."
        }
    ]
    
    # MediaPipe pose landmark names (33 landmarks)
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
    
    # Detection thresholds
    FULL_BODY_VISIBLE_THRESHOLD = 0.9
    FULL_BODY_HOLD_TIME = 2
    COUNTDOWN_TIME = 10
    
    # File settings
    OUTPUT_FILE = "calibration_data.json"
    NORMALIZED_OUTPUT_FILE = "normalized_calibration_data.json"
    
    # UI settings
    WINDOW_SIZE = "800x700"
    CAMERA_SIZE = (640, 480)
    
    # Colors and styling
    COLOR_PRIMARY = "#2196F3"
    COLOR_SUCCESS = "#4CAF50"
    COLOR_WARNING = "#FF9800"
    COLOR_BACKGROUND = "white"
    COLOR_TEXT = "black"


class NormalizationIntegrator:
    """Handles integration with the normalization system."""
    
    def __init__(self):
        """Initialize the normalization integrator."""
        self.normalizer = None
        
    def create_normalizer(self) -> bool:
        """
        Create and initialize the normalizer instance.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.normalizer = DataNormalizer()
            print("🔧 Created DataNormalizer instance")
            return True
        except Exception as e:
            print(f"❌ Error creating normalizer: {e}")
            return False
    
    def process_calibration_data(self, calibration_data: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Process calibration data through normalization system.
        
        Args:
            calibration_data: Dictionary containing pose data
            
        Returns:
            Dictionary containing processing results
        """
        if not self.normalizer:
            if not self.create_normalizer():
                return {"success": False, "error": "Failed to create normalizer"}
        
        print("\n" + "="*70)
        print("🎯 PROCESSING CALIBRATION DATA THROUGH NORMALIZATION SYSTEM")
        print("="*70)
        
        results = {}
        normalized_output = {}
        
        for pose_name, pose_data in calibration_data.items():
            print(f"\n{'─'*50}")
            print(f"🧍 Processing: {pose_name}")
            print(f"{'─'*50}")
            
            # Extract landmarks and names
            landmarks, landmark_names = self._extract_landmarks(pose_data)
            
            if not landmarks:
                print(f"❌ No valid landmarks found for {pose_name}")
                results[pose_name] = {"success": False, "error": "No landmarks"}
                continue
            
            # Display original pose information
            self._display_original_pose_info(pose_name, landmarks)
            
            try:
                # Normalize the landmarks
                print(f"\n🔧 Normalizing {len(landmarks)} landmarks...")
                normalized = self.normalizer.normalize_landmarks(landmarks)
                
                if normalized:
                    print(f"✅ Normalization successful!")
                    
                    # Display normalized results
                    self._display_normalized_results(pose_name, normalized, landmark_names)
                    
                    # Store results
                    results[pose_name] = {
                        "success": True,
                        "original_landmarks": landmarks,
                        "normalized_landmarks": normalized,
                        "landmark_names": landmark_names
                    }
                    
                    # Prepare normalized output for saving
                    normalized_output[pose_name] = {
                        "landmarks": [
                            {
                                "name": landmark_names[i] if i < len(landmark_names) else f"landmark_{i}",
                                "original": {"x": landmarks[i][0], "y": landmarks[i][1], "z": landmarks[i][2]},
                                "normalized": {"x": normalized[i][0], "y": normalized[i][1], "z": normalized[i][2]}
                            }
                            for i in range(len(normalized))
                        ],
                        "statistics": self._calculate_statistics(normalized)
                    }
                else:
                    print(f"❌ Normalization failed for {pose_name}")
                    results[pose_name] = {"success": False, "error": "Normalization failed"}
                    
            except Exception as e:
                print(f"❌ Error during normalization of {pose_name}: {e}")
                print(f"📝 Error details: {traceback.format_exc()}")
                results[pose_name] = {"success": False, "error": str(e)}
        
        # Save normalized results
        self._save_normalized_data(normalized_output)
        
        # Display final summary
        self._display_final_summary(results)
        
        return {"success": True, "results": results, "normalized_data": normalized_output}
    
    def _extract_landmarks(self, pose_data: Dict) -> Tuple[List[Tuple[float, float, float]], List[str]]:
        """Extract coordinates and names from pose data."""
        landmarks = []
        landmark_names = []
        
        for landmark_name, data in pose_data.items():
            if isinstance(data, dict) and 'x' in data and 'y' in data and 'z' in data:
                x, y, z = data['x'], data['y'], data['z']
                landmarks.append((x, y, z))
                landmark_names.append(landmark_name)
        
        return landmarks, landmark_names
    
    def _display_original_pose_info(self, pose_name: str, landmarks: List[Tuple[float, float, float]]):
        """Display information about the original pose."""
        print(f"📊 Original {pose_name}:")
        print(f"   • Total landmarks: {len(landmarks)}")
        
        if landmarks:
            x_coords = [pt[0] for pt in landmarks]
            y_coords = [pt[1] for pt in landmarks]
            z_coords = [pt[2] for pt in landmarks]
            
            print(f"   • X range: [{min(x_coords):.3f}, {max(x_coords):.3f}]")
            print(f"   • Y range: [{min(y_coords):.3f}, {max(y_coords):.3f}]")
            print(f"   • Z range: [{min(z_coords):.3f}, {max(z_coords):.3f}]")
    
    def _display_normalized_results(self, pose_name: str, normalized: List[Tuple[float, float, float]], 
                                  landmark_names: List[str]):
        """Display detailed normalized results."""
        print(f"\n🎯 {pose_name} - Normalized Results:")
        print(f"   • Landmarks processed: {len(normalized)}")
        
        # Calculate statistics
        x_coords = [pt[0] for pt in normalized]
        y_coords = [pt[1] for pt in normalized]
        z_coords = [pt[2] for pt in normalized]
        
        print(f"   • X range: [{min(x_coords):.3f}, {max(x_coords):.3f}]")
        print(f"   • Y range: [{min(y_coords):.3f}, {max(y_coords):.3f}]")
        print(f"   • Z range: [{min(z_coords):.3f}, {max(z_coords):.3f}]")
        
        # Center of mass (should be close to origin)
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        center_z = sum(z_coords) / len(z_coords)
        print(f"   • Center of mass: ({center_x:.3f}, {center_y:.3f}, {center_z:.3f})")
        
        # Display individual landmarks with names
        print(f"   • Individual normalized landmarks:")
        for i, (x, y, z) in enumerate(normalized):
            if i < len(landmark_names):
                name = landmark_names[i].replace('_', ' ').title()
                print(f"     {name:<20} ({x:6.3f}, {y:6.3f}, {z:6.3f})")
    
    def _calculate_statistics(self, normalized: List[Tuple[float, float, float]]) -> Dict[str, Any]:
        """Calculate statistics for normalized data."""
        if not normalized:
            return {}
        
        x_coords = [pt[0] for pt in normalized]
        y_coords = [pt[1] for pt in normalized]
        z_coords = [pt[2] for pt in normalized]
        
        return {
            "landmark_count": len(normalized),
            "x_range": [min(x_coords), max(x_coords)],
            "y_range": [min(y_coords), max(y_coords)],
            "z_range": [min(z_coords), max(z_coords)],
            "center_of_mass": [
                sum(x_coords) / len(x_coords),
                sum(y_coords) / len(y_coords),
                sum(z_coords) / len(z_coords)
            ]
        }
    
    def _save_normalized_data(self, normalized_output: Dict[str, Any]):
        """Save normalized data to file."""
        try:
            with open(CalibrationConfig.NORMALIZED_OUTPUT_FILE, 'w') as f:
                json.dump(normalized_output, f, indent=2)
            print(f"\n💾 Normalized data saved to '{CalibrationConfig.NORMALIZED_OUTPUT_FILE}'")
        except Exception as e:
            print(f"⚠️  Warning: Could not save normalized data: {e}")
    
    def _display_final_summary(self, results: Dict[str, Any]):
        """Display final processing summary."""
        print("\n" + "="*70)
        print("📊 CALIBRATION NORMALIZATION SUMMARY")
        print("="*70)
        
        successful = sum(1 for r in results.values() if r.get('success', False))
        total = len(results)
        
        print(f"\n✅ Successfully processed: {successful}/{total} poses")
        
        if successful < total:
            print(f"❌ Failed to process: {total - successful} poses")
        
        print(f"\n📋 Detailed Status:")
        for pose_name, result in results.items():
            if result.get('success', False):
                landmark_count = len(result.get('normalized_landmarks', []))
                print(f"   • {pose_name:<20} ✅ SUCCESS ({landmark_count} landmarks)")
            else:
                error = result.get('error', 'Unknown error')
                print(f"   • {pose_name:<20} ❌ FAILED ({error})")
        
        print(f"\n🏁 Calibration normalization processing completed!")


class BodyCalibrationSystem:
    """
    Main calibration system that handles GUI, pose detection, and normalization integration.
    """
    
    def __init__(self, root):
        """Initialize the calibration system."""
        self.root = root
        self.root.title("ErgoScan - Body Calibration System")
        self.root.geometry(CalibrationConfig.WINDOW_SIZE)
        self.root.configure(bg=CalibrationConfig.COLOR_BACKGROUND)
        
        # Initialize MediaPipe
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose_detector = self.mp_pose.Pose(
            min_detection_confidence=0.5, 
            min_tracking_confidence=0.5
        )
        
        # Camera and detection variables
        self.cap = None
        self.running = False
        self.current_pose_index = 0
        self.visible_start_time = None
        self.countdown_start_time = None
        self.calibration_data = {}
        
        # Initialize normalization integrator
        self.normalizer_integration = NormalizationIntegrator()
        
        # Start with instruction page
        self.show_instructions_page()
    
    def show_instructions_page(self):
        """Display the initial instructions page."""
        self.clear_window()
        
        # Title
        title = tk.Label(
            self.root,
            text="ErgoScan Body Calibration System",
            font=("Arial", 24, "bold"),
            fg=CalibrationConfig.COLOR_TEXT,
            bg=CalibrationConfig.COLOR_BACKGROUND
        )
        title.pack(pady=(30, 20))
        
        # Instructions text
        instructions = (
            "Welcome to the ErgoScan calibration system!\n\n"
            "This process will capture your body measurements using 3 poses:\n\n"
            f"🚶 {CalibrationConfig.POSES[0]['name']}: {CalibrationConfig.POSES[0]['instruction']}\n"
            f"🧍 {CalibrationConfig.POSES[1]['name']}: {CalibrationConfig.POSES[1]['instruction']}\n"
            f"🪑 {CalibrationConfig.POSES[2]['name']}: {CalibrationConfig.POSES[2]['instruction']}\n\n"
            "📋 What happens during calibration:\n"
            "• Camera detects when your full body is visible\n"
            "• 10-second countdown starts - hold your pose steady\n"
            "• Pose data is automatically captured and saved\n"
            "• Data is processed through normalization system\n"
            "• Results are displayed in the terminal\n\n"
            "📌 Requirements:\n"
            "• Well-lit environment\n"
            "• Full body visible in camera (head to toe)\n"
            "• Minimal background movement\n"
            "• Stay still during countdown"
        )
        
        instructions_label = tk.Label(
            self.root,
            text=instructions,
            font=("Arial", 12),
            fg=CalibrationConfig.COLOR_TEXT,
            bg=CalibrationConfig.COLOR_BACKGROUND,
            justify="left",
            wraplength=700
        )
        instructions_label.pack(pady=(0, 30))
        
        # Continue button
        continue_button = tk.Button(
            self.root,
            text="Start Calibration Process",
            font=("Arial", 16, "bold"),
            bg=CalibrationConfig.COLOR_PRIMARY,
            fg="white",
            width=25,
            height=2,
            command=self.show_calibration_page,
            relief="raised",
            bd=3
        )
        continue_button.pack(pady=20)
    
    def show_calibration_page(self):
        """Display the main calibration interface."""
        self.clear_window()
        
        # Title
        self.title_label = tk.Label(
            self.root,
            text="Body Calibration in Progress",
            font=("Arial", 20, "bold"),
            fg=CalibrationConfig.COLOR_TEXT,
            bg=CalibrationConfig.COLOR_BACKGROUND
        )
        self.title_label.pack(pady=(20, 10))
        
        # Video display
        self.video_label = tk.Label(
            self.root, 
            bg="black",
            width=80,
            height=30
        )
        self.video_label.pack(pady=10)
        
        # Instructions
        self.instruction_text = tk.StringVar()
        self.instruction_label = tk.Label(
            self.root,
            textvariable=self.instruction_text,
            font=("Arial", 14),
            fg=CalibrationConfig.COLOR_TEXT,
            bg=CalibrationConfig.COLOR_BACKGROUND,
            wraplength=700,
            justify="center"
        )
        self.instruction_label.pack(pady=10)
        
        # Countdown display
        self.countdown_text = tk.StringVar()
        self.countdown_label = tk.Label(
            self.root,
            textvariable=self.countdown_text,
            font=("Arial", 36, "bold"),
            fg=CalibrationConfig.COLOR_PRIMARY,
            bg=CalibrationConfig.COLOR_BACKGROUND
        )
        self.countdown_label.pack(pady=10)
        
        # Control button
        self.control_button = tk.Button(
            self.root,
            text="Begin Calibration",
            font=("Arial", 14, "bold"),
            bg=CalibrationConfig.COLOR_SUCCESS,
            fg="white",
            width=20,
            height=2,
            command=self.start_calibration,
            relief="raised",
            bd=3
        )
        self.control_button.pack(pady=20)
    
    def start_calibration(self):
        """Start the calibration process."""
        self.control_button.config(state=tk.DISABLED, text="Calibration Running...")
        self.running = True
        self.instruction_text.set("Starting camera... Position yourself so your full body is visible.")
        
        # Start camera in separate thread
        Thread(target=self.run_calibration_loop, daemon=True).start()
    
    def run_calibration_loop(self):
        """Main calibration loop that handles camera and pose detection."""
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.instruction_text.set("❌ Unable to access camera. Please check camera permissions.")
            self.control_button.config(state=tk.NORMAL, text="Retry Calibration")
            return
        
        print("\n🎥 Camera initialized successfully")
        print("🚀 Starting calibration process...")
        
        while self.running and self.current_pose_index < len(CalibrationConfig.POSES):
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Process frame for pose detection
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose_detector.process(rgb_frame)
            
            # Draw landmarks if detected
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
                )
            
            # Update video display
            self.update_video_display(frame)
            
            # Handle pose detection logic
            self.handle_pose_detection(results)
            
            # Update UI
            self.root.update()
        
        # Cleanup and finalize
        self.finalize_calibration()
    
    def update_video_display(self, frame):
        """Update the video display with current frame."""
        # Resize frame to fit display
        frame_resized = cv2.resize(frame, CalibrationConfig.CAMERA_SIZE)
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        
        # Convert to PhotoImage
        image = Image.fromarray(frame_rgb)
        photo = ImageTk.PhotoImage(image)
        
        # Update label
        self.video_label.config(image=photo)
        self.video_label.image = photo  # Keep reference
    
    def handle_pose_detection(self, results):
        """Handle pose detection logic and state management."""
        current_pose = CalibrationConfig.POSES[self.current_pose_index]
        
        # Check if landmarks are detected
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # Calculate visibility and body coverage
            avg_visibility = sum(lm.visibility for lm in landmarks) / len(landmarks)
            y_coords = [lm.y for lm in landmarks]
            full_body_in_frame = (min(y_coords) > 0.05 and max(y_coords) < 0.95)
            
            # Check if pose requirements are met
            pose_ready = (avg_visibility > CalibrationConfig.FULL_BODY_VISIBLE_THRESHOLD and 
                         full_body_in_frame)
            
            if pose_ready:
                # Start or continue countdown
                if self.visible_start_time is None:
                    self.visible_start_time = time.time()
                elif time.time() - self.visible_start_time >= CalibrationConfig.FULL_BODY_HOLD_TIME:
                    if self.countdown_start_time is None:
                        self.countdown_start_time = time.time()
                        print(f"📸 Starting {CalibrationConfig.COUNTDOWN_TIME}s countdown for {current_pose['name']}")
            else:
                # Reset timers if pose requirements not met
                self.visible_start_time = None
                self.countdown_start_time = None
        else:
            # No landmarks detected
            self.visible_start_time = None
            self.countdown_start_time = None
        
        # Handle countdown and capture
        if self.countdown_start_time:
            elapsed = time.time() - self.countdown_start_time
            remaining = int(CalibrationConfig.COUNTDOWN_TIME - elapsed)
            
            if remaining > 0:
                self.countdown_text.set(f"{remaining}")
                self.instruction_text.set(
                    f"Hold steady for {current_pose['name']}!\n"
                    f"{current_pose['instruction']}\n"
                    f"Stay still during countdown..."
                )
            else:
                # Capture pose
                self.capture_pose(results, current_pose)
        else:
            # Show positioning instructions
            self.countdown_text.set("")
            if self.current_pose_index < len(CalibrationConfig.POSES):
                self.instruction_text.set(
                    f"Position for {current_pose['name']}:\n"
                    f"{current_pose['instruction']}\n"
                    f"Ensure your full body is visible in the camera."
                )
    
    def capture_pose(self, results, pose_config):
        """Capture and save pose landmarks."""
        print(f"📸 Capturing {pose_config['name']}...")
        
        # Create labeled landmarks dictionary
        labeled_landmarks = {}
        for i, landmark in enumerate(results.pose_landmarks.landmark):
            if i < len(CalibrationConfig.POSE_LANDMARKS):
                labeled_landmarks[CalibrationConfig.POSE_LANDMARKS[i]] = {
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z,
                    "visibility": landmark.visibility
                }
        
        # Save pose data
        self.calibration_data[pose_config['name']] = labeled_landmarks
        
        # Save to file immediately
        with open(CalibrationConfig.OUTPUT_FILE, "w") as f:
            json.dump(self.calibration_data, f, indent=2)
        
        print(f"✅ {pose_config['name']} captured and saved ({len(labeled_landmarks)} landmarks)")
        
        # Move to next pose
        self.current_pose_index += 1
        self.visible_start_time = None
        self.countdown_start_time = None
        self.countdown_text.set("")
        
        # Update instruction for next pose or completion
        if self.current_pose_index < len(CalibrationConfig.POSES):
            next_pose = CalibrationConfig.POSES[self.current_pose_index]
            self.instruction_text.set(
                f"✅ {pose_config['name']} captured!\n\n"
                f"Prepare for {next_pose['name']}:\n"
                f"{next_pose['instruction']}"
            )
            print(f"🔄 Moving to next pose: {next_pose['name']}")
        else:
            self.instruction_text.set("🎉 All poses captured! Processing data...")
    
    def finalize_calibration(self):
        """Finalize calibration and process results."""
        print("\n🏁 Calibration capture completed!")
        
        # Stop camera
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Clear video display
        self.video_label.config(image="")
        
        # Update UI
        self.instruction_text.set("Calibration complete! Processing normalization...")
        self.countdown_text.set("")
        
        # Process through normalization system
        try:
            print(f"\n📊 Processing {len(self.calibration_data)} poses through normalization...")
            results = self.normalizer_integration.process_calibration_data(self.calibration_data)
            
            if results.get("success", False):
                self.instruction_text.set(
                    "🎉 Calibration and normalization completed successfully!\n"
                    "Check the terminal for detailed results."
                )
                messagebox.showinfo(
                    "Calibration Complete", 
                    f"Calibration finished successfully!\n\n"
                    f"• Raw data saved to: {CalibrationConfig.OUTPUT_FILE}\n"
                    f"• Normalized data saved to: {CalibrationConfig.NORMALIZED_OUTPUT_FILE}\n"
                    f"• Detailed results displayed in terminal\n\n"
                    f"Poses captured: {len(self.calibration_data)}"
                )
            else:
                error_msg = results.get("error", "Unknown error")
                self.instruction_text.set(f"❌ Processing failed: {error_msg}")
                messagebox.showerror("Processing Error", f"Normalization failed: {error_msg}")
                
        except Exception as e:
            error_msg = f"Error during processing: {str(e)}"
            print(f"❌ {error_msg}")
            self.instruction_text.set(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)
        
        # Re-enable control button
        self.control_button.config(
            state=tk.NORMAL, 
            text="Start New Calibration",
            command=self.reset_calibration
        )
    
    def reset_calibration(self):
        """Reset calibration for a new session."""
        self.current_pose_index = 0
        self.visible_start_time = None
        self.countdown_start_time = None
        self.calibration_data = {}
        
        # Reset UI
        self.control_button.config(text="Begin Calibration", command=self.start_calibration)
        self.instruction_text.set("Ready to start new calibration session.")
        self.countdown_text.set("")
        
        print("\n🔄 Calibration system reset - ready for new session")
    
    def clear_window(self):
        """Clear all widgets from the window."""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def cleanup(self):
        """Clean up resources when closing."""
        self.running = False
        if self.cap:
            self.cap.release()
        if hasattr(self, 'pose_detector'):
            self.pose_detector.close()


def load_and_process_existing_data():
    """
    Load and process existing calibration data (standalone mode).
    """
    print("🎯 ErgoScan Calibration Data Processor")
    print("="*50)
    
    # Check if calibration data exists
    if not os.path.exists(CalibrationConfig.OUTPUT_FILE):
        print(f"❌ No calibration data found at '{CalibrationConfig.OUTPUT_FILE}'")
        print("Please run the calibration system first to capture pose data.")
        return False
    
    # Load existing data
    try:
        with open(CalibrationConfig.OUTPUT_FILE, 'r') as f:
            calibration_data = json.load(f)
        
        print(f"✅ Loaded calibration data with {len(calibration_data)} poses")
        
        # Process through normalization
        integrator = NormalizationIntegrator()
        results = integrator.process_calibration_data(calibration_data)
        
        if results.get("success", False):
            print(f"\n🎉 Processing completed successfully!")
            return True
        else:
            error_msg = results.get("error", "Unknown error")
            print(f"❌ Processing failed: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Error loading calibration data: {e}")
        return False


def main():
    """Main function to run the calibration system."""
    print("🎯 ErgoScan Unified Calibration System")
    print("="*50)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--process-existing' or sys.argv[1] == '-p':
            # Process existing data mode
            load_and_process_existing_data()
            return
        elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("Usage:")
            print("  python calibration_integration.py              # Run full calibration system")
            print("  python calibration_integration.py -p           # Process existing calibration data")
            print("  python calibration_integration.py --help       # Show this help")
            return
    
    # Normal GUI mode
    print("Starting calibration interface...")
    
    root = tk.Tk()
    app = BodyCalibrationSystem(root)
    
    # Handle window closing
    def on_closing():
        app.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n⚠️  Calibration interrupted by user")
        on_closing()


if __name__ == "__main__":
    main()