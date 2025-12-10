"""
Palette definitions for the PNG recoloring script.
Palettes are organized by groups, allowing same palette names in different groups.
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
        hex_color:   Hex color string (e.g., "FBFBFB" or "#FBFBFB")

    Returns:
        Tuple of (R, G, B) values as integers (0-255)
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb:  tuple) -> str:
    """
    Convert an RGB tuple to a hex color string.

    Args:
        rgb:  Tuple of (R, G, B) values as integers (0-255)

    Returns:
        Hex color string with '#' prefix
    """
    return "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])


def get_default_data() -> dict:
    """Get default palette data structure (empty)."""
    return {
        "source_palettes": {},
        "palette_groups": {}
    }


def load_custom_data() -> dict:
    """Load custom palettes and groups from JSON file."""
    if PALETTES_FILE.exists():
        try:
            with open(PALETTES_FILE, 'r') as f:
                data = json.load(f)
                # Ensure required keys exist
                if "source_palettes" not in data:
                    data["source_palettes"] = {}
                if "palette_groups" not in data:
                    data["palette_groups"] = {}
                return data
        except (json.JSONDecodeError, IOError):
            pass

    return get_default_data()


def save_custom_data(data: dict) -> None:
    """Save custom palettes and groups to JSON file."""
    with open(PALETTES_FILE, 'w') as f:
        json.dump(data, f, indent=2)


# ============ SOURCE PALETTE FUNCTIONS ============

def get_source_palettes() -> Dict[str, List[Tuple[int, int, int]]]:
    """Get all source palettes as RGB tuples."""
    data = load_custom_data()
    return {
        name: [hex_to_rgb(c) for c in colors]
        for name, colors in data. get("source_palettes", {}).items()
    }


def add_source_palette(name: str, colors: List[str]) -> bool:
    """Add a new source palette."""
    data = load_custom_data()
    if "source_palettes" not in data:
        data["source_palettes"] = {}
    data["source_palettes"][name] = colors
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


# ============ PALETTE GROUP FUNCTIONS ============

def get_palette_groups() -> Dict[str, Dict[str, List[Tuple[int, int, int]]]]:
    """
    Get all palette groups with their palettes as RGB tuples.

    Returns:
        Dict structure: { "GroupName": { "PaletteName": [(R,G,B), ...] } }
    """
    data = load_custom_data()
    result = {}
    for group_name, palettes in data.get("palette_groups", {}).items():
        result[group_name] = {
            palette_name: [hex_to_rgb(c) for c in colors]
            for palette_name, colors in palettes.items()
        }
    return result


def get_palette_groups_hex() -> Dict[str, Dict[str, List[str]]]:
    """
    Get all palette groups with their palettes as hex strings.

    Returns:
        Dict structure: { "GroupName": { "PaletteName":  ["#RRGGBB", ...] } }
    """
    data = load_custom_data()
    return data.get("palette_groups", {})


def get_group_names() -> List[str]:
    """Get list of all group names."""
    data = load_custom_data()
    return list(data.get("palette_groups", {}).keys())


def get_palettes_in_group(group_name: str) -> Dict[str, List[Tuple[int, int, int]]]:
    """
    Get all palettes in a specific group as RGB tuples.

    Args:
        group_name:  Name of the group

    Returns:
        Dict:  { "PaletteName": [(R,G,B), ...] }
    """
    data = load_custom_data()
    group_data = data.get("palette_groups", {}).get(group_name, {})
    return {
        palette_name: [hex_to_rgb(c) for c in colors]
        for palette_name, colors in group_data.items()
    }


def add_palette_group(group_name: str) -> bool:
    """Create a new empty palette group."""
    data = load_custom_data()
    if "palette_groups" not in data:
        data["palette_groups"] = {}
    if group_name not in data["palette_groups"]:
        data["palette_groups"][group_name] = {}
        save_custom_data(data)
        return True
    return False


def delete_palette_group(group_name: str) -> bool:
    """Delete a palette group and all its palettes."""
    data = load_custom_data()
    if group_name in data. get("palette_groups", {}):
        del data["palette_groups"][group_name]
        save_custom_data(data)
        return True
    return False


def rename_palette_group(old_name: str, new_name:  str) -> bool:
    """Rename a palette group."""
    data = load_custom_data()
    if old_name in data.get("palette_groups", {}) and new_name not in data["palette_groups"]:
        data["palette_groups"][new_name] = data["palette_groups"]. pop(old_name)
        save_custom_data(data)
        return True
    return False


# ============ PALETTE FUNCTIONS (within groups) ============

def add_palette_to_group(group_name:  str, palette_name: str, colors: List[str]) -> bool:
    """
    Add a palette to a specific group.

    Args:
        group_name: Name of the group
        palette_name: Name of the palette
        colors: List of hex color strings
    """
    data = load_custom_data()
    if "palette_groups" not in data:
        data["palette_groups"] = {}
    if group_name not in data["palette_groups"]:
        data["palette_groups"][group_name] = {}

    data["palette_groups"][group_name][palette_name] = colors
    save_custom_data(data)
    return True


def update_palette_in_group(group_name: str, palette_name: str, colors: List[str]) -> bool:
    """Update a palette's colors in a specific group."""
    data = load_custom_data()
    if group_name in data.get("palette_groups", {}):
        if palette_name in data["palette_groups"][group_name]:
            data["palette_groups"][group_name][palette_name] = colors
            save_custom_data(data)
            return True
    return False


def delete_palette_from_group(group_name:  str, palette_name: str) -> bool:
    """Delete a palette from a specific group."""
    data = load_custom_data()
    if group_name in data.get("palette_groups", {}):
        if palette_name in data["palette_groups"][group_name]:
            del data["palette_groups"][group_name][palette_name]
            save_custom_data(data)
            return True
    return False


def rename_palette_in_group(group_name: str, old_name: str, new_name: str) -> bool:
    """Rename a palette within a group."""
    data = load_custom_data()
    if group_name in data.get("palette_groups", {}):
        group = data["palette_groups"][group_name]
        if old_name in group and new_name not in group:
            group[new_name] = group.pop(old_name)
            save_custom_data(data)
            return True
    return False


def copy_palette_to_group(
    source_group: str,
    palette_name: str,
    target_group: str,
    new_name: str = None
) -> bool:
    """Copy a palette from one group to another."""
    data = load_custom_data()
    if source_group in data.get("palette_groups", {}):
        if palette_name in data["palette_groups"][source_group]:
            colors = data["palette_groups"][source_group][palette_name]
            target_name = new_name or palette_name

            if target_group not in data["palette_groups"]:
                data["palette_groups"][target_group] = {}

            data["palette_groups"][target_group][target_name] = colors. copy()
            save_custom_data(data)
            return True
    return False


# ============ IMPORT/EXPORT FUNCTIONS ============

def export_palettes_json() -> str:
    """Export all palettes and groups as JSON string."""
    data = load_custom_data()
    return json.dumps(data, indent=2)


def import_palettes_json(json_string: str, merge:  bool = True) -> bool:
    """
    Import palettes and groups from JSON string.

    Args:
        json_string: JSON data to import
        merge: If True, merge with existing data.  If False, replace all.
    """
    try:
        imported_data = json.loads(json_string)

        if merge:
            current_data = load_custom_data()

            # Merge source palettes
            if "source_palettes" in imported_data:
                current_data["source_palettes"]. update(imported_data["source_palettes"])

            # Merge palette groups
            if "palette_groups" in imported_data:
                for group_name, palettes in imported_data["palette_groups"].items():
                    if group_name not in current_data["palette_groups"]:
                        current_data["palette_groups"][group_name] = {}
                    current_data["palette_groups"][group_name].update(palettes)

            save_custom_data(current_data)
        else:
            # Replace all data
            if "source_palettes" in imported_data or "palette_groups" in imported_data:
                new_data = get_default_data()
                if "source_palettes" in imported_data:
                    new_data["source_palettes"] = imported_data["source_palettes"]
                if "palette_groups" in imported_data:
                    new_data["palette_groups"] = imported_data["palette_groups"]
                save_custom_data(new_data)

        return True
    except (json.JSONDecodeError, KeyError):
        return False


# ============ UTILITY FUNCTIONS ============

def get_all_palettes_flat() -> Dict[str, Dict[str, List[Tuple[int, int, int]]]]:
    """
    Get all palettes organized by group for easy iteration.

    Returns:
        Dict: { "GroupName":  { "PaletteName": [(R,G,B), ...] } }
    """
    return get_palette_groups()


def get_unique_palette_identifier(group_name: str, palette_name: str) -> str:
    """
    Get a unique identifier for a palette (group/palette format).

    Args:
        group_name: Name of the group
        palette_name: Name of the palette

    Returns:
        String in format "GroupName/PaletteName"
    """
    return f"{group_name}/{palette_name}"


def parse_palette_identifier(identifier: str) -> Tuple[str, str]:
    """
    Parse a palette identifier back to group and palette names.

    Args:
        identifier: String in format "GroupName/PaletteName"

    Returns:
        Tuple of (group_name, palette_name)
    """
    parts = identifier.split("/", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return "", identifier