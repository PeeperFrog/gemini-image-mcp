#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pillow>=10.0.0",
# ]
# ///
"""
Convert PNG images to WebP format for WordPress optimization.
Usage: uv run convert-to-webp.py input.png [output.webp] [--quality 85]

No installation required - uv handles dependencies automatically.
"""

import sys
import argparse
from pathlib import Path
from PIL import Image

def convert_to_webp(input_path, output_path=None, quality=85, skip_existing=True):
    """
    Convert image to WebP format.
    
    Args:
        input_path: Path to input image (PNG, JPG, etc.)
        output_path: Optional output path (defaults to input name with .webp)
        quality: WebP quality (0-100, default 85)
        skip_existing: Skip if .webp version already exists (default True)
    
    Returns:
        Path to output file, or None if skipped/error
    """
    input_path = Path(input_path)
    
    # Default output path
    if output_path is None:
        output_path = input_path.with_suffix('.webp')
    else:
        output_path = Path(output_path)
    
    # Skip if WebP already exists
    if skip_existing and output_path.exists():
        print(f"⊘ Skipped (already exists): {input_path.name}")
        return None
    
    # Load and convert
    try:
        img = Image.open(input_path)
        
        # Convert RGBA to RGB if necessary (WebP supports alpha but this ensures compatibility)
        if img.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save as WebP
        img.save(
            output_path,
            'webp',
            quality=quality,
            method=6  # Highest quality compression method
        )
        
        # Report size reduction
        original_size = input_path.stat().st_size
        webp_size = output_path.stat().st_size
        reduction = ((original_size - webp_size) / original_size) * 100
        
        print(f"✓ Converted: {input_path.name}")
        print(f"  Original: {original_size:,} bytes")
        print(f"  WebP: {webp_size:,} bytes")
        print(f"  Saved: {reduction:.1f}%")
        print(f"  Output: {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"✗ Error converting {input_path}: {e}", file=sys.stderr)
        return None

def batch_convert(directory, quality=85, recursive=False, skip_existing=True):
    """
    Convert all PNG/JPG images in a directory to WebP.
    
    Args:
        directory: Path to directory
        quality: WebP quality
        recursive: Search subdirectories
        skip_existing: Skip files that already have .webp versions
    """
    directory = Path(directory)
    
    # Find images
    patterns = ['*.png', '*.PNG', '*.jpg', '*.JPG', '*.jpeg', '*.JPEG']
    images = []
    
    for pattern in patterns:
        if recursive:
            images.extend(directory.rglob(pattern))
        else:
            images.extend(directory.glob(pattern))
    
    if not images:
        print(f"No images found in {directory}")
        return
    
    print(f"\nProcessing {len(images)} images...\n")
    
    converted = 0
    skipped = 0
    errors = 0
    
    for img_path in images:
        result = convert_to_webp(img_path, quality=quality, skip_existing=skip_existing)
        if result:
            converted += 1
        elif img_path.with_suffix('.webp').exists():
            skipped += 1
        else:
            errors += 1
        print()  # Blank line between files
    
    print(f"\n✓ Converted: {converted}")
    print(f"⊘ Skipped (already exist): {skipped}")
    if errors > 0:
        print(f"✗ Errors: {errors}")
    print(f"Total processed: {converted + skipped + errors}/{len(images)}")

def main():
    parser = argparse.ArgumentParser(
        description='Convert images to WebP format for WordPress optimization'
    )
    parser.add_argument(
        'input',
        help='Input image file or directory'
    )
    parser.add_argument(
        'output',
        nargs='?',
        help='Output file (optional, defaults to input name with .webp)'
    )
    parser.add_argument(
        '-q', '--quality',
        type=int,
        default=85,
        help='WebP quality (0-100, default: 85)'
    )
    parser.add_argument(
        '-b', '--batch',
        action='store_true',
        help='Process all images in directory'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Process subdirectories recursively (with --batch)'
    )
    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Force reconversion even if .webp already exists'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    # Validate quality
    if not 0 <= args.quality <= 100:
        print("Error: Quality must be between 0 and 100", file=sys.stderr)
        sys.exit(1)
    
    # Batch mode
    if args.batch or input_path.is_dir():
        if not input_path.is_dir():
            print(f"Error: {input_path} is not a directory", file=sys.stderr)
            sys.exit(1)
        batch_convert(
            input_path, 
            quality=args.quality, 
            recursive=args.recursive,
            skip_existing=not args.force
        )
    
    # Single file mode
    else:
        if not input_path.exists():
            print(f"Error: {input_path} not found", file=sys.stderr)
            sys.exit(1)
        
        result = convert_to_webp(
            input_path, 
            args.output, 
            quality=args.quality,
            skip_existing=not args.force
        )
        if not result:
            sys.exit(1)

if __name__ == '__main__':
    main()
