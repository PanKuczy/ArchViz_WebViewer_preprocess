"""Processor for extracting polygons from VRay object ID mask images"""

import cv2
import numpy as np
from ..core.utils import hex_to_bgr, get_color_bounds


def _normalize_polygon(points, image_width, image_height):
    """Normalize polygon coordinates to the processed image dimensions."""
    return [
        [x / image_width, y / image_height]
        for x, y in points
    ]


def extract_polygons_from_mask(image, color_to_id_map, epsilon=2.0, tolerance=0):
    """Extract polygons from a mask image based on colors
    
    When multiple contours exist for the same color, returns them as a compound polygon
    (list of polygons under the same key).
    
    Args:
        image: OpenCV image array (BGR format)
        color_to_id_map: Dictionary mapping unit IDs to hex colors
        epsilon: Polygon approximation epsilon (higher = simpler polygons)
        tolerance: Color tolerance for matching (0-255)
        
    Returns:
        Dictionary mapping object IDs to:
                - Single normalized polygon (list of points) if only one contour exists
                - Compound normalized polygon (list of polygons) if multiple contours exist
                    where each point is [x / image_width, y / image_height]
    """
    if image is None:
        raise ValueError("Invalid image")
    
    image_height, image_width = image.shape[:2]
    results = {}
    found_count = 0

    if tolerance == 0:
        # Exact matching only needs colors that are actually present in the mask.
        # This avoids scanning the image once for every unused color in a large map.
        present_colors = {
            tuple(color) for color in np.unique(image.reshape(-1, image.shape[2]), axis=0)
        }
        colors_to_process = (
            (unit_id, hex_color)
            for unit_id, hex_color in color_to_id_map.items()
            if tuple(hex_to_bgr(hex_color)) in present_colors
        )
    else:
        colors_to_process = color_to_id_map.items()
    
    # Iterate: unit_id is key (XXXXX), hex_color is value (#XXXXXX)
    for unit_id, hex_color in colors_to_process:
        try:
            bgr = np.array(hex_to_bgr(hex_color), dtype=np.uint8)
            lower_bound, upper_bound = get_color_bounds(bgr, tolerance)
            
            # Create binary mask for this color
            binary = cv2.inRange(image, lower_bound, upper_bound)
            
            # Find contours (handle OpenCV version differences)
            result = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = result[0] if len(result) == 2 else result[1]
            
            if contours:
                polygons = []
                
                # Extract all contours for this color
                for contour in contours:
                    simplified = cv2.approxPolyDP(contour, epsilon, True)
                    points = simplified.reshape(-1, 2).tolist()
                    
                    # Valid polygon must have at least 3 points
                    if len(points) >= 3:
                        polygons.append(
                            _normalize_polygon(points, image_width, image_height)
                        )
                
                # Store result: single polygon or compound (list of polygons)
                if len(polygons) == 1:
                    results[unit_id] = polygons[0]
                    found_count += 1
                elif len(polygons) > 1:
                    results[unit_id] = polygons  # Compound polygon
                    found_count += len(polygons)
                    
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
        Dictionary mapping object IDs to normalized polygon point lists (or compound
        polygons), where each point is [x / image_width, y / image_height]
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
        Dictionary mapping object IDs to the largest normalized polygon per color,
        where each point is [x / image_width, y / image_height]
    """
    results = {}
    image_height, image_width = image.shape[:2]
    
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
                    results[unit_id] = _normalize_polygon(
                        points, image_width, image_height
                    )
                    
        except Exception as e:
            print(f"Warning: Failed to process color {unit_id} ({hex_color}): {e}")
    
    return results

