"""Pipeline for batch processing VRay object ID color extraction"""

import os
from pathlib import Path
from ..core.json_io import save_json
from .processor import extract_colors_from_chart, extract_colors_from_strip


def process_single_chart(image_path, output_path=None, chart_type='chart', start_index=1):
    """Process a single VRay object ID chart
    
    Args:
        image_path: Path to the chart image
        output_path: Optional output path for the JSON file
        chart_type: 'chart' or 'strip' - type of color source
        
    Returns:
        Dictionary of extracted colors
    """
    if chart_type == 'chart':
        colors = extract_colors_from_chart(image_path, start_index=start_index)
    elif chart_type == 'strip':
        colors = extract_colors_from_strip(image_path, start_index=start_index)
    else:
        raise ValueError(f"Unknown chart_type: {chart_type}")
    
    if output_path:
        save_json(colors, output_path)
        print(f"Saved {len(colors)} colors to {output_path}")
    
    return colors

#TODO: 1. Fix batch with merge: if multiple charts have same unit ID, the last one will overwrite previous ones. Need to merge them into a list of colors for each unit ID.

def process_batch(input_dir, output_dir=None, file_pattern='*.png', chart_type='chart'):
    """Batch process multiple VRay color charts
    
    Args:
        input_dir: Directory containing chart images
        output_dir: Directory where JSON files will be saved (default: same as input_dir)
        file_pattern: Pattern to match image files (default: '*.png')
        chart_type: 'chart' or 'strip' - type of color source
        
    Returns:
        Dictionary mapping image filenames to their extracted colors
    """
    if output_dir is None:
        output_dir = input_dir
    
    os.makedirs(output_dir, exist_ok=True)
    
    input_path = Path(input_dir)
    results = {}
    processed_count = 0
    failed_count = 0
    
    image_files = sorted(input_path.glob(file_pattern))
    
    if not image_files:
        print(f"No files matching pattern '{file_pattern}' found in {input_dir}")
        return results
    
    print(f"Processing {len(image_files)} files from {input_dir}")
    
    for image_file in image_files:
        try:
            # Create output filename
            output_filename = image_file.stem + '.json'
            output_path = os.path.join(output_dir, output_filename)
            
            # Process the image
            colors = process_single_chart(str(image_file), output_path, chart_type, start_index=1)
            results[image_file.name] = colors
            processed_count += 1
            
        except Exception as e:
            print(f"Error processing {image_file.name}: {e}")
            failed_count += 1
    
    print(f"Completed: {processed_count} successful, {failed_count} failed")
    return results


def process_batch_merged(input_dir, output_path, file_pattern='*.png', chart_type='chart'):
    """Batch process and merge results into a single JSON file
    
    Args:
        input_dir: Directory containing chart images
        output_path: Path where the merged JSON will be saved
        file_pattern: Pattern to match image files (default: '*.png')
        chart_type: 'chart' or 'strip' - type of color source
        
    Returns:
        Merged dictionary of all extracted colors
    """
    all_colors = {}
    
    input_path = Path(input_dir)
    image_files = sorted(input_path.glob(file_pattern))
    
    print(f"Processing {len(image_files)} files and merging into single output")
    
    for image_file in image_files:
        try:
            colors = process_single_chart(str(image_file), None, chart_type)
            all_colors.update(colors)
            print(f"  - {image_file.name}: {len(colors)} colors")
        except Exception as e:
            print(f"  - {image_file.name}: ERROR - {e}")
    
    # Save the merged result
    save_json(all_colors, output_path)
    print(f"\nSaved {len(all_colors)} total colors to {output_path}")
    
    return all_colors
