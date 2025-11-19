# calibration/storage.py
# -------------------------------------------------------------
# PURPOSE:
# This module handles saving, loading, and validating calibration
# data used in your ergonomic measurement app (like body posture
# or setup calibration results).
#
# It includes:
#  - File naming conventions
#  - Safe JSON writing/loading
#  - Validation checks
#  - Example helper to bundle mock or real data and save it
# -------------------------------------------------------------

import json
import os
import tempfile
from datetime import datetime, timezone
from typing import Dict, Tuple, List, Optional, Any

# -------------------------------------------------------------
# REQUIRED JSON STRUCTURE
# -------------------------------------------------------------
# These are the main keys expected in every calibration file.
# If any are missing, the data fails validation.
REQUIRED_TOP_LEVEL_KEYS = {
    "version",
    "timestamp",
    "raw_landmarks",
    "measurements",
    "normalized",
    "camera_meta"
}

# -------------------------------------------------------------
# FUNCTION: default_filename
# -------------------------------------------------------------
def default_filename(user_id: Optional[str] = None) -> str:
    """
    Generate a standard filename for a calibration file.

    Example output:
        "calibration_user-abc123_2025-10-30T22-00-00Z.json"

    - user_id is optional (if you don’t have a logged-in user yet)
    - Uses current UTC time to keep filenames unique
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    user_tag = f"user-{user_id}" if user_id else "anon"
    return f"calibration_{user_tag}_{ts}.json"


# -------------------------------------------------------------
# FUNCTION: atomic_write_json
# -------------------------------------------------------------
def atomic_write_json(path: str, data: Dict[str, Any]) -> None:
    """
    Safely writes JSON data to disk.
    Why “atomic”? Because it avoids corrupted files if your app
    crashes mid-write.

    FLOW:
      1. Create a temp file in the same folder
      2. Write data into that temp file
      3. Replace the final file in one atomic operation

    This ensures we never end up with half-written JSONs.
    """
    dirpath = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dirpath, prefix=".tmp_cal_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())  # ensure it's written to disk
        # Replace original file atomically
        os.replace(tmp_path, path)
    finally:
        # Cleanup temp file in case of errors
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


# -------------------------------------------------------------
# FUNCTION: validate_calibration_data
# -------------------------------------------------------------
def validate_calibration_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Check whether calibration data has all required fields and
    correct basic types.

    Returns:
        (is_valid, list_of_error_messages)

    FLOW:
      1. Verify data is a dictionary
      2. Check required top-level keys exist
      3. Validate timestamp format
      4. Check sub-objects (raw_landmarks, measurements, etc.)

    Used before saving data to ensure structure integrity.
    """
    errors: List[str] = []

    # Step 1: Basic type check
    if not isinstance(data, dict):
        return False, ["data must be a dictionary (parsed JSON object)"]

    # Step 2: Check for missing keys
    missing = REQUIRED_TOP_LEVEL_KEYS - set(data.keys())
    if missing:
        errors.append(f"Missing top-level keys: {sorted(list(missing))}")

    # Step 3: Check timestamp
    ts = data.get("timestamp")
    if ts is None:
        errors.append("timestamp is required")
    else:
        if not isinstance(ts, str):
            errors.append("timestamp must be an ISO string")

    # Step 4: Validate nested structures
    # raw_landmarks should be a dict with a list of "landmarks"
    raw = data.get("raw_landmarks")
    if raw:
        if not isinstance(raw, dict):
            errors.append("raw_landmarks must be an object/dict")
        else:
            lm = raw.get("landmarks")
            if lm is None:
                errors.append("raw_landmarks.landmarks is required")
            elif not isinstance(lm, list):
                errors.append("raw_landmarks.landmarks must be a list (per-joint dicts)")
            else:
                # Validate each landmark entry (required keys/types) and check for duplicate names
                seen_names = set()
                for i, item in enumerate(lm):
                    if not isinstance(item, dict):
                        errors.append(f"raw_landmarks.landmarks[{i}] must be an object")
                        continue
                    # required fields per item
                    for key in ("name", "x", "y", "z", "visibility"):
                        if key not in item:
                            errors.append(f"raw_landmarks.landmarks[{i}] missing '{key}'")
                    # types & ranges
                    if "name" in item and not isinstance(item["name"], str):
                        errors.append(f"raw_landmarks.landmarks[{i}].name must be a string")
                    if "name" in item:
                        if item["name"] in seen_names:
                            errors.append(f"duplicate landmark name: {item['name']}")
                        else:
                            seen_names.add(item["name"])
                    for coord in ("x", "y", "z"):
                        if coord in item and not isinstance(item[coord], (int, float)):
                            errors.append(f"raw_landmarks.landmarks[{i}].{coord} must be a number")
                    if "visibility" in item:
                        if not isinstance(item["visibility"], (int, float)):
                            errors.append(f"raw_landmarks.landmarks[{i}].visibility must be a number")
                        else:
                            v = item["visibility"]
                            if not (0.0 <= v <= 1.0):
                                errors.append(f"raw_landmarks.landmarks[{i}].visibility must be between 0 and 1")

    # measurements must be a dict
    meas = data.get("measurements")
    if meas and not isinstance(meas, dict):
        errors.append("measurements must be a dict")
    else:
        # If present, ensure known numeric measurement fields are numbers
        if isinstance(meas, dict):
            numeric_fields = [
                "pixel_height",
                "scale_factor_cm_per_pixel",
                "shoulder_width_px",
                "shoulder_width_cm",
                "arm_length_px",
                "arm_length_cm",
                "leg_length_px",
                "leg_length_cm",
                "torso_length_px",
                "torso_length_cm",
            ]
            for f in numeric_fields:
                if f in meas and not isinstance(meas[f], (int, float)):
                    errors.append(f"measurements.{f} must be a number")

    # camera_meta must be a dict
    cam = data.get("camera_meta")
    if cam and not isinstance(cam, dict):
        errors.append("camera_meta must be a dict")

    return (len(errors) == 0), errors


# -------------------------------------------------------------
# FUNCTION: save_calibration_json
# -------------------------------------------------------------
def save_calibration_json(
    data: Dict[str, Any],
    folder: str = "calibration/samples",
    filename: Optional[str] = None,
    overwrite: bool = False
) -> str:
    """
    Validate and then save calibration JSON to disk.

    Parameters:
      - data: the calibration data dict (from mock or actual calibration)
      - folder: where to save (defaults to calibration/samples)
      - filename: optional custom name
      - overwrite: if False, prevents overwriting existing files

    Returns:
      - Absolute path to the saved JSON

    FLOW:
      1. Fill in missing defaults (version, timestamp)
      2. Validate structure
      3. Create target folder if missing
      4. Build filename
      5. Use atomic_write_json() to safely save
    """
    # Ensure minimal metadata exists
    data = dict(data)  # copy to avoid mutating input
    data.setdefault("version", "1.0")
    data.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

    # Validate before saving
    ok, errs = validate_calibration_data(data)
    if not ok:
        raise ValueError(f"Calibration data failed validation: {errs}")

    # Ensure directory exists
    os.makedirs(folder, exist_ok=True)

    # Build filename
    if filename is None:
        filename = default_filename(data.get("user_id"))
    path = os.path.join(folder, filename)

    # Avoid overwriting unless explicitly allowed
    if os.path.exists(path) and not overwrite:
        raise FileExistsError(f"{path} already exists (use overwrite=True to replace)")

    # Write to disk safely
    atomic_write_json(path, data)
    return os.path.abspath(path)


# -------------------------------------------------------------
# FUNCTION: load_calibration_json
# -------------------------------------------------------------
def load_calibration_json(path: str) -> Dict[str, Any]:
    """
    Load calibration data from disk into memory.

    Returns a dictionary that you can use elsewhere in your app.

    Raises:
      - FileNotFoundError if path doesn’t exist
      - json.JSONDecodeError if file is corrupted or not valid JSON
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# -------------------------------------------------------------
# FUNCTION: build_and_save_example
# -------------------------------------------------------------
def build_and_save_example(
    raw_landmarks: Dict[str, Any],
    measurements: Dict[str, Any],
    normalized: Dict[str, Any],
    camera_meta: Dict[str, Any],
    folder: str = "calibration/samples",
    user_id: Optional[str] = None
) -> str:
    """
    Convenience function for testing or mocking.

    Combines several components (raw_landmarks, measurements,
    normalized, camera_meta) into a valid calibration payload
    and immediately saves it using save_calibration_json().

    FLOW:
      1. Build a complete payload dictionary
      2. Add defaults (version, timestamp)
      3. Pass the payload to save_calibration_json()
    """
    payload = {
        "version": "1.0",
        "user_id": user_id,
        "pose_type": raw_landmarks.get("pose_type", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "raw_landmarks": raw_landmarks,
        "measurements": measurements,
        "normalized": normalized,
        "camera_meta": camera_meta
    }

    # Reuse the main save function for consistency
    return save_calibration_json(payload, folder=folder)
