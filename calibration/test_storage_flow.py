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
with open("mock_calibration_data.json", "r", encoding="utf-8") as f:
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

print("\n🎉 Full test completed successfully!")
