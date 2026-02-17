#!/usr/bin/env python
"""
Position Finder Tool for Certificate Generator
Helps identify the optimal position for text on certificate templates
"""

import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont

def find_position(template_file, output_folder="position_test", sample_text="Sample Name"):
    """
    Generate test certificates with position grid to help find the optimal position
    
    Args:
        template_file (str): Path to certificate template image
        output_folder (str): Output folder for test images
        sample_text (str): Sample text to display on the certificate
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        # Load template image
        print(f"Loading template from {template_file}...")
        template = Image.open(template_file)
        width, height = template.size
        print(f"Template dimensions: {width}x{height} pixels")
        
        # Try to load font
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except OSError:
            try:
                font = ImageFont.truetype("ArialMT.ttf", 60)  # Mac
            except OSError:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 60)  # Mac system
                except OSError:
                    font = ImageFont.load_default()
                    print("Warning: Using default font (font file not found)")
        
        # Create grid image
        grid_image = template.copy()
        draw = ImageDraw.Draw(grid_image)
        
        # Draw horizontal and vertical center lines
        draw.line([(0, height//2), (width, height//2)], fill="red", width=1)  # Horizontal center
        draw.line([(width//2, 0), (width//2, height)], fill="red", width=1)  # Vertical center
        
        # Draw grid lines every 100 pixels
        for x in range(100, width, 100):
            draw.line([(x, 0), (x, height)], fill="lightblue", width=1)
            # Add coordinate labels
            draw.text((x, 10), str(x), fill="blue", font=ImageFont.truetype("arial.ttf", 20) if 'arial.ttf' in font.path else ImageFont.load_default())
        
        for y in range(100, height, 100):
            draw.line([(0, y), (width, y)], fill="lightblue", width=1)
            # Add coordinate labels
            draw.text((10, y), str(y), fill="blue", font=ImageFont.truetype("arial.ttf", 20) if 'arial.ttf' in font.path else ImageFont.load_default())
        
        # Save grid image
        grid_path = os.path.join(output_folder, "grid_overlay.png")
        grid_image.save(grid_path)
        print(f"Grid overlay saved to: {os.path.abspath(grid_path)}")
        
        # Generate test images with sample text at different positions
        positions = [
            (width//2, height//2),  # Center
            (width//2, height//3),  # Upper center
            (width//2, 2*height//3),  # Lower center
            (width//3, height//2),  # Center left
            (2*width//3, height//2),  # Center right
            (400, 300),  # Default position
        ]
        
        for i, pos in enumerate(positions):
            test_image = template.copy()
            draw = ImageDraw.Draw(test_image)
            
            # Draw position marker
            marker_size = 5
            draw.ellipse([pos[0]-marker_size, pos[1]-marker_size, pos[0]+marker_size, pos[1]+marker_size], 
                         outline="red", fill="red")
            
            # Add sample text
            draw.text(pos, sample_text, fill="black", font=font, anchor="mm")
            
            # Add position coordinates
            coord_text = f"Position: ({pos[0]}, {pos[1]})"
            draw.text((10, 10), coord_text, fill="blue", font=ImageFont.truetype("arial.ttf", 20) if 'arial.ttf' in font.path else ImageFont.load_default())
            
            # Save test image
            filename = f"position_test_{pos[0]}_{pos[1]}.png"
            output_path = os.path.join(output_folder, filename)
            test_image.save(output_path)
            print(f"Test image saved to: {os.path.abspath(output_path)}")
        
        print("\nAll test images generated successfully!")
        print(f"Test images saved in: {os.path.abspath(output_folder)}")
        print("\nReview the test images to find the optimal position for your text.")
        print("Once you've found the optimal position, use the --position X Y parameter with certificate_generator.py")
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Find optimal text position on certificate template')
    parser.add_argument('template_file', help='Path to certificate template image')
    parser.add_argument('--output', '-o', default='position_test', help='Output folder name')
    parser.add_argument('--text', '-t', default='Sample Name', help='Sample text to display')
    
    args = parser.parse_args()
    
    try:
        find_position(
            template_file=args.template_file,
            output_folder=args.output,
            sample_text=args.text
        )
    except Exception as e:
        print(f"Error in position finder: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())