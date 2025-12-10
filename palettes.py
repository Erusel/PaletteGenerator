"""
Palette definitions for the PNG recoloring script.
Contains the source palette (colors to detect) and target palettes (replacement colors).
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

# File to store custom palettes
PALETTES_FILE = Path("custom_palettes.json")


def hex_to_rgb(hex_color: str) -> tuple:
    """
    Convert a hex color string to an RGB tuple.

    Args:
        hex_color:  Hex color string (e.g., "FBFBFB" or "#FBFBFB")

    Returns:
        Tuple of (R, G, B) values as integers (0-255)
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple) -> str:
    """
    Convert an RGB tuple to a hex color string.

    Args:
        rgb:  Tuple of (R, G, B) values as integers (0-255)

    Returns:
        Hex color string with '#' prefix
    """
    return "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])


# Default source palette - colors to detect and replace
DEFAULT_SOURCE_PALETTE = [
    hex_to_rgb("FBFBFB"),  # Index 1: Light gray/white
    hex_to_rgb("CAC1D1"),  # Index 2: Light purple-gray
    hex_to_rgb("9788A2"),  # Index 3: Medium purple-gray
    hex_to_rgb("6A5976"),  # Index 4: Dark purple-gray
]

# Default target palettes - replacement colors for each theme
DEFAULT_TARGET_PALETTES = {
    "Purple": [
        hex_to_rgb("B23CED"),
        hex_to_rgb("8734C3"),
        hex_to_rgb("672FA0"),
        hex_to_rgb("582888"),
    ],
    "Magenta": [
        hex_to_rgb("ED3CED"),
        hex_to_rgb("B634C3"),
        hex_to_rgb("8D2FA0"),
        hex_to_rgb("782888"),
    ],
    "Pink": [
        hex_to_rgb("FF42B5"),
        hex_to_rgb("D53DA2"),
        hex_to_rgb("A33788"),
        hex_to_rgb("8B2F74"),
    ],
}

# Default palette groups
DEFAULT_PALETTE_GROUPS = {
    "All Colors": ["Purple", "Magenta", "Pink"],
    "Warm Tones": ["Magenta", "Pink"],
    "Cool Tones": ["Purple"],
}


def load_custom_data() -> dict:
    """Load custom palettes and groups from JSON file."""
    if PALETTES_FILE.exists():
        try:
            with open(PALETTES_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    return {
        "source_palettes": {
            "Default": [rgb_to_hex(c) for c in DEFAULT_SOURCE_PALETTE]
        },
        "target_palettes": {
            name: [rgb_to_hex(c) for c in colors]
            for name, colors in DEFAULT_TARGET_PALETTES. items()
        },
        "palette_groups": DEFAULT_PALETTE_GROUPS
    }


def save_custom_data(data: dict) -> None:
    """Save custom palettes and groups to JSON file."""
    with open(PALETTES_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def get_source_palettes() -> Dict[str, List[Tuple[int, int, int]]]:
    """Get all source palettes as RGB tuples."""
    data = load_custom_data()
    return {
        name: [hex_to_rgb(c) for c in colors]
        for name, colors in data. get("source_palettes", {}).items()
    }


def get_target_palettes() -> Dict[str, List[Tuple[int, int, int]]]:
    """Get all target palettes as RGB tuples."""
    data = load_custom_data()
    return {
        name:  [hex_to_rgb(c) for c in colors]
        for name, colors in data.get("target_palettes", {}).items()
    }


def get_palette_groups() -> Dict[str, List[str]]:
    """Get all palette groups."""
    data = load_custom_data()
    return data.get("palette_groups", {})


def add_source_palette(name: str, colors: List[str]) -> bool:
    """Add a new source palette."""
    data = load_custom_data()
    if "source_palettes" not in data:
        data["source_palettes"] = {}
    data["source_palettes"][name] = colors
    save_custom_data(data)
    return True


def add_target_palette(name: str, colors: List[str]) -> bool:
    """Add a new target palette."""
    data = load_custom_data()
    if "target_palettes" not in data:
        data["target_palettes"] = {}
    data["target_palettes"][name] = colors
    save_custom_data(data)
    return True


def delete_source_palette(name: str) -> bool:
    """Delete a source palette."""
    data = load_custom_data()
    if name in data. get("source_palettes", {}):
        del data["source_palettes"][name]
        save_custom_data(data)
        return True
    return False


def delete_target_palette(name: str) -> bool:
    """Delete a target palette and remove from groups."""
    data = load_custom_data()
    if name in data.get("target_palettes", {}):
        del data["target_palettes"][name]
        # Remove from all groups
        for group_name, palettes in data.get("palette_groups", {}).items():
            if name in palettes:
                palettes.remove(name)
        save_custom_data(data)
        return True
    return False


def add_palette_group(name: str, palette_names: List[str]) -> bool:
    """Add a new palette group."""
    data = load_custom_data()
    if "palette_groups" not in data:
        data["palette_groups"] = {}
    data["palette_groups"][name] = palette_names
    save_custom_data(data)
    return True


def update_palette_group(name: str, palette_names: List[str]) -> bool:
    """Update an existing palette group."""
    data = load_custom_data()
    if name in data.get("palette_groups", {}):
        data["palette_groups"][name] = palette_names
        save_custom_data(data)
        return True
    return False


def delete_palette_group(name: str) -> bool:
    """Delete a palette group."""
    data = load_custom_data()
    if name in data.get("palette_groups", {}):
        del data["palette_groups"][name]
        save_custom_data(data)
        return True
    return False


def export_palettes_json() -> str:
    """Export all palettes and groups as JSON string."""
    data = load_custom_data()
    return json.dumps(data, indent=2)


def import_palettes_json(json_string: str) -> bool:
    """Import palettes and groups from JSON string."""
    try:
        data = json.loads(json_string)
        # Validate structure
        if "source_palettes" in data or "target_palettes" in data or "palette_groups" in data:
            current_data = load_custom_data()
            if "source_palettes" in data:
                current_data["source_palettes"]. update(data["source_palettes"])
            if "target_palettes" in data:
                current_data["target_palettes"]. update(data["target_palettes"])
            if "palette_groups" in data:
                current_data["palette_groups"].update(data["palette_groups"])
            save_custom_data(current_data)
            return True
    except (json.JSONDecodeError, KeyError):
        pass
    return False