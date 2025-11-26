def normalized_to_pixels(landmarks, image_size=None):
    """Convert normalized landmarks (0..1) to pixel coordinates.

    Args:
        landmarks: list of landmark dicts with keys 'name','x','y','z'
        image_size: tuple (width, height). If None, returns original values.

    Returns:
        dict mapping landmark name -> (x_px, y_px, z)
    """
    result = {}

    for lm in landmarks:
        name = lm["name"]
        x = lm["x"]
        y = lm["y"]
        z = lm["z"]

        if image_size is None:
            result[name] = (x, y, z)
        else:
            w, h = image_size
            result[name] = (x * w, y * h, z)

    return result
