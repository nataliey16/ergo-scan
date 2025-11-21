"""
Integration module for Data Normalization & Refinement
Connects the data normalizer with existing ErgoScan calibration and scanning systems
"""

import cv2
import numpy as np
import time
from typing import List, Dict, Tuple, Optional
from .data_normalizer import DataNormalizer, MeasurementPoint, BodyProfile
import json

# Try to import MediaPipe for pose detection
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("MediaPipe not available. Using basic measurements.")

class ErgoScanProcessor:
    """Enhanced ErgoScan processor with data normalization integration"""
    
    def __init__(self):
        self.normalizer = DataNormalizer()
        self.measurement_buffer = []
        self.frame_count = 0
        self.scanning_active = False
        
        # Initialize MediaPipe if available
        if MEDIAPIPE_AVAILABLE:
            self.mp_pose = mp.solutions.pose
            self.mp_draw = mp.solutions.drawing_utils
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                smooth_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
    
    def extract_measurements_from_landmarks(self, landmarks, frame_shape: Tuple[int, int], 
                                          depth_map: np.ndarray = None) -> List[MeasurementPoint]:
        """Extract measurements from MediaPipe landmarks"""
        measurements = []
        
        if not landmarks or not MEDIAPIPE_AVAILABLE:
            return measurements
        
        height, width = frame_shape[:2]
        timestamp = time.time()
        
        # Convert normalized coordinates to pixel coordinates
        def get_pixel_coords(landmark):
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            return x, y
        
        try:
            # Key landmarks
            nose = landmarks[self.mp_pose.PoseLandmark.NOSE.value]
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
            left_elbow = landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value]
            right_elbow = landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value]
            left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
            right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value]
            left_knee = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value]
            right_knee = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value]
            left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value]
            right_ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value]
            
            # Convert to pixel coordinates
            nose_px = get_pixel_coords(nose)
            left_shoulder_px = get_pixel_coords(left_shoulder)
            right_shoulder_px = get_pixel_coords(right_shoulder)
            left_hip_px = get_pixel_coords(left_hip)
            right_hip_px = get_pixel_coords(right_hip)
            left_elbow_px = get_pixel_coords(left_elbow)
            right_elbow_px = get_pixel_coords(right_elbow)
            left_wrist_px = get_pixel_coords(left_wrist)
            right_wrist_px = get_pixel_coords(right_wrist)
            left_knee_px = get_pixel_coords(left_knee)
            right_knee_px = get_pixel_coords(right_knee)
            left_ankle_px = get_pixel_coords(left_ankle)
            right_ankle_px = get_pixel_coords(right_ankle)
            
            # Calculate measurements in pixels
            
            # 1. Height (nose to average of ankles)
            ankle_avg_y = (left_ankle_px[1] + right_ankle_px[1]) / 2
            height_px = abs(nose_px[1] - ankle_avg_y)
            
            # 2. Shoulder width
            shoulder_width_px = np.sqrt((left_shoulder_px[0] - right_shoulder_px[0])**2 + 
                                       (left_shoulder_px[1] - right_shoulder_px[1])**2)
            
            # 3. Torso length (shoulder to hip)
            shoulder_center_y = (left_shoulder_px[1] + right_shoulder_px[1]) / 2
            hip_center_y = (left_hip_px[1] + right_hip_px[1]) / 2
            torso_length_px = abs(shoulder_center_y - hip_center_y)
            
            # 4. Arm length (shoulder to wrist)
            left_arm_length = (np.sqrt((left_shoulder_px[0] - left_elbow_px[0])**2 + 
                                      (left_shoulder_px[1] - left_elbow_px[1])**2) +
                              np.sqrt((left_elbow_px[0] - left_wrist_px[0])**2 + 
                                     (left_elbow_px[1] - left_wrist_px[1])**2))
            
            right_arm_length = (np.sqrt((right_shoulder_px[0] - right_elbow_px[0])**2 + 
                                       (right_shoulder_px[1] - right_elbow_px[1])**2) +
                               np.sqrt((right_elbow_px[0] - right_wrist_px[0])**2 + 
                                      (right_elbow_px[1] - right_wrist_px[1])**2))
            
            arm_length_px = (left_arm_length + right_arm_length) / 2
            
            # 5. Leg length (hip to ankle)
            left_leg_length = (np.sqrt((left_hip_px[0] - left_knee_px[0])**2 + 
                                      (left_hip_px[1] - left_knee_px[1])**2) +
                              np.sqrt((left_knee_px[0] - left_ankle_px[0])**2 + 
                                     (left_knee_px[1] - left_ankle_px[1])**2))
            
            right_leg_length = (np.sqrt((right_hip_px[0] - right_knee_px[0])**2 + 
                                       (right_hip_px[1] - right_knee_px[1])**2) +
                               np.sqrt((right_knee_px[0] - right_ankle_px[0])**2 + 
                                      (right_knee_px[1] - right_ankle_px[1])**2))
            
            leg_length_px = (left_leg_length + right_leg_length) / 2
            
            # 6. Hip width
            hip_width_px = np.sqrt((left_hip_px[0] - right_hip_px[0])**2 + 
                                  (left_hip_px[1] - right_hip_px[1])**2)
            
            # Calculate average depth
            avg_depth = 2.0  # Default depth
            if depth_map is not None:
                shoulder_center_x = (left_shoulder_px[0] + right_shoulder_px[0]) // 2
                shoulder_center_y = (left_shoulder_px[1] + right_shoulder_px[1]) // 2
                if (0 <= shoulder_center_x < width and 0 <= shoulder_center_y < height):
                    avg_depth = depth_map[shoulder_center_y, shoulder_center_x]
            
            # Calculate confidence based on landmark visibility
            landmark_confidence = np.mean([
                nose.visibility, left_shoulder.visibility, right_shoulder.visibility,
                left_hip.visibility, right_hip.visibility, left_ankle.visibility, right_ankle.visibility
            ])
            
            # Calculate landmarks quality based on detection confidence
            landmarks_quality = np.mean([
                getattr(landmark, 'presence', 0.8) for landmark in [
                    nose, left_shoulder, right_shoulder, left_hip, right_hip,
                    left_ankle, right_ankle, left_elbow, right_elbow, left_wrist, right_wrist
                ]
            ])
            
            # Create measurement points
            measurement_data = [
                ('height', height_px),
                ('shoulder_width', shoulder_width_px),
                ('torso_length', torso_length_px),
                ('arm_length', arm_length_px),
                ('leg_length', leg_length_px),
                ('hip_width', hip_width_px)
            ]
            
            for measurement_type, value in measurement_data:
                if value > 0:  # Only add valid measurements
                    measurements.append(MeasurementPoint(
                        timestamp=timestamp,
                        measurement_type=measurement_type,
                        value=value,
                        confidence=landmark_confidence,
                        depth=avg_depth,
                        frame_id=self.frame_count,
                        landmarks_quality=landmarks_quality
                    ))
        
        except Exception as e:
            print(f"Error extracting measurements: {e}")
        
        return measurements
    
    def normalize_pose_landmarks(self, landmarks, target_height: float = 1.0, 
                                center_point: str = None) -> List[Tuple[float, float, float]]:
        """
        Normalize MediaPipe pose landmarks using the 3D landmark normalization
        
        Args:
            landmarks: MediaPipe pose landmarks
            target_height: Target height for normalization (default: 1.0)
            center_point: Point to center on ('nose', 'chest', 'hip', or None for centroid)
            
        Returns:
            List of normalized (x, y, z) coordinates
        """
        if not landmarks or not MEDIAPIPE_AVAILABLE:
            return []
        
        try:
            # Convert MediaPipe landmarks to 3D tuples
            landmark_tuples = []
            for landmark in landmarks:
                # Use MediaPipe's normalized coordinates (0-1) and Z depth
                landmark_tuples.append((landmark.x, landmark.y, landmark.z))
            
            # Apply the 3D landmark normalization
            normalized_landmarks = self.normalizer.normalize_landmarks(
                landmarks=landmark_tuples,
                target_height=target_height,
                center_point=center_point
            )
            
            return normalized_landmarks
            
        except Exception as e:
            print(f"Error normalizing pose landmarks: {e}")
            return []
    
    def process_frame(self, frame: np.ndarray, collect_measurements: bool = True) -> Tuple[np.ndarray, List[MeasurementPoint]]:
        """Process a single frame and extract measurements"""
        self.frame_count += 1
        measurements = []
        
        if not MEDIAPIPE_AVAILABLE:
            return frame, measurements
        
        # Convert BGR to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process pose landmarks
        results = self.pose.process(frame_rgb)
        
        if results.pose_landmarks and collect_measurements:
            # Draw landmarks on frame
            self.mp_draw.draw_landmarks(
                frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2)
            )
            
            # Extract measurements
            measurements = self.extract_measurements_from_landmarks(
                results.pose_landmarks.landmark, frame.shape
            )
            
            # Add to buffer
            self.measurement_buffer.extend(measurements)
            
            # Display current measurements on frame
            if measurements:
                y_offset = 30
                for measurement in measurements:
                    cv2.putText(frame, f"{measurement.measurement_type}: {measurement.value:.1f}px", 
                               (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    y_offset += 25
        
        return frame, measurements
    
    def start_scanning_session(self):
        """Start a new scanning session"""
        self.scanning_active = True
        self.measurement_buffer = []
        self.frame_count = 0
        print("Scanning session started")
    
    def end_scanning_session(self, user_id: str = "default") -> Tuple[BodyProfile, Dict]:
        """End scanning session and process collected measurements"""
        self.scanning_active = False
        
        if not self.measurement_buffer:
            print("No measurements collected during session")
            return None, {}
        
        print(f"Processing {len(self.measurement_buffer)} measurements...")
        
        # Process measurements through normalizer
        body_profile, report = self.normalizer.process_measurements(self.measurement_buffer, user_id)
        
        # Clear buffer
        self.measurement_buffer = []
        
        return body_profile, report
    
    def get_current_measurements(self) -> Dict[str, float]:
        """Get current averaged measurements from buffer"""
        if not self.measurement_buffer:
            return {}
        
        # Group recent measurements (last 10 frames)
        recent_measurements = [m for m in self.measurement_buffer if self.frame_count - m.frame_id <= 10]
        
        if not recent_measurements:
            return {}
        
        # Calculate averages
        grouped = {}
        for m in recent_measurements:
            if m.measurement_type not in grouped:
                grouped[m.measurement_type] = []
            grouped[m.measurement_type].append(m.value)
        
        averages = {}
        for measurement_type, values in grouped.items():
            averages[measurement_type] = np.mean(values)
        
        return averages
    
    def save_session_data(self, body_profile: BodyProfile, report: Dict, 
                         filename: str = None) -> str:
        """Save complete session data including profile and report"""
        if filename is None:
            filename = f"scan_session_{body_profile.user_id}_{int(body_profile.timestamp)}.json"
        
        session_data = {
            'body_profile': body_profile.__dict__,
            'processing_report': report,
            'session_info': {
                'total_frames': self.frame_count,
                'measurements_collected': len(self.measurement_buffer),
                'mediapipe_available': MEDIAPIPE_AVAILABLE
            }
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(session_data, f, indent=2)
            print(f"Session data saved to: {filename}")
            return filename
        except Exception as e:
            print(f"Error saving session data: {e}")
            return ""

class LiveScanningDemo:
    """Demo class showing live scanning with data normalization"""
    
    def __init__(self):
        self.processor = ErgoScanProcessor()
        self.cap = None
        self.running = False
    
    def start_live_demo(self):
        """Start live demo with webcam"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        self.running = True
        self.processor.start_scanning_session()
        
        print("Live scanning demo started. Press 'q' to quit, 's' to save profile")
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Process frame
            processed_frame, measurements = self.processor.process_frame(frame)
            
            # Add session info to frame
            cv2.putText(processed_frame, f"Frame: {self.processor.frame_count}", 
                       (10, frame.shape[0] - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(processed_frame, f"Measurements: {len(self.processor.measurement_buffer)}", 
                       (10, frame.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(processed_frame, "Press 'q' to quit, 's' to save profile", 
                       (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Display current measurements
            current_measurements = self.processor.get_current_measurements()
            y_offset = 200
            for measurement_type, value in current_measurements.items():
                cv2.putText(processed_frame, f"Avg {measurement_type}: {value:.1f}px", 
                           (processed_frame.shape[1] - 300, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                y_offset += 25
            
            # Show frame
            cv2.imshow('ErgoScan Live Demo with Data Normalization', processed_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self.save_current_profile()
        
        self.cleanup()
    
    def save_current_profile(self):
        """Save current profile from measurements"""
        if len(self.processor.measurement_buffer) < 10:
            print("Not enough measurements for reliable profile. Collect more data.")
            return
        
        body_profile, report = self.processor.end_scanning_session("demo_user")
        
        if body_profile:
            filename = self.processor.save_session_data(body_profile, report)
            print(f"Profile saved with quality score: {body_profile.calibration_quality:.2f}/10")
            
            # Restart session for continued scanning
            self.processor.start_scanning_session()
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        
        # Final save if measurements available
        if len(self.processor.measurement_buffer) >= 5:
            print("Saving final measurements...")
            body_profile, report = self.processor.end_scanning_session("final_user")
            if body_profile:
                self.processor.save_session_data(body_profile, report)

def main():
    """Main function to run the live demo"""
    print("ErgoScan Data Normalization & Refinement Demo")
    print("=" * 50)
    
    demo = LiveScanningDemo()
    demo.start_live_demo()

if __name__ == "__main__":
    main()