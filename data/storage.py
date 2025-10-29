# save/load/validate functions

# calibration/storage.py
import json
import os
import tempfile
from datetime import datetime, timezone
from typing import Dict, Tuple, List, Optional, Any

# Top-level required keys and minimal structure for validation
REQUIRED_TOP_LEVEL_KEYS = {
    "version",
    "timestamp",
    "raw_landmarks",
    "measurements",
    "normalized",
    "camera_meta"
}

def default_filename(user_id: Optional[str] = None) -> str:
    """
    Example filename: calibration_user-abc123_2025-10-30T22-00-00Z.json
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    user_tag = f"user-{user_id}" if user_id else "anon"
    return f"calibration_{user_tag}_{ts}.json"

def atomic_write_json(path: str, data: Dict[str, Any]) -> None:
    """
    Write JSON to a temporary file and atomically replace the target path.
    This avoids partial writes if the process crashes.
    """
    dirpath = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dirpath, prefix=".tmp_cal_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        # atomic replace
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

def validate_calibration_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Minimal validation — checks presence of required top-level keys and some types.
    Returns (is_valid, list_of_error_messages).
    Keep this strict enough to catch common mistakes but flexible for prototyping.
    """
    errors: List[str] = []

    if not isinstance(data, dict):
        return False, ["data must be a dictionary (parsed JSON object)"]

    # required keys
    missing = REQUIRED_TOP_LEVEL_KEYS - set(data.keys())
    if missing:
        errors.append(f"Missing top-level keys: {sorted(list(missing))}")

    # timestamp sanity
    ts = data.get("timestamp")
    if ts is None:
        errors.append("timestamp is required")
    else:
        # simple format check (ISO-ish)
        if not isinstance(ts, str):
            errors.append("timestamp must be an ISO string")

    # raw_landmarks basic shape check
    raw = data.get("raw_landmarks")
    if raw:
        if not isinstance(raw, dict):
            errors.append("raw_landmarks must be an object/dict")
        else:
            if "landmarks" in raw and not isinstance(raw["landmarks"], list):
                errors.append("raw_landmarks.landmarks must be a list (per-joint dicts)")

    # measurements basic check
    meas = data.get("measurements")
    if meas and not isinstance(meas, dict):
        errors.append("measurements must be a dict")

    # camera_meta basic check
    cam = data.get("camera_meta")
    if cam and not isinstance(cam, dict):
        errors.append("camera_meta must be a dict")

    return (len(errors) == 0), errors

def save_calibration_json(
    data: Dict[str, Any],
    folder: str = "calibration/samples",
    filename: Optional[str] = None,
    overwrite: bool = False
) -> str:
    """
    Validate then save calibration JSON to disk.
    - folder: path relative to repo or absolute path
    - filename: if None, a default filename will be generated
    - overwrite: if False and file exists, raises FileExistsError

    Returns the absolute path where the file was written.
    """
    # Ensure minimal metadata exists
    data = dict(data)  # copy so we can inject defaults
    data.setdefault("version", "1.0")
    data.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

    # Validate
    ok, errs = validate_calibration_data(data)
    if not ok:
        # fail fast — caller can choose to bypass validation by pre-validating
        raise ValueError(f"Calibration data failed validation: {errs}")

    # ensure dir exists
    os.makedirs(folder, exist_ok=True)

    if filename is None:
        filename = default_filename(data.get("user_id"))

    path = os.path.join(folder, filename)

    if os.path.exists(path) and not overwrite:
        raise FileExistsError(f"{path} already exists (use overwrite=True to replace)")

    atomic_write_json(path, data)
    return os.path.abspath(path)

def load_calibration_json(path: str) -> Dict[str, Any]:
    """
    Load a calibration JSON file and return a dictionary.
    Will raise FileNotFoundError or json.JSONDecodeError upstream if file is invalid.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


# Example helper: quick save wrapper for raw landmarks + computed fields
def build_and_save_example(
    raw_landmarks: Dict[str, Any],
    measurements: Dict[str, Any],
    normalized: Dict[str, Any],
    camera_meta: Dict[str, Any],
    folder: str = "calibration/samples",
    user_id: Optional[str] = None
) -> str:
    """
    Convenience utility: builds the data structure and saves it (used for demos/tests).
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
    return save_calibration_json(payload, folder=folder)
