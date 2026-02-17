
# Automatic Certificate Generator

This tool automatically generates personalized certificates by reading names from an Excel file and adding them to a certificate template.

## Features

- ✅ Read names from Excel (.xlsx, .xls) or CSV files
- ✅ Support for PNG, JPG certificate templates
- ✅ Customizable font size, color, and position
- ✅ Batch generation of certificates
- ✅ Safe filename handling
- ✅ Web application interface
- ✅ Command-line Python script

## Web Application

Use the web interface at: [Certificate Generator Web App](https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/46ce04e8a1f331159bf9be9092ff6c5b/74f33e02-6873-47b5-ba59-9c59451df580/index.html)

### Web App Features:
- Drag & drop file uploads
- Live certificate preview
- Interactive positioning
- Batch download as ZIP
- No installation required

## Python Script Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line (Basic)
```bash
python certificate_generator.py sample_names.xlsx certificate_template.png
```

### Command Line (Advanced)
```bash
python certificate_generator.py sample_names.xlsx template.png --output "my_certificates" --font-size 72 --color "navy" --position 350 250
```

### Parameters:
- `excel_file`: Path to your Excel/CSV file with names
- `template_file`: Path to your certificate template image
- `--output` / `-o`: Output folder name (default: "certificates")
- `--font-size` / `-s`: Font size for names (default: 60)
- `--color` / `-c`: Text color (default: "black")
- `--position` / `-p`: X Y coordinates for text placement (default: 400 300)

## File Formats

### Excel/CSV File Requirements:
- Must have a column named "name", "Name", or use the first column
- One name per row
- Supports Excel (.xlsx, .xls) and CSV (.csv) formats

### Template Image Requirements:
- PNG, JPG, or JPEG format
- Leave empty space where names will be placed
- Recommended size: 1200x800 pixels or larger
- Ensure good contrast between text area and background

## Tips for Best Results

1. **Template Design**: Use high-resolution images with clear space for names
2. **Font Size**: Start with 60px and adjust based on your template size
3. **Positioning**: Use image editing software to measure exact coordinates
4. **Testing**: Generate one certificate first to verify positioning
5. **Colors**: Use contrasting colors (e.g., black text on light background)

## Troubleshooting

### Common Issues:
- **Font not found**: The script will use default font automatically
- **Names not detected**: Check your Excel column headers
- **Text positioning**: Adjust the --position parameters
- **File permissions**: Ensure write access to output folder

### Python Requirements:
- Python 3.6 or higher
- pandas (for Excel reading)
- Pillow (for image processing)
- openpyxl (for Excel support)

## Examples

Your Excel file should look like this:

| name |
|------|
| John Smith |
| Sarah Johnson |
| Michael Brown |

The script will create individual PNG files for each person:
- `John Smith.png`
- `Sarah Johnson.png`
- `Michael Brown.png`

## Web vs Python Script

**Use Web Application When:**
- You want a visual interface
- Need to test positioning interactively
- Want to preview before generating
- Prefer no installation

**Use Python Script When:**
- You have many certificates to generate
- Want to automate the process
- Need to integrate with other scripts
- Prefer command-line tools
