def convert_mediapipe_coords(name, x, y, z, frame_width, frame_height, scale_px_per_cm=37.8):
    """
    Convert MediaPipe normalized coordinates (x, y, z)
    into pixel and approximate centimeter values, with a coordinate name.

    Parameters:
        name (str): Descriptive name for this coordinate (e.g. 'shoulder_width')
        x, y, z (float): Normalized coordinates from MediaPipe (0–1)
        frame_width (int): Width of the frame in pixels
        frame_height (int): Height of the frame in pixels
        scale_px_per_cm (float): Pixel-per-cm scale (default: 37.8 px/cm)

    Returns:
        dict: {
            "name": str,
            "pixels": (x_px, y_px, z_px),
            "centimeters": (x_cm, y_cm, z_cm)
        }
    """

    # Convert normalized values to pixel positions
    x_px = x * frame_width
    y_px = y * frame_height
    z_px = z * frame_width  # approximate for depth scaling

    # Convert pixels to centimeters
    x_cm = x_px / scale_px_per_cm
    y_cm = y_px / scale_px_per_cm
    z_cm = z_px / scale_px_per_cm

    return {
        "name": name,
        "pixels": (x_px, y_px, z_px),
        "centimeters": (x_cm, y_cm, z_cm)
    }


# -----------------------
# Test the function below
# -----------------------
if __name__ == "__main__":
    # Example normalized coordinates (from MediaPipe)
    name = "shoulder_width"
    x, y, z = 0.45, 0.32, -0.12
    frame_width = 1280
    frame_height = 720

    result = convert_mediapipe_coords(name, x, y, z, frame_width, frame_height)

    print(f"Name: {result['name']}\n")
    print("Pixels:", [f"{v:.2f}" for v in result['pixels']])
    print("Centimeters:", [f"{v:.2f}" for v in result['centimeters']])
