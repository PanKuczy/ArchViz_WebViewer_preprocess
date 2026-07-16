"""Extract polygons from VRay object ID mask images - CLI entry point"""

import os
from pathlib import Path
from ..core.json_io import load_json
from .pipeline import process_single_mask, process_batch, process_batch_merged


def extract_from_single_mask(mask_path, color_map, output_path=None, epsilon=2.0,
                             tolerance=0, cg_id_map=None):
    """Extract polygons from a single VRay mask image
    
    Args:
        mask_path: Path to the VRay object ID mask image
        color_map: Dictionary mapping unit IDs to hex colors (or path to JSON file)
        output_path: Optional path to save the JSON output
        epsilon: Polygon approximation epsilon (higher = simpler polygons)
        tolerance: Color tolerance for matching (0-255)
        cg_id_map: Dictionary or path mapping project IDs to polygon IDs
        
    Returns:
        Dictionary mapping object IDs to polygon point lists
    """
    return process_single_mask(
        mask_path, color_map, output_path, epsilon, tolerance,
        cg_id_map=cg_id_map,
    )


def extract_batch_separate(input_dir, color_map, output_dir=None, epsilon=2.0,
                           tolerance=0, remove_string=None, auto_names=False,
                           cg_id_map=None):
    """Extract polygons from multiple mask images, saving each as separate JSON
    
    Args:
        input_dir: Directory containing VRay object ID mask images
        color_map: Dictionary mapping unit IDs to hex colors (or path to JSON file)
        output_dir: Directory to save JSON files (default: same as input_dir)
        epsilon: Polygon approximation epsilon
        tolerance: Color tolerance for matching
        remove_string: String to remove from output filenames
        cg_id_map: Dictionary or path mapping project IDs to polygon IDs
        
    Returns:
        Dictionary with results for each image
    """
    return process_batch(input_dir, color_map, output_dir, file_pattern='*.png', 
                        epsilon=epsilon, tolerance=tolerance, remove_string=remove_string,
                        auto_names=auto_names, cg_id_map=cg_id_map)


def extract_batch_merged(input_dir, color_map, output_path, epsilon=2.0,
                         tolerance=0, remove_string=None, cg_id_map=None):
    """Extract polygons from multiple images, merging into single JSON by frame
    
    Args:
        input_dir: Directory containing VRay object ID mask images
        color_map: Dictionary mapping unit IDs to hex colors (or path to JSON file)
        output_path: Path to save the merged JSON output
        epsilon: Polygon approximation epsilon
        tolerance: Color tolerance for matching
        remove_string: String to remove from the frame identifier (stem)
        cg_id_map: Dictionary or path mapping project IDs to polygon IDs
        
    Returns:
        Merged dictionary of all polygons organized by frame
    """
    return process_batch_merged(input_dir, color_map, output_path, file_pattern='*.png',
                               epsilon=epsilon, tolerance=tolerance, remove_string=remove_string,
                               cg_id_map=cg_id_map)


# Example usage for direct execution
if __name__ == "__main__":
    # Example: Process single mask
    # Uncomment to use:
    # mask_path = "WebViewer_t1-1_0002.VRayObjectID.png"
    # color_map_path = "vrayobjectid_chart_1024.json"
    # output_json = "extracted_shapes.json"
    # polygons = extract_from_single_mask(mask_path, color_map_path, output_json)
    # print(f"Extracted {len(polygons)} polygons")
    
    # Example: Batch process directory
    # input_directory = "path/to/mask/images"
    # color_map_path = "vrayobjectid_chart_1024.json"
    # output_directory = "path/to/output"
    # results = extract_batch_separate(input_directory, color_map_path, output_directory)
    
    # Example: Batch process with merge
    # input_directory = "path/to/mask/images"
    # color_map_path = "vrayobjectid_chart_1024.json"
    # output_file = "all_frames_polygons.json"
    # all_polygons = extract_batch_merged(input_directory, color_map_path, output_file)
    
    pass