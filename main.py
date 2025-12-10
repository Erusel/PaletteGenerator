"""
Main entry point for the PNG recoloring script.
Can run as CLI or launch the Streamlit web app.
"""

import os
import sys
from pathlib import Path
from PIL import Image

from palettes import get_source_palettes, get_palette_groups
from recolor import recolor_image


# Define folder paths
ASSETS_FOLDER = Path("assets")
GENERATED_FOLDER = Path("generated")


def ensure_folder_exists(folder_path:  Path) -> None:
    """Create a folder if it doesn't exist."""
    folder_path.mkdir(parents=True, exist_ok=True)


def get_png_files(folder:  Path) -> list:
    """Get all PNG files in a folder."""
    if not folder.exists():
        print(f"Warning: Folder '{folder}' does not exist.")
        return []
    return list(folder.glob("*.png")) + list(folder.glob("*. PNG"))


def process_image(
    image_path: Path,
    source_palette: list,
    palette_groups: dict
) -> None:
    """Process a single image with all palette groups and their palettes."""
    basename = image_path.stem
    print(f"Processing: {image_path. name}")

    try:
        source_image = Image.open(str(image_path))
    except Exception as e:
        print(f"  Error loading image: {e}")
        return

    ensure_folder_exists(GENERATED_FOLDER)

    for group_name, palettes in palette_groups.items():
        print(f"  Group: {group_name}")

        for palette_name, target_palette in palettes.items():
            print(f"    Generating {palette_name} version...")

            recolored_image = recolor_image(source_image, source_palette, target_palette)

            # Output format: nameofthefile_palettename.png
            output_path = GENERATED_FOLDER / f"{basename}_{palette_name}. png"
            recolored_image.save(str(output_path), "PNG")
            print(f"      Saved: {output_path}")


def run_cli():
    """Run the command-line interface version."""
    print("=" * 50)
    print("PNG Recoloring Script (CLI Mode)")
    print("=" * 50)
    print()

    ensure_folder_exists(ASSETS_FOLDER)
    ensure_folder_exists(GENERATED_FOLDER)

    png_files = get_png_files(ASSETS_FOLDER)

    if not png_files:
        print(f"No PNG files found in '{ASSETS_FOLDER}/'")
        print("Please add PNG files to the assets/ folder and run again.")
        return

    print(f"Found {len(png_files)} PNG file(s) to process.")
    print()

    # Get palettes
    source_palettes = get_source_palettes()
    palette_groups = get_palette_groups()

    # Count total palettes
    total_palettes = sum(len(palettes) for palettes in palette_groups.values())
    print(f"Found {len(palette_groups)} group(s) with {total_palettes} total palette(s).")
    print()

    # Use default source palette
    source_palette = source_palettes. get("Default", list(source_palettes.values())[0])

    for png_path in png_files:
        process_image(png_path, source_palette, palette_groups)
        print()

    print("=" * 50)
    print("Processing complete!")
    print(f"Output format: filename_palettename.png")
    print(f"Check the '{GENERATED_FOLDER}/' folder for output.")
    print("=" * 50)


def run_webapp():
    """Launch the Streamlit web application."""
    import subprocess
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--web":
        print("Launching Streamlit web application...")
        run_webapp()
    else:
        run_cli()


if __name__ == "__main__":
    main()