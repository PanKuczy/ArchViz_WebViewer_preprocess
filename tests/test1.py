
from avwv_preprocess.core.json_io import load_json
from avwv_preprocess.core.image_io import load_image

from avwv_preprocess.colors_from_vrayobjid.processor import extract_colors_from_chart
from avwv_preprocess.objid_to_polygon.processor import extract_polygons_from_mask

# Test processor directly (no I/O)
test_image = load_image("data/input/WebViewer_t1-1_0002.VRayObjectID.png")
test_color_map = load_json('tests/chart.json')
result = extract_polygons_from_mask(test_image, test_color_map)
assert len(result) > 0
print(result)