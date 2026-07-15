"""Pipeline for single and batch image conversion"""

import os
from pathlib import Path
from tqdm import tqdm
from .processor import convert_image
from ..core.asset_paths import asset_id, auto_name, find_asset_files
from ..core.utils import play_bell


def process_single_image(input_path, output_path, quality=80, output_format='webp'):
    """Processes a single image.

    Args:
        input_path (str): Path to the input image.
        output_path (str): Path to save the converted image.
        quality (int): Compression quality.
        output_format (str): 'webp' or 'avif'.
    """
    print(f"Converting {input_path} to {output_path}...")
    convert_image(input_path, output_path, quality, output_format)
    print("✓ Conversion successful.")


def process_batch(input_dir, output_dir, quality=80, output_format='webp', 
                  remove_string=None, input_patterns=None, auto_names=False):
    """Processes a batch of images.

    Args:
        input_dir (str): Directory containing images to convert.
        output_dir (str): Directory to save converted images.
        quality (int): Compression quality.
        output_format (str): 'webp' or 'avif'.
        remove_string (str, optional): String to remove from output filenames.
        input_patterns (list, optional): List of file patterns to search for. 
                                         Defaults to ['*.jpg', '*.jpeg', '*.png', '*.tif', '*.tiff'].
    """
    if auto_names:
        image_files = find_asset_files(input_dir, 'RGB_color')
        os.makedirs(output_dir, exist_ok=True)
        for image_file in tqdm(image_files, desc="Converting RGB assets"):
            output_path = os.path.join(
                output_dir, asset_id(image_file), 'rotator_frames',
                auto_name(image_file, output_format),
            )
            try:
                convert_image(str(image_file), output_path, quality, output_format)
            except Exception as e:
                print(f"✗ Failed to convert {image_file.name}: {e}")
        print(f"\nBatch conversion complete: {len(image_files)} assets.")
        play_bell()
        return

    if input_patterns is None:
        input_patterns = ['*.jpg', '*.jpeg', '*.png', '*.tif', '*.tiff']

    os.makedirs(output_dir, exist_ok=True)
    
    input_path_obj = Path(input_dir)
    image_files = []
    for pattern in input_patterns:
        image_files.extend(input_path_obj.glob(pattern))

    if not image_files:
        print(f"No images found in {input_dir} matching patterns: {input_patterns}")
        return

    print(f"Found {len(image_files)} images to convert.")
    
    for image_file in tqdm(image_files, desc="Converting images"):
        try:
            stem = image_file.stem
            if remove_string:
                stem = stem.replace(remove_string, '')
            
            output_filename = f"{stem}.{output_format.lower()}"
            output_path = os.path.join(output_dir, output_filename)
            
            convert_image(str(image_file), output_path, quality, output_format)
            
        except Exception as e:
            print(f"✗ Failed to convert {image_file.name}: {e}")

    print("\nBatch conversion complete.")
    play_bell()
