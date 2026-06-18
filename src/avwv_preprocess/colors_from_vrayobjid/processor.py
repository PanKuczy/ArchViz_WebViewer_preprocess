"""Processor for extracting colors from VRay object ID charts"""
import json
from PIL import Image
from ..core.utils import rgb_to_hex


def extract_colors_from_chart(image_path, start_index=1):
    """Extract colors from a VRay object ID chart image
    
    Each pixel column in the chart represents one object ID with its color.
    
    Args:
        image_path: Path to the VRay object ID chart image
        start_index: Starting index for object IDs (default: 1)
        
    Returns:
        Dictionary mapping object IDs with 5-digit padding (e.g., '00001') to hex colors (e.g., '#FF0000')
        
    Raises:
        FileNotFoundError: If image not found
        IOError: If image cannot be opened
    """
    try:
        img = Image.open(image_path).convert("RGB")
    except FileNotFoundError:
        raise FileNotFoundError(f"Image not found: {image_path}")
    except Exception as e:
        raise IOError(f"Failed to open image {image_path}: {e}")
    
    colors = {}
    index = start_index
    
    # Each column represents one color
    for x in range(img.width):
        r, g, b = img.getpixel((x, 0))
        colors[f"{index:05d}"] = rgb_to_hex(r, g, b)
        index += 1
    
    return colors


def extract_colors_from_strip(image_path, orientation='horizontal', start_index=1):
    """Extract colors from a color strip (horizontal or vertical)
    
    Args:
        image_path: Path to the color strip image
        orientation: 'horizontal' or 'vertical'
        start_index: Starting index for object IDs (default: 1)
        
    Returns:
        Dictionary mapping object IDs to hex colors
    """
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        raise IOError(f"Failed to open image {image_path}: {e}")
    
    colors = {}
    index = start_index
    
    if orientation == 'horizontal':
        # Each column is a color
        for x in range(img.width):
            r, g, b = img.getpixel((x, 0))
            colors[f"{index:05d}"] = rgb_to_hex(r, g, b)
            index += 1
    elif orientation == 'vertical':
        # Each row is a color
        for y in range(img.height):
            r, g, b = img.getpixel((0, y))
            colors[f"{index:05d}"] = rgb_to_hex(r, g, b)
            index += 1
    else:
        raise ValueError(f"Unknown orientation: {orientation}. Use 'horizontal' or 'vertical'")
    
    return colors
