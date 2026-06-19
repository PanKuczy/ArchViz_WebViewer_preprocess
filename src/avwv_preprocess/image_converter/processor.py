"""Core processor for image conversion"""

from PIL import Image


def convert_image(input_path, output_path, quality=80, output_format='webp'):
    """Converts an image to WebP or AVIF format.

    Args:
        input_path (str): Path to the input image.
        output_path (str): Path to save the converted image.
        quality (int): Compression quality (1-100).
        output_format (str): 'webp' or 'avif'.

    Raises:
        ValueError: If the output format is not supported.
    """
    if output_format.lower() not in ['webp', 'avif']:
        raise ValueError("Unsupported output format. Choose 'webp' or 'avif'.")

    try:
        with Image.open(input_path) as img:
            # Ensure output directory exists
            import os
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            img.save(output_path, format=output_format, quality=quality)
            
    except Exception as e:
        print(f"Error converting {input_path}: {e}")
        raise

