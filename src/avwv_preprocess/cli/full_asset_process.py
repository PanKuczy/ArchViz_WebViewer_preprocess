"""Run automatic image conversion and polygon extraction for an asset tree."""

import argparse
import sys
from pathlib import Path

from avwv_preprocess.image_converter import pipeline as image_pipeline
from avwv_preprocess.objid_to_polygon import objID_to_polygon


def _default_color_map(input_path):
    candidates = (
        input_path / 'vrayobjid_colors_all_map.json',
        input_path.parent / 'vrayobjid_colors_all_map.json',
        Path.cwd() / 'data' / 'vrayobjid_colors_all_map.json',
    )
    return next((path for path in candidates if path.is_file()), None)


def main():
    parser = argparse.ArgumentParser(
        description='Convert RGB_color assets and extract VRayObjectID polygons'
    )
    parser.add_argument('input_path', help='Root directory containing asset folders')
    parser.add_argument('output_path', help='Root directory for processed assets')
    parser.add_argument('image_format', choices=['webp', 'avif'],
                        help='Output format for RGB_color images')
    parser.add_argument('-c', '--color-map', type=Path,
                        help='Color map JSON for VRayObjectID polygons')
    parser.add_argument('-q', '--quality', type=int, default=80,
                        help='Image compression quality (default: 80)')
    parser.add_argument('-e', '--epsilon', type=float, default=2.0)
    parser.add_argument('-t', '--tolerance', type=int, default=0)
    args = parser.parse_args()

    input_path = Path(args.input_path)
    color_map = args.color_map or _default_color_map(input_path)
    if color_map is None:
        parser.error('a color map is required; use --color-map PATH')

    try:
        image_pipeline.process_batch(
            input_path, args.output_path, args.quality, args.image_format,
            auto_names=True,
        )
        objID_to_polygon.extract_batch_separate(
            input_path, str(color_map), args.output_path, args.epsilon,
            args.tolerance, auto_names=True,
        )
    except Exception as e:
        print(f'✗ Error: {e}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())