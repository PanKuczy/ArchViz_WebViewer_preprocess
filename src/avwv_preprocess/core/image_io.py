import json
import numpy as np
import cv2
from PIL import Image
import os


def load_image(image_path, mode='opencv'):
    """Load an image from file
    
    Args:
        image_path: Path to the image file
        mode: 'opencv' for BGR array or 'pil' for PIL Image
        
    Returns:
        Image array (opencv) or PIL Image object
        
    Raises:
        FileNotFoundError: If image file doesn't exist
    """
    if mode == 'opencv':
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found: {image_path}")
        return img
    elif mode == 'pil':
        try:
            return Image.open(image_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Image not found: {image_path}")
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'opencv' or 'pil'")


def save_image(image_array, output_path):
    """Save an image array to file
    
    Args:
        image_array: OpenCV image array (BGR format)
        output_path: Path where the image will be saved
        
    Returns:
        True if successful
    """
    success = cv2.imwrite(output_path, image_array)
    if not success:
        raise IOError(f"Failed to save image to {output_path}")
    return success


def get_image_info(image_path):
    """Get information about an image without loading full data
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dict with 'shape', 'dtype', 'size' (width, height)
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    return {
        'shape': img.shape,
        'dtype': img.dtype,
        'size': (img.shape[1], img.shape[0]),  # (width, height)
        'channels': img.shape[2] if len(img.shape) == 3 else 1
    }

