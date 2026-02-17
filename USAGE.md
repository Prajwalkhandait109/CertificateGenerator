# Certificate Generator Usage Guide

## Basic Usage

The certificate generator requires two mandatory arguments:
1. Path to an Excel/CSV file containing names
2. Path to a certificate template image

```bash
python certificate_generator.py sample_names.csv "Blue and Gold Simple Certificate.png"
```

## Command Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|--------|
| `--output` | `-o` | Output folder name | `certificates` |
| `--font-size` | `-s` | Font size for names | `60` |
| `--color` | `-c` | Text color | `black` |
| `--position` | `-p` | X Y position of text on certificate | `400 300` |

## Examples

### Basic usage with default settings
```bash
python certificate_generator.py sample_names.csv "Blue and Gold Simple Certificate.png"
```

### Custom output folder
```bash
python certificate_generator.py sample_names.csv "Blue and Gold Simple Certificate.png" --output my_certificates
```

### Custom font size and color
```bash
python certificate_generator.py sample_names.csv "Blue and Gold Simple Certificate.png" --font-size 80 --color blue
```

### Custom text position
```bash
python certificate_generator.py sample_names.csv "Blue and Gold Simple Certificate.png" --position 500 400
```

## Input File Format

The input file should be an Excel (.xlsx, .xls) or CSV file with names in the first column or in a column named 'name' or 'Name'.

Example CSV format:
```
name
John Smith
Sarah Johnson
Michael Brown
```

## Troubleshooting

- If you see an error about missing arguments, make sure you're providing both the Excel/CSV file and the template image file.
- If you're having issues with font rendering, the script will automatically try different font files or fall back to the default font.
- For any other errors, check the error message for details on what went wrong.