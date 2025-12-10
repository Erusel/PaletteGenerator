
"""
Color replacement logic for PNG recoloring. 
Handles pixel-perfect color matching and RGBA image support.
"""

from PIL import Image
from typing import List, Tuple
import io


def recolor_image(
    image: Image.Image,
    source_palette: List[Tuple[int, int, int]],
    target_palette: List[Tuple[int, int, int]]
) -> Image.Image:
    """
    Replace colors in an image from source palette to target palette. 

    Performs pixel-perfect (exact) color matching. Only pixels that exactly
    match a source color will be replaced.   Alpha channel is preserved.

    Args:
        image: PIL Image object to process
        source_palette: List of RGB tuples representing colors to find
        target_palette: List of RGB tuples representing replacement colors

    Returns:
        New PIL Image with colors replaced
    """
    # Ensure we're working with RGBA for consistent handling
    image = image.convert("RGBA")

    # Get pixel data
    pixels = image.load()
    width, height = image.size

    # Create a mapping from source colors to target colors
    color_map = {}
    for source_color, target_color in zip(source_palette, target_palette):
        color_map[source_color] = target_color

    # Create a new image for the output
    output_image = Image. new("RGBA", (width, height))
    output_pixels = output_image.load()

    # Process each pixel
    for y in range(height):
        for x in range(width):
            # Get the current pixel (R, G, B, A)
            current_pixel = pixels[x, y]
            r, g, b, a = current_pixel

            # Extract RGB for comparison
            rgb = (r, g, b)

            # Check if this color is in our source palette
            if rgb in color_map:
                # Replace with target color, preserving alpha
                new_rgb = color_map[rgb]
                output_pixels[x, y] = (new_rgb[0], new_rgb[1], new_rgb[2], a)
            else:
                # Keep original pixel unchanged
                output_pixels[x, y] = current_pixel

    return output_image


def create_emissive_texture(
    image: Image.Image,
    source_palette: List[Tuple[int, int, int]],
    target_palette: List[Tuple[int, int, int]]
) -> Image.Image:
    """
    Create an emissive texture showing only the recolored pixels. 

    Only pixels that match the source palette are visible (with target colors).
    All other pixels are made fully transparent.

    Args:
        image: PIL Image object to process
        source_palette: List of RGB tuples representing colors to find
        target_palette: List of RGB tuples representing replacement colors

    Returns: 
        New PIL Image with only recolored pixels visible, rest transparent
    """
    # Ensure we're working with RGBA for consistent handling
    image = image. convert("RGBA")

    # Get pixel data
    pixels = image.load()
    width, height = image.size

    # Create a mapping from source colors to target colors
    color_map = {}
    for source_color, target_color in zip(source_palette, target_palette):
        color_map[source_color] = target_color

    # Create a new image for the output
    output_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    output_pixels = output_image.load()

    # Process each pixel
    for y in range(height):
        for x in range(width):
            # Get the current pixel (R, G, B, A)
            current_pixel = pixels[x, y]
            r, g, b, a = current_pixel

            # Extract RGB for comparison
            rgb = (r, g, b)

            # Only keep pixels that were recolored
            if rgb in color_map: 
                # Use target color, preserving alpha
                new_rgb = color_map[rgb]
                output_pixels[x, y] = (new_rgb[0], new_rgb[1], new_rgb[2], a)
            # All other pixels remain transparent (already initialized to 0,0,0,0)

    return output_image


def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
    """
    Load an image from bytes data. 

    Args:
        image_bytes: Image data as bytes

    Returns: 
        PIL Image object
    """
    return Image.open(io. BytesIO(image_bytes))


def image_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
    """
    Convert a PIL Image to bytes.

    Args:
        image: PIL Image object
        format: Output format (default: PNG)

    Returns:
        Image data as bytes
    """
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return buffer.getvalue()