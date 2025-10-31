"""
ErgoScan Data Normalization & Refinement Module
Step 3: Clean, normalize, and validate computed data for consistent measurement accuracy

This module handles:
- Outlier detection and removal
- Multi-frame measurement averaging  
- Camera distance corrections
- Calibration standard applications
- Data validation and quality assurance
- MediaPipe landmark normalization
"""

import numpy as np
import json
import time
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from scipy import stats
from collections import deque
import warnings

warnings.filterwarnings('ignore')

@dataclass
class MeasurementPoint:
    """Single measurement data point"""
    timestamp: float
    measurement_type: str  # 'height', 'shoulder_width', 'arm_length', etc.
    value: float  # Raw measurement in pixels or cm
    confidence: float  # Detection confidence (0-1)
    depth: float  # Estimated depth in meters
    frame_id: int  # Frame number
    landmarks_quality: float  # Quality of landmark detection (0-1)

@dataclass
class BodyProfile:
    """Refined body profile with normalized measurements"""
    user_id: str
    height: float
    shoulder_width: float
    torso_length: float
    arm_length: float
    leg_length: float
    hip_width: float
    scale_factor: float
    calibration_quality: float
    measurement_count: int
    timestamp: float
    
class DataNormalizer:
    """Main class for data normalization and refinement"""
    
    def __init__(self, calibration_file: str = "ergoscan_calibration.json",
                 outlier_threshold: float = 2.5,
                 min_confidence: float = 0.5,
                 min_samples: int = 5):
        """
        Initialize the data normalizer
        
        Args:
            calibration_file: Path to calibration data file
            outlier_threshold: Z-score threshold for outlier detection
            min_confidence: Minimum confidence threshold for measurements
            min_samples: Minimum number of samples required for processing
        """
        self.calibration_file = calibration_file
        self.outlier_threshold = outlier_threshold
        self.min_confidence = min_confidence
        self.min_samples = min_samples
        
        # Load calibration data if available
        self.calibration_data = self.load_calibration_data()
        
    def load_calibration_data(self) -> Dict[str, Any]:
        """Load calibration data from file"""
        try:
            with open(self.calibration_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Calibration file {self.calibration_file} not found")
            return {}
        except Exception as e:
            print(f"Error loading calibration data: {e}")
            return {}
    
    def process_measurements(self, measurements: List[MeasurementPoint], 
                           user_id: str) -> Tuple[BodyProfile, Dict[str, Any]]:
        """
        Main processing pipeline for measurement data
        
        Args:
            measurements: List of measurement points to process
            user_id: Identifier for the user/session
            
        Returns:
            Tuple of (refined_body_profile, processing_report)
        """
        print("Starting data normalization and refinement...")
        
        processing_steps = []
        initial_count = len(measurements)
        
        # Step 1: Filter by confidence
        filtered_measurements = self.filter_by_confidence(measurements)
        confidence_retained = len(filtered_measurements)
        processing_steps.append(f"Step 1 - Confidence filter: {confidence_retained}/{initial_count} retained")
        
        # Step 2: Remove outliers
        cleaned_measurements = self.remove_outliers(filtered_measurements)
        outlier_retained = len(cleaned_measurements)
        processing_steps.append(f"Step 2 - Outlier removal: {outlier_retained}/{initial_count} retained")
        
        # Step 3: Apply temporal smoothing
        smoothed_measurements = self.apply_temporal_smoothing(cleaned_measurements)
        processing_steps.append("Step 3 - Temporal smoothing applied")
        
        # Step 4: Apply depth correction
        depth_corrected = self.apply_depth_correction(smoothed_measurements)
        processing_steps.append("Step 4 - Depth correction applied")
        
        # Step 5: Apply calibration scaling
        scaled_measurements = self.apply_calibration_scaling(depth_corrected)
        processing_steps.append("Step 5 - Calibration scaling applied")
        
        # Step 6: Create body profile
        body_profile = self.create_body_profile(scaled_measurements, user_id)
        
        # Step 7: Validate results
        is_valid, issues = self.validate_measurements(scaled_measurements)
        if is_valid:
            processing_steps.append("Step 6 - Validation: PASSED")
        else:
            processing_steps.append("Step 6 - Validation: FAILED")
        
        # Calculate quality score
        quality_score = self.calculate_quality_score(scaled_measurements, body_profile)
        
        print(f"Data normalization complete. Quality score: {quality_score:.2f}/10")
        
        # Create processing report
        report = {
            'initial_count': initial_count,
            'final_count': len(scaled_measurements),
            'processing_steps': processing_steps,
            'quality_score': quality_score,
            'issues': issues
        }
        
        return body_profile, report
    
    def filter_by_confidence(self, measurements: List[MeasurementPoint]) -> List[MeasurementPoint]:
        """Filter measurements by confidence threshold"""
        return [m for m in measurements if m.confidence >= self.min_confidence]
    
    def remove_outliers(self, measurements: List[MeasurementPoint]) -> List[MeasurementPoint]:
        """Remove outliers using Z-score method"""
        if len(measurements) < self.min_samples:
            return measurements
        
        # Group by measurement type
        grouped = {}
        for measurement in measurements:
            if measurement.measurement_type not in grouped:
                grouped[measurement.measurement_type] = []
            grouped[measurement.measurement_type].append(measurement)
        
        cleaned_measurements = []
        
        for measurement_type, group in grouped.items():
            if len(group) < 3:  # Need at least 3 points for outlier detection
                cleaned_measurements.extend(group)
                continue
            
            values = [m.value for m in group]
            z_scores = np.abs(stats.zscore(values))
            
            # Keep measurements within threshold
            for i, measurement in enumerate(group):
                if z_scores[i] <= self.outlier_threshold:
                    cleaned_measurements.append(measurement)
                else:
                    print(f"Removed outlier: {measurement_type} = {measurement.value:.2f}")
        
        return cleaned_measurements
    
    def apply_temporal_smoothing(self, measurements: List[MeasurementPoint]) -> List[MeasurementPoint]:
        """Apply temporal smoothing using weighted averages"""
        if len(measurements) < 3:
            return measurements
        
        # Group by measurement type and sort by timestamp
        grouped = {}
        for measurement in measurements:
            if measurement.measurement_type not in grouped:
                grouped[measurement.measurement_type] = []
            grouped[measurement.measurement_type].append(measurement)
        
        smoothed_measurements = []
        
        for measurement_type, group in grouped.items():
            if len(group) < 3:
                smoothed_measurements.extend(group)
                continue
            
            # Sort by timestamp
            group.sort(key=lambda m: m.timestamp)
            
            # Apply moving average with confidence weighting
            window_size = min(5, len(group))
            
            for i in range(len(group)):
                start_idx = max(0, i - window_size // 2)
                end_idx = min(len(group), i + window_size // 2 + 1)
                window = group[start_idx:end_idx]
                
                # Calculate weighted average
                weights = [m.confidence * m.landmarks_quality for m in window]
                values = [m.value for m in window]
                
                if sum(weights) > 0:
                    smoothed_value = np.average(values, weights=weights)
                else:
                    smoothed_value = np.mean(values)
                
                # Create smoothed measurement
                smoothed = MeasurementPoint(
                    timestamp=group[i].timestamp,
                    measurement_type=measurement_type,
                    value=smoothed_value,
                    confidence=group[i].confidence,
                    depth=group[i].depth,
                    frame_id=group[i].frame_id,
                    landmarks_quality=group[i].landmarks_quality
                )
                smoothed_measurements.append(smoothed)
        
        return smoothed_measurements
    
    def apply_depth_correction(self, measurements: List[MeasurementPoint]) -> List[MeasurementPoint]:
        """Apply depth-based corrections to measurements"""
        if not self.calibration_data:
            print("Warning: No calibration data available for depth correction")
            return measurements
        
        corrected_measurements = []
        reference_depth = self.calibration_data.get('reference_depth', 2.0)
        
        for measurement in measurements:
            # Apply depth scaling factor
            depth_ratio = reference_depth / measurement.depth
            corrected_value = measurement.value * depth_ratio
            
            corrected = MeasurementPoint(
                timestamp=measurement.timestamp,
                measurement_type=measurement.measurement_type,
                value=corrected_value,
                confidence=measurement.confidence,
                depth=measurement.depth,
                frame_id=measurement.frame_id,
                landmarks_quality=measurement.landmarks_quality
            )
            corrected_measurements.append(corrected)
        
        return corrected_measurements
    
    def apply_calibration_scaling(self, measurements: List[MeasurementPoint]) -> List[MeasurementPoint]:
        """Apply calibration scaling factors"""
        if not self.calibration_data:
            print("Warning: No calibration data available for scaling")
            return measurements
        
        scaled_measurements = []
        scaling_factors = self.calibration_data.get('scaling_factors', {})
        
        for measurement in measurements:
            scale_factor = scaling_factors.get(measurement.measurement_type, 1.0)
            scaled_value = measurement.value * scale_factor
            
            scaled = MeasurementPoint(
                timestamp=measurement.timestamp,
                measurement_type=measurement.measurement_type,
                value=scaled_value,
                confidence=measurement.confidence,
                depth=measurement.depth,
                frame_id=measurement.frame_id,
                landmarks_quality=measurement.landmarks_quality
            )
            scaled_measurements.append(scaled)
        
        return scaled_measurements
    
    def create_body_profile(self, measurements: List[MeasurementPoint], 
                          user_id: str) -> BodyProfile:
        """Create refined body profile from processed measurements"""
        
        # Group measurements by type and calculate final values
        grouped = {}
        for measurement in measurements:
            if measurement.measurement_type not in grouped:
                grouped[measurement.measurement_type] = []
            grouped[measurement.measurement_type].append(measurement)
        
        # Calculate final measurements using confidence-weighted averages
        final_measurements = {}
        for measurement_type, group in grouped.items():
            weights = [m.confidence * m.landmarks_quality for m in group]
            values = [m.value for m in group]
            
            if sum(weights) > 0:
                final_value = np.average(values, weights=weights)
            else:
                final_value = np.mean(values)
            
            final_measurements[measurement_type] = final_value
        
        # Create body profile with default values if measurements are missing
        height = final_measurements.get('height', 0.0)
        shoulder_width = final_measurements.get('shoulder_width', 0.0)
        torso_length = final_measurements.get('torso_length', 0.0)
        arm_length = final_measurements.get('arm_length', 0.0)
        leg_length = final_measurements.get('leg_length', 0.0)
        hip_width = final_measurements.get('hip_width', 0.0)
        
        # Calculate scale factor based on calibration
        scale_factor = self.calibration_data.get('global_scale_factor', 1.0)
        
        # Calculate quality score
        quality_score = self.calculate_quality_score(measurements, None)
        
        return BodyProfile(
            user_id=user_id,
            height=height,
            shoulder_width=shoulder_width,
            torso_length=torso_length,
            arm_length=arm_length,
            leg_length=leg_length,
            hip_width=hip_width,
            scale_factor=scale_factor,
            calibration_quality=quality_score,
            measurement_count=len(measurements),
            timestamp=time.time()
        )
    
    def calculate_measurement_statistics(self, measurements: List[MeasurementPoint]) -> Dict[str, Dict[str, float]]:
        """Calculate statistics for each measurement type"""
        grouped = {}
        for measurement in measurements:
            if measurement.measurement_type not in grouped:
                grouped[measurement.measurement_type] = []
            grouped[measurement.measurement_type].append(measurement.value)
        
        stats_dict = {}
        for measurement_type, values in grouped.items():
            if values:
                stats_dict[measurement_type] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'count': len(values),
                    'cv': np.std(values) / np.mean(values) if np.mean(values) > 0 else 0
                }
            else:
                stats_dict[measurement_type] = {
                    'mean': 0, 'std': 0, 'count': 0, 'cv': 0
                }
        
        return stats_dict
    
    def validate_measurements(self, measurements: List[MeasurementPoint]) -> Tuple[bool, List[str]]:
        """Validate final measurements for reasonableness"""
        issues = []
        
        # Calculate final averages
        stats = self.calculate_measurement_statistics(measurements)
        
        # Define reasonable ranges (in cm)
        reasonable_ranges = {
            'height': (140, 220),
            'shoulder_width': (30, 70),
            'torso_length': (40, 80),
            'arm_length': (50, 90),
            'leg_length': (60, 120),
            'hip_width': (25, 60)
        }
        
        for measurement_type, (min_val, max_val) in reasonable_ranges.items():
            if measurement_type in stats:
                mean_val = stats[measurement_type]['mean']
                if mean_val < min_val or mean_val > max_val:
                    issues.append(f"{measurement_type} out of reasonable range: {mean_val:.1f}cm")
        
        # Check for sufficient data
        total_measurements = sum(stats[mt]['count'] for mt in stats)
        if total_measurements < self.min_samples:
            issues.append(f"Insufficient data: {total_measurements} measurements")
        
        return len(issues) == 0, issues
    
    def calculate_quality_score(self, measurements: List[MeasurementPoint], 
                              body_profile: Optional[BodyProfile] = None) -> float:
        """Calculate overall quality score (0-10)"""
        if not measurements:
            return 0.0
        
        # Factor 1: Number of samples (0-10 points)
        sample_score = min(10.0, len(measurements) / 50.0 * 10)
        
        # Factor 2: Measurement consistency (0-10 points)
        stats = self.calculate_measurement_statistics(measurements)
        consistency_scores = []
        for measurement_type, stat in stats.items():
            if stat['count'] > 1 and stat['mean'] > 0:
                cv = stat['cv']
                consistency_score = max(0, 10 - cv * 100)  # Lower CV is better
                consistency_scores.append(consistency_score)
        
        avg_consistency = np.mean(consistency_scores) if consistency_scores else 5.0
        
        # Factor 3: Detection quality (0-10 points)
        avg_confidence = np.mean([m.confidence for m in measurements])
        avg_landmarks_quality = np.mean([m.landmarks_quality for m in measurements])
        detection_score = (avg_confidence + avg_landmarks_quality) / 2 * 10
        
        # Factor 4: Completeness (0-10 points)
        expected_measurements = ['height', 'shoulder_width', 'torso_length', 
                               'arm_length', 'leg_length', 'hip_width']
        actual_measurements = set(m.measurement_type for m in measurements)
        completeness_score = (len(actual_measurements) / len(expected_measurements)) * 10
        
        # Weighted average
        weights = [0.2, 0.3, 0.3, 0.2]  # consistency and detection quality most important
        scores = [sample_score, avg_consistency, detection_score, completeness_score]
        
        final_score = np.average(scores, weights=weights)
        return min(10.0, max(0.0, final_score))
    
    def normalize_landmarks(self, landmarks: List[Tuple[float, float]], 
                          reference_points: Optional[Dict[str, int]] = None,
                          target_height: float = 1.0,
                          center_point: Optional[str] = None) -> List[Tuple[float, float]]:
        """
        Normalize MediaPipe landmarks by centering, rotating, and scaling coordinates
        
        Args:
            landmarks: List of (x, y) coordinate tuples from MediaPipe
            reference_points: Dict mapping body part names to landmark indices
                             (e.g., {'nose': 0, 'left_shoulder': 11, 'right_shoulder': 12})
            target_height: Target height for scaling (default: 1.0 for normalized coords)
            center_point: Body part to use as center ('nose', 'chest', 'hip', or None for centroid)
        
        Returns:
            List of normalized (x, y) coordinate tuples (centered, rotated, scaled)
        """
        if not landmarks or len(landmarks) < 2:
            return landmarks
        
        # Convert to numpy array for easier manipulation
        coords = np.array(landmarks)
        
        # Define default MediaPipe pose landmark indices if not provided
        if reference_points is None:
            reference_points = {
                'nose': 0,
                'left_shoulder': 11, 'right_shoulder': 12,
                'left_hip': 23, 'right_hip': 24,
                'left_knee': 25, 'right_knee': 26,
                'left_ankle': 27, 'right_ankle': 28
            }
        
        # 1. CENTERING: Move to origin based on specified center point
        if center_point and center_point in reference_points:
            idx = reference_points[center_point]
            if idx < len(coords):
                center = coords[idx]
            else:
                center = np.mean(coords, axis=0)  # Fallback to centroid
        elif center_point == 'chest':
            # Use midpoint between shoulders as chest
            left_shoulder_idx = reference_points.get('left_shoulder', 11)
            right_shoulder_idx = reference_points.get('right_shoulder', 12)
            if left_shoulder_idx < len(coords) and right_shoulder_idx < len(coords):
                center = (coords[left_shoulder_idx] + coords[right_shoulder_idx]) / 2
            else:
                center = np.mean(coords, axis=0)
        elif center_point == 'hip':
            # Use midpoint between hips
            left_hip_idx = reference_points.get('left_hip', 23)
            right_hip_idx = reference_points.get('right_hip', 24)
            if left_hip_idx < len(coords) and right_hip_idx < len(coords):
                center = (coords[left_hip_idx] + coords[right_hip_idx]) / 2
            else:
                center = np.mean(coords, axis=0)
        else:
            # Default: use centroid of all landmarks
            center = np.mean(coords, axis=0)
        
        # Center the coordinates
        centered_coords = coords - center
        
        # 2. ROTATION: Align body to vertical axis using shoulder line
        left_shoulder_idx = reference_points.get('left_shoulder', 11)
        right_shoulder_idx = reference_points.get('right_shoulder', 12)
        
        if (left_shoulder_idx < len(coords) and right_shoulder_idx < len(coords)):
            # Calculate shoulder line angle
            left_shoulder = centered_coords[left_shoulder_idx]
            right_shoulder = centered_coords[right_shoulder_idx]
            shoulder_vector = right_shoulder - left_shoulder
            
            # Calculate rotation angle to make shoulders horizontal
            angle = np.arctan2(shoulder_vector[1], shoulder_vector[0])
            
            # Create rotation matrix
            cos_angle = np.cos(-angle)
            sin_angle = np.sin(-angle)
            rotation_matrix = np.array([
                [cos_angle, -sin_angle],
                [sin_angle, cos_angle]
            ])
            
            # Apply rotation
            rotated_coords = np.dot(centered_coords, rotation_matrix.T)
        else:
            # If shoulders not available, skip rotation
            rotated_coords = centered_coords
        
        # 3. SCALING: Normalize based on body height
        # Calculate current body height using head-to-foot distance
        nose_idx = reference_points.get('nose', 0)
        left_ankle_idx = reference_points.get('left_ankle', 27)
        right_ankle_idx = reference_points.get('right_ankle', 28)
        
        if nose_idx < len(rotated_coords):
            head_point = rotated_coords[nose_idx]
            
            # Find the lowest foot point
            if (left_ankle_idx < len(rotated_coords) and right_ankle_idx < len(rotated_coords)):
                left_ankle = rotated_coords[left_ankle_idx]
                right_ankle = rotated_coords[right_ankle_idx]
                foot_point = left_ankle if left_ankle[1] > right_ankle[1] else right_ankle
            elif left_ankle_idx < len(rotated_coords):
                foot_point = rotated_coords[left_ankle_idx]
            elif right_ankle_idx < len(rotated_coords):
                foot_point = rotated_coords[right_ankle_idx]
            else:
                # Fallback: use the point with maximum y-distance from head
                distances = np.abs(rotated_coords[:, 1] - head_point[1])
                foot_point = rotated_coords[np.argmax(distances)]
            
            # Calculate current height
            current_height = abs(head_point[1] - foot_point[1])
            
            if current_height > 0:
                # Scale to target height
                scale_factor = target_height / current_height
                scaled_coords = rotated_coords * scale_factor
            else:
                scaled_coords = rotated_coords
        else:
            # If head not available, use overall bounding box for scaling
            y_range = np.max(rotated_coords[:, 1]) - np.min(rotated_coords[:, 1])
            if y_range > 0:
                scale_factor = target_height / y_range
                scaled_coords = rotated_coords * scale_factor
            else:
                scaled_coords = rotated_coords
        
        # Convert back to list of tuples
        normalized_landmarks = [(float(x), float(y)) for x, y in scaled_coords]
        
        return normalized_landmarks
    
    def save_refined_profile(self, body_profile: BodyProfile, 
                           filename: str = None) -> str:
        """Save the refined body profile to file"""
        if filename is None:
            filename = f"body_profile_{body_profile.user_id}_{int(body_profile.timestamp)}.json"
        
        profile_data = asdict(body_profile)
        
        try:
            with open(filename, 'w') as f:
                json.dump(profile_data, f, indent=2)
            print(f"Refined body profile saved to: {filename}")
            return filename
        except Exception as e:
            print(f"Error saving profile: {e}")
            return ""