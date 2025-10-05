COLOR_THRESHOLD = 10

def color_match(c1, c2, threshold=COLOR_THRESHOLD):
    """Check if two RGB colors match within a threshold."""
    return all(abs(int(a) - int(b)) <= threshold for a, b in zip(c1, c2))