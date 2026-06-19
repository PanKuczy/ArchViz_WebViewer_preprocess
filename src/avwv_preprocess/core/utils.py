import numpy as np
from platform import platform


def hex_to_bgr(hex_color):
    """Convert hex color string to BGR tuple for OpenCV
    
    Args:
        hex_color: Hex color string (e.g., '#FF0000')
        
    Returns:
        List of BGR values suitable for OpenCV
    """
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return [b, g, r]


def rgb_to_hex(r, g, b):
    """Convert RGB values to hex color string
    
    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)
        
    Returns:
        Hex color string (e.g., '#FF0000')
    """
    return f"#{r:02X}{g:02X}{b:02X}"


def get_color_bounds(bgr_color, tolerance=0):
    """Get lower and upper bounds for color matching
    
    Args:
        bgr_color: BGR color as numpy array or list
        tolerance: Color tolerance (0-255)
        
    Returns:
        Tuple of (lower_bound, upper_bound) as numpy arrays
    """
    bgr = np.array(bgr_color, dtype=np.uint8)
    lower_bound = np.maximum(bgr - tolerance, 0)
    upper_bound = np.minimum(bgr + tolerance, 255)
    return lower_bound, upper_bound

def play_bell():
    if "Windows" in platform():
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_OK)
        except ImportError:
            # Fallback for Windows versions without winsound
            print('\a')
    else:
        # For macOS, Linux, etc.
        print('\a')