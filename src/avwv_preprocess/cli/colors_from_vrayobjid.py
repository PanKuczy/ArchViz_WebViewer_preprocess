"""CLI for extracting VRay object ID colors from chart images"""

import argparse
import sys
from pathlib import Path

from avwv_preprocess.colors_from_vrayobjid import extract_vray_colors_from_objectIDs


def main():
    parser = argparse.ArgumentParser(
        description='Extract VRay object ID colors from chart images'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Single image command
    single_parser = subparsers.add_parser('single', help='Process a single chart image')
    single_parser.add_argument('image', help='Path to the chart image')
    single_parser.add_argument('-t', '--type', dest='chart_type', help='Type of chart: "chart" or "strip" (default: "chart")', default='chart')
    single_parser.add_argument('-o', '--output', help='Output JSON file path')
    single_parser.add_argument('-i', '--index', type=int, default=1, help='Starting index for object IDs (default: 1)')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch process multiple chart images')
    batch_parser.add_argument('input_dir', help='Directory containing chart images')
    batch_parser.add_argument('-t', '--type', dest='chart_type', help='Type of chart: "chart" or "strip" (default: "chart")', default='chart')
    batch_parser.add_argument('-o', '--output-dir', help='Output directory (default: input directory)')
    batch_parser.add_argument('-m', '--merge', action='store_true', help='Merge all outputs into single file')
    batch_parser.add_argument('--merge-output', help='Output path for merged file (used with --merge)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'single':
            print(f"Processing single image: {args.image}")
            colors = extract_vray_colors_from_objectIDs.extract_from_single_image(
                args.image, args.chart_type, args.output, args.index
            )
            print(f"✓ Extracted {len(colors)} colors, starting from index {args.index}")
            return 0
            
        elif args.command == 'batch':
            if args.merge:
                if not args.merge_output:
                    print("Error: --merge-output required when using --merge")
                    return 1
                print(f"Batch processing with merge: {args.input_dir} -> {args.merge_output}")
                colors = extract_vray_colors_from_objectIDs.extract_batch_merged(
                    args.input_dir, args.merge_output, args.chart_type
                )
                print(f"✓ Merged {len(colors)} colors")
            else:
                output_dir = args.output_dir or args.input_dir
                print(f"Batch processing: {args.input_dir} -> {output_dir}")
                results = extract_vray_colors_from_objectIDs.extract_batch_separate(
                    args.input_dir, output_dir, args.chart_type
                )
                print(f"✓ Processed {len(results)} images")
            return 0
            
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
