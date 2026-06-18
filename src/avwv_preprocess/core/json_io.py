#TODO: 2. Remove .VrayObjectID from filename when saving JSON.

import json
import os
from pathlib import Path


def load_json(file_path):
    """Load JSON data from file
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    
    with open(file_path, 'r') as f:
        return json.load(f)


def save_json(data, file_path, indent=2):
    """Save data as JSON to file
    
    Args:
        data: Data to serialize
        file_path: Path where JSON will be saved
        indent: JSON indentation level (None for compact)
        
    Returns:
        True if successful
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=indent)
    
    return True


def merge_json_files(input_dir, output_path, file_pattern='*.json'):
    """Merge multiple JSON files into one
    
    Args:
        input_dir: Directory containing JSON files to merge
        output_path: Output file path
        file_pattern: Pattern to match JSON files (default: '*.json')
        
    Returns:
        Merged dictionary
    """
    merged_data = {}
    input_path = Path(input_dir)
    
    for json_file in sorted(input_path.glob(file_pattern)):
        try:
            data = load_json(str(json_file))
            merged_data.update(data)
        except json.JSONDecodeError as e:
            print(f"Warning: Skipping {json_file}, invalid JSON: {e}")
    
    save_json(merged_data, output_path)
    return merged_data
