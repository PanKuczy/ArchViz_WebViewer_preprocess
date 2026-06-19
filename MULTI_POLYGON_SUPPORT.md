# Multiple Polygon Support - Updated Polygon Extraction

## Overview

The polygon extraction has been updated to properly handle multiple contours for the same color. Three extraction modes are now available:

### 1. **Compound Polygons** (Default)
When multiple contours exist for a color, they're returned as a list of polygons:

```json
{
  "0001": [
    [[x1,y1], [x2,y2], [x3,y3]],
    [[x1,y1], [x2,y2], [x3,y3]]
  ]
}
```

**Usage:**
```python
from avwv_preprocess.objid_to_polygon import objID_to_polygon

polygons = objID_to_polygon.extract_from_single_mask(
    mask_path="mask.png",
    color_map="colors.json"
)
```

### 2. **Union Merge** (New)
Multiple contours are merged via union into a single polygon:

```json
{
  "0001": [[x1,y1], [x2,y2], [x3,y3]]
}
```

**Usage (Programmatic):**
```python
from avwv_preprocess.objid_to_polygon.processor import merge_polygons_via_union
from avwv_preprocess.core.image_io import load_image
from avwv_preprocess.core.json_io import load_json

image = load_image("mask.png")
color_map = load_json("colors.json")

polygons = merge_polygons_via_union(
    image, color_map, epsilon=2.0, tolerance=0
)
```

### 3. **Largest Contour Only**
Only the largest polygon is extracted per color:

```json
{
  "0001": [[x1,y1], [x2,y2], [x3,y3]]
}
```

**Usage:**
```python
from avwv_preprocess.objid_to_polygon.processor import extract_largest_polygon_per_color

polygons = extract_largest_polygon_per_color(
    image, color_map, epsilon=2.0, tolerance=0
)
```

## Processor Functions

### `extract_polygons_from_mask()` (Default - Compound)
```python
from avwv_preprocess.objid_to_polygon.processor import extract_polygons_from_mask

result = extract_polygons_from_mask(
    image,           # OpenCV image array
    color_to_id_map, # Color map dict
    epsilon=2.0,     # Polygon simplification
    tolerance=0      # Color matching tolerance
)
```

**Returns:**
- Single polygon if one contour: `{"id": [[x,y], ...]}`
- Compound polygon if multiple contours: `{"id": [[[x,y], ...], [[x,y], ...]]}`

### `merge_polygons_via_union()`
```python
from avwv_preprocess.objid_to_polygon.processor import merge_polygons_via_union

result = merge_polygons_via_union(
    image,           # OpenCV image array
    color_to_id_map, # Color map dict
    epsilon=2.0,     # Polygon simplification
    tolerance=0      # Color matching tolerance
)
```

**Returns:**
- Always a single polygon per ID: `{"id": [[x,y], ...]}`
- Uses convex hull of all contours

### `extract_largest_polygon_per_color()`
```python
from avwv_preprocess.objid_to_polygon.processor import extract_largest_polygon_per_color

result = extract_largest_polygon_per_color(
    image,           # OpenCV image array
    color_to_id_map, # Color map dict
    epsilon=2.0,     # Polygon simplification
    tolerance=0      # Color matching tolerance
)
```

**Returns:**
- Single largest polygon per ID: `{"id": [[x,y], ...]}`

## CLI Usage

### Single Mask with Compound Polygons (Default)
```bash
python -m avwv_preprocess.cli.objid_to_polygon_cli single \
  "mask.png" \
  "colors.json" \
  -o output.json
```

### Single Mask Options
```bash
# Default (compound polygons for multiple contours)
python -m avwv_preprocess.cli.objid_to_polygon_cli single \
  mask.png colors.json -o output.json

# Options:
# -e, --epsilon    : Polygon simplification (default: 2.0)
# -t, --tolerance  : Color matching tolerance (default: 0)
```

### Batch Processing
```bash
# Process multiple masks (default compound mode)
python -m avwv_preprocess.cli.objid_to_polygon_cli batch \
  input/masks/ \
  colors.json \
  -o output/

# Batch with merge
python -m avwv_preprocess.cli.objid_to_polygon_cli batch \
  input/masks/ \
  colors.json \
  -m --merge-output all_frames.json
```

## Output Format Examples

### Compound Polygon Format (Multiple Contours)
```json
{
  "0001": [
    [[10, 20], [30, 40], [50, 10]],
    [[100, 100], [150, 120], [120, 180]]
  ],
  "0002": [[5, 5], [10, 10], [15, 5]]
}
```

### Union Merge Format (Single Polygon)
```json
{
  "0001": [[10, 20], [150, 120], [50, 180], [5, 5]],
  "0002": [[5, 5], [10, 10], [15, 5]]
}
```

### Largest Contour Format
```json
{
  "0001": [[10, 20], [30, 40], [50, 10]],
  "0002": [[5, 5], [10, 10], [15, 5]]
}
```

## Processing Multiple Contours for Same Color

### HTML Rendering Considerations

**Compound Polygons:**
- Multiple polygons can be rendered as separate shapes
- Good for maintaining original geometry
- Requires multi-polygon support in visualization

**Union Merge:**
- Single polygon encompasses all regions
- Creates convex hull boundary
- May include unwanted area between disconnected regions
- Simpler for rendering

**Largest Contour:**
- Single largest region only
- Simple to render
- Loss of smaller regions

## Code Example: Processing with Different Modes

```python
from avwv_preprocess.objid_to_polygon import objID_to_polygon
from avwv_preprocess.objid_to_polygon.processor import (
    extract_polygons_from_mask,
    extract_largest_polygon_per_color,
    merge_polygons_via_union
)
from avwv_preprocess.core.image_io import load_image
from avwv_preprocess.core.json_io import load_json, save_json

# Load data
image = load_image("mask.png")
color_map = load_json("colors.json")

# Method 1: Compound polygons (default)
compound = extract_polygons_from_mask(image, color_map, epsilon=2.0)
save_json(compound, "output_compound.json")

# Method 2: Union merge (single polygon per color)
merged = merge_polygons_via_union(image, color_map, epsilon=2.0)
save_json(merged, "output_merged.json")

# Method 3: Largest only
largest = extract_largest_polygon_per_color(image, color_map, epsilon=2.0)
save_json(largest, "output_largest.json")
```

## Detection: How to Tell Format in Output

```python
import json

with open("output.json") as f:
    data = json.load(f)

for obj_id, polygons in data.items():
    if isinstance(polygons[0][0], list):
        # Compound format: [[x,y], [x,y], ...] at position [0][0]
        print(f"{obj_id}: Compound polygon with {len(polygons)} regions")
    else:
        # Single format: [x,y] at position [0]
        print(f"{obj_id}: Single polygon")
```

## Performance Notes

- **Compound Polygons:** Fastest extraction, minimal processing
- **Union Merge:** Slightly slower (convex hull computation), single output
- **Largest Only:** Fast (max by area comparison)

## Migration from Old Version

If you had code expecting single polygons:

```python
# OLD CODE (would fail on compound polygons)
for obj_id, points in polygons.items():
    render_polygon(points)

# NEW CODE (handles both formats)
for obj_id, data in polygons.items():
    if isinstance(data[0][0], list):
        # Compound: multiple polygons
        for points in data:
            render_polygon(points)
    else:
        # Single polygon
        render_polygon(data)
```

Or use `merge_polygons_via_union()` to ensure single polygons only.
