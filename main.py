"""
Main entry point for the PNG recoloring script.
Can run as CLI or launch the Streamlit web app.
"""

import os
import sys
from pathlib import Path
from PIL import Image

from palettes import get_source_palettes, get_target_palettes
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
    return list(folder.glob("*.png")) + list(folder.glob("*.PNG"))


def process_image(image_path: Path, source_palette: list, target_palettes: dict) -> None:
    """Process a single image with all target palettes."""
    basename = image_path.stem
    print(f"Processing:  {image_path.name}")

    try:
        source_image = Image.open(str(image_path))
    except Exception as e:
        print(f"  Error loading image: {e}")
        return

    output_folder = GENERATED_FOLDER / basename
    ensure_folder_exists(output_folder)

    for palette_name, target_palette in target_palettes.items():
        print(f"  Generating {palette_name} version...")

        recolored_image = recolor_image(source_image, source_palette, target_palette)

        output_path = output_folder / f"{palette_name}.png"
        recolored_image.save(str(output_path), "PNG")
        print(f"    Saved: {output_path}")


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
    target_palettes = get_target_palettes()

    # Use default source palette
    source_palette = source_palettes. get("Default", list(source_palettes.values())[0])

    for png_path in png_files:
        process_image(png_path, source_palette, target_palettes)
        print()

    print("=" * 50)
    print("Processing complete!")
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