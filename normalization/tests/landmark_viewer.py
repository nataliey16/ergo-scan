#!/usr/bin/env python3
"""
ErgoScan Normalized Landmarks Viewer
Shows all 33 normalized MediaPipe landmarks in detail
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from data_normalizer import DataNormalizer
from test_normalization import create_dummy_mediapipe_landmarks

def show_all_normalized_landmarks(center_point=None, target_height=1.0):
    """Display all 33 normalized landmarks with their names and indices"""
    
    print("ErgoScan - Complete Normalized Landmarks Display")
    print("=" * 60)
    
    # Initialize normalizer and create landmarks
    normalizer = DataNormalizer()
    raw_landmarks = create_dummy_mediapipe_landmarks()
    
    # Normalize landmarks
    try:
        normalized = normalizer.normalize_landmarks(
            landmarks=raw_landmarks,
            center_point=center_point,
            target_height=target_height
        )
        
        if not normalized:
            print("❌ Normalization failed")
            return
        
        coords = np.array(normalized)
        
        # MediaPipe landmark names
        landmark_names = [
            "nose", "left_eye_inner", "left_eye", "left_eye_outer",
            "right_eye_inner", "right_eye", "right_eye_outer", "left_ear", 
            "right_ear", "mouth_left", "mouth_right", "left_shoulder",
            "right_shoulder", "left_elbow", "right_elbow", "left_wrist",
            "right_wrist", "left_pinky", "right_pinky", "left_index",
            "right_index", "left_thumb", "right_thumb", "left_hip",
            "right_hip", "left_knee", "right_knee", "left_ankle",
            "right_ankle", "left_heel", "right_heel", "left_foot_index",
            "right_foot_index"
        ]
        
        # Configuration info
        center_name = center_point if center_point else "centroid"
        print(f"Configuration: {center_name}-centered, height={target_height}")
        print(f"Total landmarks: {len(normalized)}")
        print("-" * 60)
        
        # Display all landmarks
        print("📍 ALL NORMALIZED LANDMARKS:")
        print(f"{'Index':<5} {'Name':<18} {'X':<8} {'Y':<8} {'Z':<8}")
        print("-" * 50)
        
        for idx, (name, pos) in enumerate(zip(landmark_names, coords)):
            if len(pos) == 3:  # 3D coordinates
                print(f"{idx:<5} {name:<18} {pos[0]:7.3f}  {pos[1]:7.3f}  {pos[2]:7.3f}")
            else:  # 2D coordinates
                print(f"{idx:<5} {name:<18} {pos[0]:7.3f}  {pos[1]:7.3f}  {'N/A':<8}")
        
        print("-" * 50)
        
        # Summary statistics
        center = np.mean(coords, axis=0)
        min_coords = np.min(coords, axis=0)
        max_coords = np.max(coords, axis=0)
        dimensions = max_coords - min_coords
        
        print(f"\n📊 SUMMARY STATISTICS:")
        if len(center) == 3:
            print(f"   Center: ({center[0]:7.3f}, {center[1]:7.3f}, {center[2]:7.3f})")
            print(f"   Min:    ({min_coords[0]:7.3f}, {min_coords[1]:7.3f}, {min_coords[2]:7.3f})")
            print(f"   Max:    ({max_coords[0]:7.3f}, {max_coords[1]:7.3f}, {max_coords[2]:7.3f})")
            print(f"   Range:  ({dimensions[0]:7.3f}, {dimensions[1]:7.3f}, {dimensions[2]:7.3f})")
            print(f"   Height: {dimensions[1]:.3f}")
        else:
            print(f"   Center: ({center[0]:7.3f}, {center[1]:7.3f})")
            print(f"   Min:    ({min_coords[0]:7.3f}, {min_coords[1]:7.3f})")
            print(f"   Max:    ({max_coords[0]:7.3f}, {max_coords[1]:7.3f})")
            print(f"   Range:  ({dimensions[0]:7.3f}, {dimensions[1]:7.3f})")
            print(f"   Height: {dimensions[1]:.3f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function with different viewing options"""
    print("Choose normalization type:")
    print("1. Default (centroid-centered)")
    print("2. Nose-centered")
    print("3. Chest-centered") 
    print("4. Hip-centered")
    print("5. Scaled to height 2.0")
    
    choice = input("\nEnter choice (1-5) or press Enter for default: ").strip()
    
    configs = {
        '1': (None, 1.0, "Default"),
        '2': ('nose', 1.0, "Nose-centered"),
        '3': ('chest', 1.0, "Chest-centered"),
        '4': ('hip', 1.0, "Hip-centered"),
        '5': (None, 2.0, "Scaled to height 2.0")
    }
    
    if choice in configs:
        center_point, target_height, name = configs[choice]
        print(f"\nShowing {name} normalized landmarks:")
        show_all_normalized_landmarks(center_point, target_height)
    else:
        print(f"\nShowing default normalized landmarks:")
        show_all_normalized_landmarks()

if __name__ == "__main__":
    main()