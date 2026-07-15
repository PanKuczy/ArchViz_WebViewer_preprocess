"""Pipeline for batch processing VRay object ID mask to polygon conversion"""

import os
from pathlib import Path
import cv2
from tqdm import tqdm

from ..core.image_io import load_image
from ..core.asset_paths import asset_id, auto_name, find_asset_files
from ..core.json_io import save_json, load_json
from ..core.utils import play_bell
from .processor import extract_polygons_from_mask, extract_largest_polygon_per_color


def process_single_mask(mask_path, color_map, output_path=None, epsilon=2.0, tolerance=0, largest_only=False):
    """Process a single VRay object ID mask image
    
    Args:
        mask_path: Path to the mask image
        color_map: Dictionary mapping unit IDs to hex colors (or path to JSON file)
        output_path: Optional output path for the JSON file
        epsilon: Polygon approximation epsilon (higher = simpler polygons)
        tolerance: Color tolerance for matching (0-255)
        largest_only: Extract only largest polygon per color
        
    Returns:
        Dictionary of extracted polygons
    """
    # Load color map if it's a path
    if isinstance(color_map, str):
        color_map = load_json(color_map)
    
    # Load the image
    img = load_image(mask_path, mode='opencv')
    
    # Extract polygons
    if largest_only:
        polygons = extract_largest_polygon_per_color(img, color_map, epsilon, tolerance)
    else:
        polygons = extract_polygons_from_mask(img, color_map, epsilon, tolerance)
    
    if output_path:
        save_json(polygons, output_path)
        print(f"Saved {len(polygons)} polygons to {output_path}")
    
    return polygons


def process_batch(input_dir, color_map, output_dir=None, file_pattern='*.png', 
                  epsilon=2.0, tolerance=0, largest_only=False, remove_string=None,
                  auto_names=False):
    """Batch process multiple VRay object ID mask images
    
    Args:
        input_dir: Directory containing mask images
        color_map: Dictionary mapping unit IDs to hex colors (or path to JSON file)
        output_dir: Directory where JSON files will be saved (default: same as input_dir)
        file_pattern: Pattern to match mask images (default: '*.png')
        epsilon: Polygon approximation epsilon
        tolerance: Color tolerance for matching
        largest_only: Extract only largest polygon per color
        remove_string: String to remove from output filenames
        
    Returns:
        Dictionary mapping image filenames to their extracted polygons
    """
    if output_dir is None:
        output_dir = input_dir
    
    os.makedirs(output_dir, exist_ok=True)

    if auto_names:
        if isinstance(color_map, str):
            color_map = load_json(color_map)
        image_files = find_asset_files(input_dir, 'VRayObjectID')
        results = {}
        print(f"Found {len(image_files)} VRayObjectID images")
        for image_file in tqdm(image_files, desc="Processing named masks"):
            print(f"Processing {image_file.name}", flush=True)
            output_path = os.path.join(
                output_dir, asset_id(image_file), 'rotator_polygons',
                auto_name(image_file, 'json'),
            )
            try:
                results[image_file.name] = process_single_mask(
                    str(image_file), color_map, output_path, epsilon, tolerance,
                )
            except Exception as e:
                print(f"Error processing {image_file.name}: {e}")
        print(f"Completed: {len(results)} named masks")
        play_bell()
        return results
    
    # Load color map if it's a path
    if isinstance(color_map, str):
        color_map = load_json(color_map)
    
    input_path = Path(input_dir)
    results = {}
    processed_count = 0
    failed_count = 0
    
    image_files = sorted(input_path.glob(file_pattern))
    
    if not image_files:
        print(f"No files matching pattern '{file_pattern}' found in {input_dir}")
        return results
    
    print(f"Processing {len(image_files)} mask images from {input_dir}")
    
    for image_file in tqdm(image_files, desc="Processing masks"):
        try:
            # Create output filename
            stem = image_file.stem
            if remove_string:
                stem = stem.replace(remove_string, '')
            output_filename = stem + '.json'
            output_path = os.path.join(output_dir, output_filename)
            
            # Process the image
            polygons = process_single_mask(
                str(image_file), color_map, output_path, epsilon, tolerance, largest_only
            )
            results[image_file.name] = polygons
            processed_count += 1
            
        except Exception as e:
            print(f"Error processing {image_file.name}: {e}")
            failed_count += 1
    
    print(f"Completed: {processed_count} successful, {failed_count} failed")
    play_bell()
    return results


def process_batch_merged(input_dir, color_map, output_path, file_pattern='*.png',
                         epsilon=2.0, tolerance=0, largest_only=False, remove_string=None):
    """Batch process and merge results into a single JSON file
    
    Args:
        input_dir: Directory containing mask images
        color_map: Dictionary mapping unit IDs to hex colors (or path to JSON file)
        output_path: Path where the merged JSON will be saved
        file_pattern: Pattern to match mask images (default: '*.png')
        epsilon: Polygon approximation epsilon
        tolerance: Color tolerance for matching
        largest_only: Extract only largest polygon per color
        remove_string: String to remove from the frame identifier (stem)
        
    Returns:
        Merged dictionary of all extracted polygons
    """
    # Load color map if it's a path
    if isinstance(color_map, str):
        color_map = load_json(color_map)
    
    all_polygons = {}
    input_path = Path(input_dir)
    image_files = sorted(input_path.glob(file_pattern))
    
    print(f"Processing {len(image_files)} mask images and merging into single output")
    
    for image_file in tqdm(image_files, desc="Merging masks"):
        try:
            polygons = process_single_mask(
                str(image_file), color_map, None, epsilon, tolerance, largest_only
            )
            # Merge with a frame identifier
            frame_id = image_file.stem
            if remove_string:
                frame_id = frame_id.replace(remove_string, '')
            all_polygons[frame_id] = polygons
            print(f"  - {image_file.name}: {len(polygons)} polygons")
        except Exception as e:
            print(f"  - {image_file.name}: ERROR - {e}")
    
    # Save the merged result
    save_json(all_polygons, output_path)
    print(f"\nSaved {len(all_polygons)} frames to {output_path}")
    play_bell()
    
    return all_polygons
    