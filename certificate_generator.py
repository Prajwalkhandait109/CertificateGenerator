
"""
Automatic Certificate Generator
Reads names from Excel file and adds them to a certificate template
"""

import os
import logging
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import sys
import argparse
from pathlib import Path

logger = logging.getLogger(__name__)

def create_certificates(excel_file, template_file, output_folder="certificates", 
                       font_size=60, text_color="black", position=(400, 300),
                       font_family="Arial", output_type="png"):
    """
    Generate certificates from Excel file and template

    Args:
        excel_file (str): Path to Excel/CSV file with names
        template_file (str): Path to certificate template image
        output_folder (str): Output folder for generated certificates
        font_size (int): Size of the text font
        text_color (str): Color of the text
        position (tuple): X,Y position of the text on certificate
        font_family (str): Font family to use for text
        output_type (str): Output file format (png or pdf)
    """

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    try:
        # Read Excel file
        logger.info("Reading names from %s...", excel_file)

        # Try to read Excel file, fallback to CSV
        try:
            if excel_file.endswith('.csv'):
                df = pd.read_csv(excel_file)
            else:
                df = pd.read_excel(excel_file)
        except FileNotFoundError:
            logger.error("File '%s' not found.", excel_file)
            return
        except pd.errors.EmptyDataError:
            logger.error("File '%s' is empty.", excel_file)
            return
        except Exception as e:
            logger.error("Error reading file '%s': %s", excel_file, e)
            return

        # Get names from first column or 'name' column
        if 'name' in df.columns:
            names = df['name'].dropna().tolist()
        elif 'Name' in df.columns:
            names = df['Name'].dropna().tolist()
        else:
            # Use first column
            names = df.iloc[:, 0].dropna().tolist()

        if not names:
            logger.error("No valid names found in the file.")
            return

        logger.info("Found %d names", len(names))

        # Load template image
        logger.info("Loading template from %s...", template_file)
        template = Image.open(template_file)

        # Try to load font (fallback to default if not found)
        def load_font_family(name: str, size: int):
            # 1. Check local 'fonts' folder (best for hosting)
            local_fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
            
            # Map common names to probable filenames
            family_map = {
                'Arial': ['arial.ttf', 'Arial.ttf', 'Roboto-Regular.ttf', 'LiberationSans-Regular.ttf'],
                'Times New Roman': ['times.ttf', 'Times New Roman.ttf', 'Times.ttf', 'LiberationSerif-Regular.ttf'],
                'Courier New': ['cour.ttf', 'Courier New.ttf', 'Courier.ttf', 'courier.ttf', 'LiberationMono-Regular.ttf'],
                'Verdana': ['verdana.ttf', 'Verdana.ttf', 'DejaVuSans.ttf'],
                'Georgia': ['georgia.ttf', 'Georgia.ttf', 'DejaVuSerif.ttf']
            }
            
            candidates = family_map.get(name, [f"{name}.ttf", f"{name}MT.ttf"])
            
            # Check local folder first
            if os.path.exists(local_fonts_dir):
                for fname in candidates:
                    path = os.path.join(local_fonts_dir, fname)
                    if os.path.exists(path):
                        return ImageFont.truetype(path, size)
                
                # If requested font not found locally, try finding ANY ttf in fonts dir as fallback
                try:
                    for f in os.listdir(local_fonts_dir):
                        if f.lower().endswith('.ttf'):
                            return ImageFont.truetype(os.path.join(local_fonts_dir, f), size)
                except OSError:
                    logger.warning("Could not list local fonts directory")

            # 2. Check System Fonts (Fallbacks)
            search_dirs = [
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts'),  # Windows
                '/usr/share/fonts/truetype',  # Linux common
                '/usr/share/fonts',           # Linux fallback
                '/System/Library/Fonts',      # macOS system
                '/Library/Fonts'              # macOS user
            ]
            
            for d in search_dirs:
                if not os.path.exists(d): continue
                for fname in candidates:
                    # Search recursively in subdirectories for Linux
                    for root, dirs, files in os.walk(d):
                        if fname in files:
                            return ImageFont.truetype(os.path.join(root, fname), size)

            # 3. Final Fallback - Default PIL font
            logger.warning("Font '%s' not found. Using default font at size %d.", name, size)
            return ImageFont.load_default(size=size)

        font = load_font_family(font_family, font_size)

        # Generate certificates
        logger.info("Generating certificates...")

        for i, name in enumerate(names, 1):
            # Create a copy of the template
            cert_image = template.copy()
            draw = ImageDraw.Draw(cert_image)

            # Add name to certificate with top-left anchor to match web preview
            draw.text(position, str(name), fill=text_color, font=font, anchor='lt')

            # Save certificate
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in str(name))
            
            # Set file extension based on output type
            extension = output_type.lower()
            if extension not in ['png', 'pdf']:
                extension = 'png'  # Default to PNG if invalid type
                
            filename = f"{safe_name.strip()}.{extension}"
            output_path = os.path.join(output_folder, filename)

            if extension == 'pdf':
                # Convert to RGB for PDF (removes alpha channel if present)
                if cert_image.mode == 'RGBA':
                    cert_image = cert_image.convert('RGB')
                cert_image.save(output_path, 'PDF', resolution=100.0)
            else:
                cert_image.save(output_path)
                
            logger.info("Generated certificate %d/%d: %s", i, len(names), filename)

        logger.info("All certificates generated successfully!")
        logger.info("Certificates saved in: %s", os.path.abspath(output_folder))

    except Exception as e:
        logger.exception("Certificate generation error")


def create_certificates_in_memory(names_data, template_data,
                                   font_size=60, text_color="black",
                                   position=(400, 300), font_family="Arial",
                                   output_type="png"):
    """
    Generate certificates entirely in memory (no disk writes).

    Args:
        names_data (bytes): Raw bytes of the CSV/XLSX file
        template_data (bytes): Raw bytes of the template image
        font_size, text_color, position, font_family, output_type: same as create_certificates

    Returns:
        list of (filename: str, file_bytes: bytes) tuples
    """
    import io as _io

    # Read names from bytes
    try:
        try:
            df = pd.read_csv(_io.BytesIO(names_data))
        except Exception:
            df = pd.read_excel(_io.BytesIO(names_data))
    except Exception as e:
        logger.error("Error reading names data: %s", e)
        raise ValueError(f"Could not read names file: {e}")

    if 'name' in df.columns:
        names = df['name'].dropna().tolist()
    elif 'Name' in df.columns:
        names = df['Name'].dropna().tolist()
    else:
        names = df.iloc[:, 0].dropna().tolist()

    if not names:
        raise ValueError("No valid names found in the file.")

    logger.info("Found %d names for in-memory generation", len(names))

    # Load template image from bytes
    template = Image.open(_io.BytesIO(template_data))

    # Load font (reuse the same logic)
    def load_font_family(name, size):
        local_fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        family_map = {
            'Arial': ['arial.ttf', 'Arial.ttf', 'Roboto-Regular.ttf', 'LiberationSans-Regular.ttf'],
            'Times New Roman': ['times.ttf', 'Times New Roman.ttf', 'LiberationSerif-Regular.ttf'],
            'Courier New': ['cour.ttf', 'Courier New.ttf', 'LiberationMono-Regular.ttf'],
            'Verdana': ['verdana.ttf', 'Verdana.ttf', 'DejaVuSans.ttf'],
            'Georgia': ['georgia.ttf', 'Georgia.ttf', 'DejaVuSerif.ttf'],
        }
        candidates = family_map.get(name, [f"{name}.ttf", f"{name}MT.ttf"])
        if os.path.exists(local_fonts_dir):
            for fname in candidates:
                path = os.path.join(local_fonts_dir, fname)
                if os.path.exists(path):
                    return ImageFont.truetype(path, size)
            try:
                for f in os.listdir(local_fonts_dir):
                    if f.lower().endswith('.ttf'):
                        return ImageFont.truetype(os.path.join(local_fonts_dir, f), size)
            except OSError:
                logger.warning("Could not list local fonts directory")
        search_dirs = [
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts'),
            '/usr/share/fonts/truetype', '/usr/share/fonts',
            '/System/Library/Fonts', '/Library/Fonts',
        ]
        for d in search_dirs:
            if not os.path.exists(d):
                continue
            for fname in candidates:
                for root, dirs, files in os.walk(d):
                    if fname in files:
                        return ImageFont.truetype(os.path.join(root, fname), size)
        logger.warning("Font '%s' not found. Using default font at size %d.", name, size)
        return ImageFont.load_default(size=size)

    font = load_font_family(font_family, font_size)

    extension = output_type.lower()
    if extension not in ['png', 'pdf']:
        extension = 'png'

    results = []
    for i, name in enumerate(names, 1):
        cert_image = template.copy()
        draw = ImageDraw.Draw(cert_image)
        draw.text(position, str(name), fill=text_color, font=font, anchor='lt')

        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in str(name))
        filename = f"{safe_name.strip()}.{extension}"

        buf = _io.BytesIO()
        if extension == 'pdf':
            if cert_image.mode == 'RGBA':
                cert_image = cert_image.convert('RGB')
            cert_image.save(buf, 'PDF', resolution=100.0)
        else:
            cert_image.save(buf, 'PNG')
        buf.seek(0)

        results.append((filename, buf.getvalue()))
        logger.info("Generated certificate %d/%d: %s (in-memory)", i, len(names), filename)

    logger.info("All %d certificates generated in memory.", len(results))
    return results

def main():
    parser = argparse.ArgumentParser(description='Generate certificates automatically')
    parser.add_argument('excel_file', help='Path to Excel/CSV file with names')
    parser.add_argument('template_file', help='Path to certificate template image')
    parser.add_argument('--output', '-o', default='certificates', help='Output folder name')
    parser.add_argument('--font-size', '-s', type=int, default=60, help='Font size for names')
    parser.add_argument('--color', '-c', default='black', help='Text color')
    parser.add_argument('--position', '-p', nargs=2, type=int, default=[700, 700], 
                        help='X Y position of text on certificate')

    args = parser.parse_args()

    try:
        create_certificates(
            excel_file=args.excel_file,
            template_file=args.template_file,
            output_folder=args.output,
            font_size=args.font_size,
            text_color=args.color,
            position=tuple(args.position)
        )
    except Exception as e:
        print(f"Error in certificate generation: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
