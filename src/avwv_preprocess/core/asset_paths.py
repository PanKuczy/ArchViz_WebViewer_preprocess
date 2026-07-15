from pathlib import Path
import re


IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.webp'}


def find_asset_files(input_dir, parent_name):
    root = Path(input_dir)
    return sorted(
        (
            path for path in root.rglob('*')
            if path.is_file()
            and path.suffix.lower() in IMAGE_SUFFIXES
            and path.parent.name == parent_name
        ),
        key=lambda path: (asset_id(path), frame_number(path), str(path).lower()),
    )


def asset_id(path):
    return Path(path).stem.split('_', 1)[0]


def frame_number(path):
    match = re.search(r'(\d{4})$', Path(path).stem)
    if match is None:
        raise ValueError(f"Asset filename must end with four digits: {path}")
    return match.group(1)


def auto_name(path, extension):
    return f'{asset_id(path)}_{frame_number(path)}.{extension.lstrip(".")}'