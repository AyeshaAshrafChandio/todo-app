#!/usr/bin/env python3
"""Generate placeholder icons for the Todo application."""

import os
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL/Pillow not available, creating minimal placeholder icons")

# Theme color from manifest
THEME_COLOR = (59, 130, 246)  # #3b82f6
WHITE = (255, 255, 255)

def create_icon_with_pil(size, output_path, text="T"):
    """Create an icon with PIL/Pillow."""
    # Create image with theme color background
    img = Image.new('RGB', (size, size), THEME_COLOR)
    draw = ImageDraw.Draw(img)

    # Try to use a font, fall back to default if not available
    try:
        # Calculate font size based on image size
        font_size = int(size * 0.6)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(size * 0.6))
        except:
            font = ImageFont.load_default()

    # Draw text in center
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size - text_width) // 2, (size - text_height) // 2 - bbox[1])

    draw.text(position, text, fill=WHITE, font=font)

    # Save image
    if output_path.endswith('.ico'):
        img.save(output_path, format='ICO', sizes=[(size, size)])
    else:
        img.save(output_path, format='PNG')

    print(f"[OK] Created {output_path} ({size}x{size})")

def create_og_image_with_pil(output_path):
    """Create Open Graph image (1200x630) with text."""
    width, height = 1200, 630
    img = Image.new('RGB', (width, height), THEME_COLOR)
    draw = ImageDraw.Draw(img)

    # Try to use a font
    try:
        font_title = ImageFont.truetype("arial.ttf", 120)
        font_subtitle = ImageFont.truetype("arial.ttf", 48)
    except:
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
            font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
        except:
            font_title = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()

    # Draw title
    title = "Todo App"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = bbox[2] - bbox[0]
    title_x = (width - title_width) // 2
    title_y = height // 2 - 80
    draw.text((title_x, title_y), title, fill=WHITE, font=font_title)

    # Draw subtitle
    subtitle = "Manage your tasks efficiently"
    bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    subtitle_width = bbox[2] - bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = title_y + 140
    draw.text((subtitle_x, subtitle_y), subtitle, fill=WHITE, font=font_subtitle)

    img.save(output_path, format='PNG')
    print(f"[OK] Created {output_path} ({width}x{height})")

def create_minimal_png(size, output_path):
    """Create a minimal solid color PNG without PIL."""
    # This creates a very basic PNG file with solid color
    # For production, you'd want to use PIL, but this works as a fallback
    import struct
    import zlib

    # PNG signature
    png_signature = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk (image header)
    width = height = size
    bit_depth = 8
    color_type = 2  # RGB
    compression = 0
    filter_method = 0
    interlace = 0

    ihdr_data = struct.pack('>IIBBBBB', width, height, bit_depth, color_type,
                            compression, filter_method, interlace)
    ihdr_chunk = b'IHDR' + ihdr_data
    ihdr_crc = struct.pack('>I', zlib.crc32(ihdr_chunk))
    ihdr = struct.pack('>I', len(ihdr_data)) + ihdr_chunk + ihdr_crc

    # IDAT chunk (image data) - solid blue color
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # Filter type: None
        for x in range(width):
            raw_data += bytes(THEME_COLOR)  # RGB pixel

    compressed_data = zlib.compress(raw_data, 9)
    idat_chunk = b'IDAT' + compressed_data
    idat_crc = struct.pack('>I', zlib.crc32(idat_chunk))
    idat = struct.pack('>I', len(compressed_data)) + idat_chunk + idat_crc

    # IEND chunk (image end)
    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', zlib.crc32(b'IEND'))

    # Write PNG file
    with open(output_path, 'wb') as f:
        f.write(png_signature + ihdr + idat + iend)

    print(f"[OK] Created {output_path} ({size}x{size}) [minimal]")

def main():
    # Output directory
    output_dir = Path(__file__).parent / 'frontend' / 'public'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating placeholder icons for Todo App...")
    print(f"Output directory: {output_dir}")
    print()

    if PIL_AVAILABLE:
        # Create icons with PIL
        create_icon_with_pil(16, str(output_dir / 'favicon-16x16.png'))
        create_icon_with_pil(32, str(output_dir / 'favicon.ico'))
        create_icon_with_pil(180, str(output_dir / 'apple-touch-icon.png'))
        create_icon_with_pil(192, str(output_dir / 'icon-192x192.png'))
        create_icon_with_pil(512, str(output_dir / 'icon-512x512.png'))
        create_og_image_with_pil(str(output_dir / 'og-image.png'))
    else:
        # Create minimal icons without PIL
        print("Creating minimal placeholder icons (install Pillow for better quality)")
        create_minimal_png(16, str(output_dir / 'favicon-16x16.png'))
        create_minimal_png(32, str(output_dir / 'favicon.ico'))  # Note: not true ICO format
        create_minimal_png(180, str(output_dir / 'apple-touch-icon.png'))
        create_minimal_png(192, str(output_dir / 'icon-192x192.png'))
        create_minimal_png(512, str(output_dir / 'icon-512x512.png'))
        create_minimal_png(630, str(output_dir / 'og-image.png'))  # Square for simplicity

    print()
    print("[SUCCESS] All icons generated successfully!")
    print()
    print("Note: These are placeholder icons. Replace with branded icons for production.")

if __name__ == '__main__':
    main()
