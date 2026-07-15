"""CLI for image conversion to WebP or AVIF"""

import argparse
import sys
from avwv_preprocess.image_converter import pipeline

def main():
    parser = argparse.ArgumentParser(
        description='Convert images to WebP or AVIF format.'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run', required=True)

    # Single image command
    single_parser = subparsers.add_parser('single', help='Convert a single image')
    single_parser.add_argument('input', help='Path to the input image')
    single_parser.add_argument('output', help='Path for the output image')
    single_parser.add_argument('-q', '--quality', type=int, default=80,
                               help='Compression quality (1-100, default: 80)')
    single_parser.add_argument('-f', '--format', choices=['webp', 'avif'], default='webp',
                               help='Output format (default: webp)')

    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Convert a directory of images')
    batch_parser.add_argument('input_dir', help='Directory containing images to convert')
    batch_parser.add_argument('output_dir', help='Directory to save converted images')
    batch_parser.add_argument('-q', '--quality', type=int, default=80,
                              help='Compression quality (1-100, default: 80)')
    batch_parser.add_argument('-f', '--format', choices=['webp', 'avif'], default='webp',
                              help='Output format (default: webp)')
    batch_parser.add_argument('--remove-string', help='String to remove from output filenames')
    batch_parser.add_argument('--auto-names', action='store_true',
                              help='Recursively process RGB_color assets using asset names')

    args = parser.parse_args()

    try:
        if args.command == 'single':
            pipeline.process_single_image(args.input, args.output, args.quality, args.format)
        
        elif args.command == 'batch':
            pipeline.process_batch(args.input_dir, args.output_dir, args.quality, 
                                   args.format, args.remove_string,
                                   auto_names=args.auto_names)
        
        return 0
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
