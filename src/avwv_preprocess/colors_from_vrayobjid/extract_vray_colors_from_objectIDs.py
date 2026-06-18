"""Extract VRay object ID colors from chart images - CLI entry point"""

import os
from pathlib import Path
from .pipeline import process_single_chart, process_batch, process_batch_merged


def extract_from_single_image(image_path, output_path=None, start_index=1):
    """Extract colors from a single VRay color chart image
    
    Args:
        image_path: Path to the VRay object ID chart image
        output_path: Optional path to save the JSON output
        start_index: Starting index for object IDs (default: 1)
        
    Returns:
        Dictionary mapping object IDs to hex colors
    """
    return process_single_chart(image_path, output_path, chart_type='chart', start_index=start_index)


def extract_batch_separate(input_dir, output_dir=None):
    """Extract colors from multiple images, saving each as separate JSON
    
    Args:
        input_dir: Directory containing VRay color chart images
        output_dir: Directory to save JSON files (default: same as input_dir)
        
    Returns:
        Dictionary with results for each image
    """
    return process_batch(input_dir, output_dir, file_pattern='*.png', chart_type='chart')


def extract_batch_merged(input_dir, output_path):
    """Extract colors from multiple images, merging into single JSON
    
    Args:
        input_dir: Directory containing VRay color chart images
        output_path: Path to save the merged JSON output
        
    Returns:
        Merged dictionary of all colors
    """
    return process_batch_merged(input_dir, output_path, file_pattern='*.png', chart_type='chart')


# Example usage for direct execution
if __name__ == "__main__":
    # Example: Process single image
    # Uncomment to use:
    # chart_path = "vrayobjectid_chart_1024x1.png"
    # output_json = "vrayobjectid_chart.json"
    # colors = extract_from_single_image(chart_path, output_json)
    # print(f"Extracted {len(colors)} colors")
    
    # Example: Batch process directory
    # input_directory = "path/to/chart/images"
    # output_directory = "path/to/output"
    # results = extract_batch_separate(input_directory, output_directory)
    
    # Example: Batch process with merge
    # input_directory = "path/to/chart/images"
    # output_file = "merged_colors.json"
    # all_colors = extract_batch_merged(input_directory, output_file)
    
    pass