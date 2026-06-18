"""Processor for extracting polygons from VRay object ID mask images"""
#TODO: 1. if multiple contours exist for same color, it should be possible to extract and merge them into one polygon (union).


import cv2
import numpy as np
from ..core.utils import hex_to_bgr, get_color_bounds


def extract_polygons_from_mask(image, color_to_id_map, epsilon=2.0, tolerance=0):
    """Extract polygons from a mask image based on colors
    
    Args:
        image: OpenCV image array (BGR format)
        color_to_id_map: Dictionary mapping unit IDs to hex colors
        epsilon: Polygon approximation epsilon (higher = simpler polygons)
        tolerance: Color tolerance for matching (0-255)
        
    Returns:
        Dictionary mapping object IDs to polygon point lists
    """
    if image is None:
        raise ValueError("Invalid image")
    
    results = {}
    found_count = 0
    
    # Iterate: unit_id is key (XXXX), hex_color is value (#XXXXXX)
    for unit_id, hex_color in color_to_id_map.items():
        try:
            bgr = np.array(hex_to_bgr(hex_color), dtype=np.uint8)
            lower_bound, upper_bound = get_color_bounds(bgr, tolerance)
            
            # Create binary mask for this color
            binary = cv2.inRange(image, lower_bound, upper_bound)
            
            # Find contours (handle OpenCV version differences)
            result = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = result[0] if len(result) == 2 else result[1]
            
            if contours:
                # Approximate the contour to a polygon
                contour = contours[0]
                simplified = cv2.approxPolyDP(contour, epsilon, True)
                points = simplified.reshape(-1, 2).tolist()
                
                # Valid polygon must have at least 3 points
                if len(points) >= 3:
                    results[unit_id] = points
                    found_count += 1
                    
        except Exception as e:
            print(f"Warning: Failed to process color {unit_id} ({hex_color}): {e}")
    
    return results


def extract_polygons_from_mask_path(mask_path, color_to_id_map, epsilon=2.0, tolerance=0):
    """Extract polygons from a mask image file
    
    Args:
        mask_path: Path to the mask image file
        color_to_id_map: Dictionary mapping unit IDs to hex colors
        epsilon: Polygon approximation epsilon (higher = simpler polygons)
        tolerance: Color tolerance for matching (0-255)
        
    Returns:
        Dictionary mapping object IDs to polygon point lists
    """
    img = cv2.imread(mask_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {mask_path}")
    
    return extract_polygons_from_mask(img, color_to_id_map, epsilon, tolerance)


def extract_largest_polygon_per_color(image, color_to_id_map, epsilon=2.0, tolerance=0):
    """Extract the largest polygon for each color (useful when multiple regions exist)
    
    Args:
        image: OpenCV image array (BGR format)
        color_to_id_map: Dictionary mapping unit IDs to hex colors
        epsilon: Polygon approximation epsilon
        tolerance: Color tolerance for matching
        
    Returns:
        Dictionary mapping object IDs to the largest polygon per color
    """
    results = {}
    
    for unit_id, hex_color in color_to_id_map.items():
        try:
            bgr = np.array(hex_to_bgr(hex_color), dtype=np.uint8)
            lower_bound, upper_bound = get_color_bounds(bgr, tolerance)
            
            binary = cv2.inRange(image, lower_bound, upper_bound)
            result = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = result[0] if len(result) == 2 else result[1]
            
            if contours:
                # Find the largest contour by area
                largest_contour = max(contours, key=cv2.contourArea)
                simplified = cv2.approxPolyDP(largest_contour, epsilon, True)
                points = simplified.reshape(-1, 2).tolist()
                
                if len(points) >= 3:
                    results[unit_id] = points
                    
        except Exception as e:
            print(f"Warning: Failed to process color {unit_id} ({hex_color}): {e}")
    
    return results
