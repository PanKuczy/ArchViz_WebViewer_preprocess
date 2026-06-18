"""CLI for extracting polygons from VRay object ID mask images"""

import argparse
import sys
from pathlib import Path

from avwv_preprocess.objid_to_polygon import objID_to_polygon


def main():
    parser = argparse.ArgumentParser(
        description='Extract polygons from VRay object ID mask images'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Single image command
    single_parser = subparsers.add_parser('single', help='Process a single mask image')
    single_parser.add_argument('image', help='Path to the mask image')
    single_parser.add_argument('color_map', help='Path to color map JSON or dict')
    single_parser.add_argument('-o', '--output', help='Output JSON file path')
    single_parser.add_argument('-e', '--epsilon', type=float, default=2.0,
                              help='Polygon approximation epsilon (default: 2.0)')
    single_parser.add_argument('-t', '--tolerance', type=int, default=0,
                              help='Color tolerance for matching (default: 0)')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch process multiple mask images')
    batch_parser.add_argument('input_dir', help='Directory containing mask images')
    batch_parser.add_argument('color_map', help='Path to color map JSON')
    batch_parser.add_argument('-o', '--output-dir', help='Output directory (default: input directory)')
    batch_parser.add_argument('-m', '--merge', action='store_true', help='Merge all outputs into single file')
    batch_parser.add_argument('--merge-output', help='Output path for merged file (used with --merge)')
    batch_parser.add_argument('-e', '--epsilon', type=float, default=2.0,
                             help='Polygon approximation epsilon (default: 2.0)')
    batch_parser.add_argument('-t', '--tolerance', type=int, default=0,
                             help='Color tolerance for matching (default: 0)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'single':
            print(f"Processing single mask: {args.image}")
            polygons = objID_to_polygon.extract_from_single_mask(
                args.image, args.color_map, args.output, args.epsilon, args.tolerance
            )
            print(f"✓ Extracted {len(polygons)} polygons")
            return 0
            
        elif args.command == 'batch':
            if args.merge:
                if not args.merge_output:
                    print("Error: --merge-output required when using --merge")
                    return 1
                print(f"Batch processing with merge: {args.input_dir} -> {args.merge_output}")
                polygons = objID_to_polygon.extract_batch_merged(
                    args.input_dir, args.color_map, args.merge_output, args.epsilon, args.tolerance
                )
                print(f"✓ Processed and merged frames")
            else:
                output_dir = args.output_dir or args.input_dir
                print(f"Batch processing: {args.input_dir} -> {output_dir}")
                results = objID_to_polygon.extract_batch_separate(
                    args.input_dir, args.color_map, output_dir, args.epsilon, args.tolerance
                )
                print(f"✓ Processed {len(results)} images")
            return 0
            
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
