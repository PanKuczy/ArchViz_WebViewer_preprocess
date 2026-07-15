# AVWV Preprocess Architecture

This document describes the modular architecture of the AVWV Preprocess module for handling VRay object ID color extraction and polygon processing.

## Overview

The project is organized into four main components:

1. **Core Utilities** - Shared functionality for image and JSON processing
2. **Colors from VRay ObjID** - Extract colors from VRay color charts (with batch support)
3. **ObjID to Polygon** - Convert object ID masks to polygon data (with batch support)
4. **Image Converter** - Converts standard image formats (JPG, PNG, TIFF) to modern web formats (WebP, AVIF).

## Folder Structure

```
src/avwv_preprocess/
├── core/
│   ├── utils.py          # Color conversion utilities
│   ├── image_io.py       # Image loading/saving
│   └── json_io.py        # JSON loading/saving
│
├── colors_from_vrayobjid/
│   ├── processor.py      # Core color extraction logic
│   ├── pipeline.py       # Batch processing pipeline
│   └── extract_vray_colors_from_objectIDs.py  # Public API
│
├── objid_to_polygon/
│   ├── processor.py      # Core polygon extraction logic
│   ├── pipeline.py       # Batch processing pipeline
│   └── objID_to_polygon.py  # Public API
│
├── image_converter/
│   ├── processor.py      # Core image conversion logic
│   └── pipeline.py       # Batch processing pipeline
│
└── cli/
    ├── colors_from_vrayobjid.py      # CLI for color extraction
    ├── objid_to_polygon_cli.py       # CLI for polygon extraction
│   ├── image_converter_cli.py        # CLI for image conversion
│   └── full_asset_process.py         # CLI for combined asset processing
```

## Module Design

### Processor Pattern
Each module follows a three-layer architecture:

1. **processor.py** - Core algorithms
   - Single image/data processing
   - Pure transformation logic
   - No I/O concerns

2. **pipeline.py** - Workflow management
   - Single item processing
   - Batch processing
   - Merge operations
   - File I/O coordination

3. **Public API** - High-level functions
   - Simple wrapper functions
   - Documentation and examples
   - Entry points for CLI and imports

### Core Utilities

**utils.py** - Color utilities
```python
from core.utils import hex_to_bgr, rgb_to_hex, get_color_bounds

bgr = hex_to_bgr('#FF0000')        # [0, 0, 255]
hex_color = rgb_to_hex(255, 0, 0)  # '#FF0000'
lower, upper = get_color_bounds(bgr, tolerance=5)
```

**image_io.py** - Image handling
```python
from core.image_io import load_image, save_image, get_image_info

img = load_image('image.png', mode='opencv')
save_image(img, 'output.png')
info = get_image_info('image.png')  # {'shape': ..., 'size': ...}
```

**json_io.py** - JSON handling
```python
from core.json_io import load_json, save_json, merge_json_files

data = load_json('data.json')
save_json(data, 'output.json')
merged = merge_json_files('input_dir/', 'output.json')
```

## Usage Examples

### 1. Extract Colors from VRay Chart

#### Single Image
```python
from avwv_preprocess.colors_from_vrayobjid import extract_vray_colors_from_objectIDs

# Extract from one chart image
colors = extract_vray_colors_from_objectIDs.extract_from_single_image(
    "data/input/color_charts/vrayobjectid_colors-strip_1-2048.png",
    output_path="data/vrayobjid_colors_1-2048_map.json"
)
# Returns: {'00001': '#FF0000', '0002': '#00FF00', ...}
```

#### Batch - Separate Files
```python
# Process multiple charts, save each result separately
results = extract_vray_colors_from_objectIDs.extract_batch_separate(
    input_dir="data/input/color_charts/",
    output_dir="data/colors_output/"
)
# Creates: colors_output/chart1.json, colors_output/chart2.json, ...
```

#### Batch - Merged
```python
# Process multiple charts, merge into single file
all_colors = extract_vray_colors_from_objectIDs.extract_batch_merged(
    input_dir="data/input/color_charts/",
    output_path="data/vrayobjid_colors_all_map.json"
)
# Returns merged dictionary of all colors
```

### 2. Extract Polygons from Mask Images

#### Single Mask
```python
from avwv_preprocess.objid_to_polygon import objID_to_polygon

# Extract polygons from mask using color map
polygons = objID_to_polygon.extract_from_single_mask(
    mask_path="data/input/masks/WebViewer_t1-1_0001.VRayObjectID.png",
    color_map="data/vrayobjid_colors_all_map.json",  # Can be path or dict
    output_path="data/output/polygons/WebViewer_t1-1_0001.json",
    epsilon=2.0,           # Polygon simplification
    tolerance=0            # Color matching tolerance
)
# Returns: {'00001': [[x1,y1], [x2,y2], ...], ...}
```

#### Batch - Separate Files
```python
# Process multiple masks, save each result separately
results = objID_to_polygon.extract_batch_separate(
    input_dir="masks/",
    color_map="data/vrayobjid_colors_all_map.json",
    output_dir="polygons_output/",
    epsilon=2.0,
    tolerance=0
)
```

#### Batch - Merged by Frame
```python
# Process multiple masks, organize by frame in single file
all_polygons = objID_to_polygon.extract_batch_merged(
    input_dir="masks/",
    color_map="data/vrayobjid_colors_all_map.json",
    output_path="all_frames.json",
    epsilon=2.0,
    tolerance=0
)
# Returns: {'0001': {'00001': [...], ...}, '0002': {...}, ...}
```

### 3. Convert Images to WebP/AVIF

#### Single Image
```python
from avwv_preprocess.image_converter import pipeline

pipeline.process_single_image(
    "input/image.png",
    "output/image.webp",
    quality=85,
    output_format='webp'
)
```

#### Batch Conversion
```python
pipeline.process_batch(
    "input_directory/",
    "output_directory/",
    quality=90,
    output_format='avif',
    remove_string="_source_file"
)
```

## Command Line Interface

### Colors from VRay ObjID

```bash
# Process single chart
python -m avwv_preprocess.cli.colors_from_vrayobjid single \
    data/input/color_charts/vrayobjectid_colors-strip_1-2048.png \
    -o data/vrayobjid_colors_1-2048_map.json \
    -i 1

python -m avwv_preprocess.cli.colors_from_vrayobjid single \
    data/input/color_charts/vrayobjectid_colors-chart_0-65535-1K.png \
    -t chart \
    -o data/vrayobjid_colors_all_map.json \
    -i 0

# Batch process separate
python -m avwv_preprocess.cli.colors_from_vrayobjid batch \
    data/input/color_charts/ \
    -o data/output/colors_maps/

# Batch process with merge
python -m avwv_preprocess.cli.colors_from_vrayobjid batch \
    data/input/color_charts/ \
    -m --merge-output data/vrayobjid_all_colors_map.json
```

### ObjID to Polygon

```bash
# Process single mask
python -m avwv_preprocess.cli.objid_to_polygon_cli single \
    data/input/masks/WebViewer_t1-1_0001.VRayObjectID.png \
    data/vrayobjid_colors_all_map.json \
    -o data/output/polygons/WebViewer_t1-1_0001.json \
    --epsilon 2.0 \
    --tolerance 0

python -m avwv_preprocess.cli.objid_to_polygon_cli single \
    "Z:\!Projekty\!Image\!R&D\Web viewer rotator\WebViewer scena testowa1\render\VRayObjectID\WebViewer_t1-1_0003.VRayObjectID.png" \
    data/vrayobjid_colors_all_map.json \
    -o data/output/polygons/polygons.json \
    --epsilon 2.0 \
    --tolerance 0

# Batch process separate
python -m avwv_preprocess.cli.objid_to_polygon_cli batch \
    data/input/masks/ \
    data/vrayobjid_colors_all_map.json \
    -o data/output/polygons/ \
    --remove-string ".VRayObjectID"

# Batch process separate
python -m avwv_preprocess.cli.objid_to_polygon_cli batch \
    "Z:\!Projekty\!Image\!R&D\Web viewer rotator\WebViewer scena testowa1\render\test" \
    data/vrayobjid_colors_all_map.json \
    -o data/output/polygons/v4_test \
    --auto-names

# Batch process separate with auto names
python -m avwv_preprocess.cli.objid_to_polygon_cli batch \
    "Z:\!Projekty\!Image\!R&D\Web viewer rotator\WebViewer scena testowa1\render\test\VRayObjectID" \
    data/vrayobjid_colors_all_map.json \
    -o data/output/polygons/v3 \
    --remove-string "_vrayoutput_.VRayObjectID."

# Batch process with merge
python -m avwv_preprocess.cli.objid_to_polygon_cli batch \
    data/input/masks/ \
    data/vrayobjid_colors_all_map.json \
    -m --merge-output data/output/polygons/all_frames.json \
    --remove-string ".VRayObjectID"
```

### Image Converter

```bash
# Convert a single image to WebP with quality 85
python -m avwv_preprocess.cli.image_converter_cli single \
    data/input/beauty_pass/WebViewer_t1-1_0001.RGB_color.png \
    data/output/beauty_pass_WebP/image.webp \
    --quality 85 \
    --format webp


# Batch convert a directory to WebP, removing ".RGB_color" from filenames
python -m avwv_preprocess.cli.image_converter_cli batch \
    "Z:\!Projekty\!Image\!R&D\Web viewer rotator\WebViewer scena testowa1\render\RGB_color" \
    data/output/beauty_pass_WebP/v3/ \
    --quality 85 \
    --format webp \
    --remove-string ".RGB_color"



```

### Full Asset Processing

The `full_asset_process` command processes an asset tree in one run. It searches
recursively for image files based on their immediate parent folder:

- `RGB_color` images are converted to the selected image format.
- `VRayObjectID` images are converted to polygon JSON files using the color map.

For each input filename, the asset ID is the text before the first `_` and the
frame number is the final four digits. Output files use the format
`<id>_<frame number>.<extension>` and are organized as follows:

```
<output path>/
└── <id>/
    ├── rotator_frames/
    │   └── <id>_<frame number>.<image format>
    └── rotator_polygons/
        └── <id>_<frame number>.json
```

The color map can be supplied with `--color-map`. When omitted, the command
looks for `vrayobjid_colors_all_map.json` in the input directory, its parent
directory, and `data/` in the current working directory.

The existing batch commands also support automatic naming with `--auto-names`:

```bash
python -m avwv_preprocess.cli.image_converter_cli batch \
    data/input/ \
    data/output/ \
    --format webp \
    --auto-names

python -m avwv_preprocess.cli.objid_to_polygon_cli batch \
    data/input/ \
    data/vrayobjid_colors_all_map.json \
    -o data/output/ \
    --auto-names

# Recursively convert RGB_color assets and extract VRayObjectID polygons
python -m avwv_preprocess.cli.full_asset_process \
    "Z:\!Projekty\!Image\!R&D\Web viewer rotator\WebViewer scena testowa1\render\v4" \
    data/output/v4 \
    webp \
    --color-map data/vrayobjid_colors_all_map.json
```

## Advanced Configuration

### Custom Color Tolerance
When extracting polygons, use tolerance to match colors with slight variations:

```python
# Exact color matching (default)
polygons = objID_to_polygon.extract_from_single_mask(
    mask_path, color_map, tolerance=0
)

# Fuzzy matching (±5 per channel)
polygons = objID_to_polygon.extract_from_single_mask(
    mask_path, color_map, tolerance=5
)
```

### Polygon Simplification
Use epsilon to control polygon complexity:

```python
# Simple polygons (fewer points)
polygons = objID_to_polygon.extract_from_single_mask(
    mask_path, color_map, epsilon=5.0
)

# Detailed polygons (more points, closer to original)
polygons = objID_to_polygon.extract_from_single_mask(
    mask_path, color_map, epsilon=0.5
)
```

### Extract Largest Region Only
When multiple regions exist for one color, extract only the largest:

```python
from avwv_preprocess.objid_to_polygon.processor import extract_largest_polygon_per_color

polygons = extract_largest_polygon_per_color(
    image, color_map, epsilon=2.0, tolerance=0
)
```

## Output Formats

### Color Extraction Output
```json
{
  "00001": "#FF0000",
  "00002": "#00FF00",
  "00003": "#0000FF"
}
```

### Polygon Extraction Output (Single)
```json
{
  "00001": [[x1, y1], [x2, y2], [x3, y3]],
  "00002": [[x1, y1], [x2, y2], ...],
  "00003": [[x1, y1], [x2, y2], [x3, y3]]
}
```

### Polygon Extraction Output (Merged by Frame)
```json
{
  "0001": {
    "00001": [[x1, y1], [x2, y2], [x3, y3]],
    "00002": [[x1, y1], ...],
  },
  "0002": {
    "00001": [[x1, y1], ...],
    ...
  }
}
```

## Error Handling

All functions include comprehensive error handling:

```python
from avwv_preprocess.objid_to_polygon import objID_to_polygon

try:
    polygons = objID_to_polygon.extract_from_single_mask(
        mask_path, color_map, output_path
    )
except FileNotFoundError as e:
    print(f"File not found: {e}")
except Exception as e:
    print(f"Processing failed: {e}")
```

## Performance Considerations

### Batch Processing
- Processes files sequentially for stability
- Reports progress and errors for each file
- Continue on error (partial results preserved)
- Each file is independent, suitable for parallelization

### Memory Usage
- Images loaded one at a time
- Color processing per unit ID (not per pixel)
- Large batches completed without memory issues
- Results organized by frame for large datasets

## Integration with CLI Tools

The modules are also available as Click/Click-style commands for integration with other CLI frameworks:

```python
from avwv_preprocess.cli import colors_from_vrayobjid, objid_to_polygon_cli

# Can be integrated into larger CLI applications
# Each command follows standard argparse conventions
```

## Extending the Module

### Adding New Processors
1. Add processing function to `processor.py`
2. Wrap in pipeline functions in `pipeline.py`
3. Export via `Public API` module
4. Add CLI command in `cli/`

### Custom Color Maps
Color maps can be passed as:
- Path to JSON file
- Python dictionary

```python
# From file
polygons = objID_to_polygon.extract_from_single_mask(
    mask_path, "data/vrayobjid_colors_all_map.json"
)

# From dict
color_map = {"00001": "#FF0000", ...}
polygons = objID_to_polygon.extract_from_single_mask(
    mask_path, color_map
)
```

## Testing

The modular architecture makes unit testing straightforward:

```python
from avwv_preprocess.colors_from_vrayobjid.processor import extract_colors_from_chart
from avwv_preprocess.objid_to_polygon.processor import extract_polygons_from_mask

# Test processor directly (no I/O)
test_image = cv2.imread("test.png")
result = extract_polygons_from_mask(test_image, test_color_map)
assert len(result) > 0
```

---

For more details on specific functions, see docstrings in source files.
