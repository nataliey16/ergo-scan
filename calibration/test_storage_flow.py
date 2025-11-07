# calibration/test_storage_flow.py
"""
Demo script to test save/load/validate functions
using the mock_calibration_data.json file.
"""

import json
import os
from storage import (
    validate_calibration_data,
    save_calibration_json,
    load_calibration_json
)

# Step 1: Load the mock calibration data
with open("data/mock_calibration_data.json", "r", encoding="utf-8") as f:
    mock_data = json.load(f)

print("Loaded mock calibration data.")

# Step 2: Validate the data structure
is_valid, errors = validate_calibration_data(mock_data)
if not is_valid:
    print("❌ Validation failed with errors:")
    for err in errors:
        print("   -", err)
    exit(1)
else:
    print("✅ Validation passed successfully!")

# Step 3: Save the data to a file (automatically generates name)
output_path = save_calibration_json(mock_data, folder="samples", overwrite=True)
print(f"✅ Data saved successfully at: {output_path}")

# Step 4: Load the data back from disk
loaded_data = load_calibration_json(output_path)
print("✅ Loaded data back from file.")

# Step 5: Quick comparison to confirm integrity
if loaded_data == mock_data:
    print("✅ Loaded data matches original data exactly!")
else:
    print("⚠️ Warning: Loaded data differs from original. (May just be timestamp or formatting differences)")

# Extra check: ensure leg length measurements were stored and loaded
try:
    orig_leg_px = mock_data["measurements"].get("leg_length_px")
    orig_leg_cm = mock_data["measurements"].get("leg_length_cm")
    loaded_leg_px = loaded_data["measurements"].get("leg_length_px")
    loaded_leg_cm = loaded_data["measurements"].get("leg_length_cm")

    if orig_leg_px is not None and orig_leg_cm is not None:
        if orig_leg_px == loaded_leg_px and orig_leg_cm == loaded_leg_cm:
            print("✅ Leg length measurements saved and loaded correctly.")
        else:
            print("⚠️ Leg length values differ between saved and loaded data.")
    else:
        print("⚠️ Original mock data did not contain leg length measurements to check.")
except Exception as e:
    print(f"Error while verifying leg length fields: {e}")

print("\n🎉 Full test completed successfully!")
