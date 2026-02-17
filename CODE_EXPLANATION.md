# Certificate Generator – Line-by-Line Code Explanation

This document explains the two core Python modules of the project line by line: `certificate_generator.py` (the engine that produces certificates) and `app.py` (the Flask web app). For each line, you’ll see what it does and why it’s used in this project.

Note: HTML templates and CSS are not covered line-by-line here to keep this readable; they follow standard Flask/Jinja2 and web styling patterns. If you want similar depth for templates or Dockerfile, say the word and I’ll add them.

---

## certificate_generator.py

1. `"""` – Starts a module-level docstring.
2. `Automatic Certificate Generator` – Brief description of the module.
3. `Reads names from Excel file and adds them to a certificate template` – Explains functionality.
4. `"""` – Ends the docstring.
5. (blank) – Formatting.
6. `import os` – Imports OS utilities for paths and directories.
7. `import pandas as pd` – Imports Pandas for reading CSV/Excel files; needed to parse the names list.
8. `from PIL import Image, ImageDraw, ImageFont` – Imports Pillow for image manipulation, text drawing, and fonts.
9. `import sys` – Allows returning exit codes and accessing interpreter state; used in `main()`.
10. `import argparse` – Enables command-line argument parsing for CLI usage.
11. `from pathlib import Path` – Path utilities (not strictly required here but handy for cross-platform paths).

12–14. `def create_certificates(...):` – Defines the main function to generate certificates. Accepts:
   - `excel_file` – Names source file.
   - `template_file` – Certificate background image.
   - `output_folder` – Destination directory.
   - `font_size`, `text_color`, `position` – Text rendering inputs.
   - `font_family`, `output_type` – Additional controls to match preview and output format.

15–26. Docstring describing what the function does and each parameter’s purpose; helps maintainers and users.

28. `os.makedirs(output_folder, exist_ok=True)` – Ensures the output directory exists; avoids crashes when saving.

30–33. Begins a try/except to handle top-level errors gracefully.
34. `print(f"Reading names from {excel_file}...")` – Logs progress to console for UX feedback.

36–43. Attempts to read the names file:
   - If `.csv` → `pd.read_csv`
   - Else → `pd.read_excel`
   Why: Supports both CSV and Excel inputs commonly used for lists of names.

44–52. Specific error handling:
   - `FileNotFoundError` → missing file.
   - `EmptyDataError` → blank file.
   - generic `Exception` → other parsing issues.
   Why: Provides clear messages and safe exit instead of hard crashes.

55–63. Extracts names from the DataFrame:
   - Prefers `name` or `Name` columns if present.
   - Falls back to the first column.
   Why: Accommodates varied spreadsheet schemas.

65–67. Validates that names exist; logs error and returns if none.

69. `print(f"Found {len(names)} names")` – Feedback to the user.

72–73. Loads the template image with Pillow; logs source path.

75–111. `load_font_family(name, size)` helper:
   - Maps common family names to typical `.ttf` filenames across Windows/macOS/Linux.
   - Searches multiple font directories.
   - Returns a loaded `ImageFont` or falls back to default with a warning.
   Why: Ensures the Python-rendered font matches the browser preview selection.

113. `font = load_font_family(font_family, font_size)` – Loads the requested font.

116. `print("Generating certificates...")` – Progress log.

118. `for i, name in enumerate(names, 1):` – Iterates through names with a human-friendly index starting at 1.
119–121. Copies the template image and gets a drawing context; prevents mutating the original.

123. `draw.text(position, str(name), fill=text_color, font=font, anchor='lt')` – Draws the name:
   - Uses top-left anchor (`lt`) to match the canvas preview text anchor.
   - Converts name to string for safety.
   Why: Aligns output positioning with the web preview experience.

126–128. Builds a safe filename by stripping unsafe characters; avoids filesystem issues.

130–135. Resolves the requested output type (`png`/`pdf`) and defaults to `png` if invalid; improves robustness.

137–138. Computes output path from `output_folder` and filename.

140–146. Handles PDF saving:
   - Converts RGBA → RGB if needed (PDF doesn’t support alpha channels).
   - Saves with `PDF` format and resolution.
   Else: saves a normal PNG.
   Why: Supports your “PNG or PDF” requirement reliably.

148. Logs which certificate was generated; user feedback.

150–151. Final success logs: where certificates are saved.

153–154. Top-level `except` to capture unexpected failures; logs the error.

156–165. `main()` function:
   - Sets up CLI arguments for files, output folder, font size, color, and position.
   - Parses args and calls `create_certificates(...)`.
   Why: Enables running outside Flask for scripts or testing.

166–173. Handles CLI errors gracefully, returns exit codes, and wires `main()` for `__name__ == "__main__"` entrypoint.

---

## app.py

1–2. `import os`, `import secrets` – OS utilities and secure random values.
3. `from flask import ...` – Imports Flask core functions for routing, rendering, request handling, and file sending.
4. `from werkzeug.utils import secure_filename` – Sanitizes uploaded filenames to prevent path traversal or unsafe chars.
5. `import pandas as pd` – Present but not directly used now; can be removed if not needed.
6. `from certificate_generator import create_certificates` – Imports the generator function to produce certificates.

8. `app = Flask(__name__)` – Creates the Flask application.
9. `app.config['SECRET_KEY'] = secrets.token_hex(16)` – Sets a random secret key for secure session/flash messaging.
10–12. Configures upload/output folders and allowed extensions; centralizes settings.

14–15. Ensures upload and output directories exist; avoids file save errors.

17–19. `allowed_file(filename)` – Validates extension against the allowlist; used to reject unsupported uploads.

21–23. `@app.route('/')` + `index()` – Serves the main page (form and preview) from `templates/index.html`.

25–63. `@app.route('/generate', methods=['POST'])` – Handles form submission:
   - Validates presence of files and non-empty filenames.
   - Checks file types via `allowed_file`.
   - Saves uploaded files to `uploads/` using `secure_filename`.
   - Reads form fields: `fontSize`, `textColor`, `positionX/Y`, `fontFamily`, `outputType`.
   - Calls `create_certificates(...)` with collected parameters.
   - Lists files in `output/` and renders `results.html` with the list.
   Why: This is the core server-side workflow for generating and showing results.

65–69. Error handling: flashes an error and redirects to the index on failure; keeps UX smooth.

71–73. `download_file` route: returns a single file from `output/` as an attachment; supports per-file download.

75–77. `view_file` route: serves a single file for inline viewing; convenient for quick checks.

79–95. `download_all` route:
   - Zips all files in `output/` into an in-memory archive.
   - Seeks to start and attempts to return as a download.
   Why: Provides the “Download All” feature.
   Note: For production, consider returning a `Response` with `BytesIO` instead of `send_from_directory` for the zip.

97–99. Flask dev server launcher: runs on `0.0.0.0:5000` with debug enabled; easy local testing.

---

## Why these pieces matter together

- The web UI lets users upload their data and visually preview text placement.
- The Flask backend validates data, stores temporary files, and delegates generation to the Pillow-based engine.
- The engine reads names, renders text using the same anchor assumptions as the preview, and saves outputs as PNG or PDF.
- Results can be viewed individually or downloaded all at once.

If you want me to generate similar line-by-line docs for `templates/index.html`, `templates/results.html`, `static/styles.css`, `Dockerfile`, or `position_finder.py`, I can add them as separate sections or files.

---

## Templates

**templates/index.html**
- Purpose: Main UI for uploading the names file and template, configuring font options, picking output type, and previewing placement.
- Key elements:
  - Upload inputs: `excel_file` (CSV/XLSX) and `template_file` (PNG/JPG).
  - Controls: `fontSize`, `textColor`, `positionX`, `positionY`, `fontFamily`, `outputType` (PNG/PDF).
  - Canvas-based preview: draws the uploaded template and renders a sample name at the specified position; supports dragging text to update position.
  - Form submission: posts to `/generate` which triggers certificate creation.
- Notes: This is the file Flask renders for the root route `/`. It should link to `static/styles.css` for styling.

**templates/results.html**
- Purpose: Displays a list of generated certificates with actions to view or download each file.
- Features:
  - “View” link opens the image/PDF inline.
  - “Download” link saves the file.
  - “Download All Certificates” button bundles outputs into a zip from `/download-all`.
  - Link back to the index page to generate more.
- Notes: Uses Jinja2 templating to iterate over the files in the `output/` folder.

## Static Assets

**static/styles.css**
- Purpose: Project-wide styles used by Flask templates.
- Highlights:
  - Layout and typography for the main container, headings, and forms.
  - Button styles including the “Download All” button.
  - Preview styles: `.preview-container` and `#previewCanvas` ensure the canvas scales and fits nicely.
- Notes: This is the stylesheet referenced by `templates/index.html` and `templates/results.html`.

**styles.css (project root)**
- Purpose: Legacy/duplicate stylesheet from earlier iterations.
- Recommendation: Prefer `static/styles.css` in Flask templates. If not referenced anywhere, consider removing or merging changes into `static/styles.css` to avoid confusion.

## Documentation and Config

**README.md**
- Overview of the project, features, and basic setup. Good entry point for new users.

**USAGE.md**
- Detailed usage instructions (web and/or CLI). Helps users run the app end-to-end.

**NAME_POSITION_GUIDE.md**
- Explains how to think about and select the X/Y position on the certificate. Useful for aligning text correctly.

**requirements.txt**
- Python dependencies. Includes libraries like Flask, Pillow, Pandas, and ReportLab for PDF support.

**.vscode/launch.json**
- Editor configuration for debugging. Optional but handy for consistent dev setups.

## Examples and Utilities

**example_usage.bat**
- Windows helper script that demonstrates running the generator or starting the app with sample inputs.

**sample_names.csv**
- Example data file with names for quick testing.

**Blue and Gold Simple Certificate.png**, **certificate 1.png**
- Sample certificate templates for preview/testing.

**git_CertificateGenerator/**
- A nested git-related folder (likely a separate repo or scratch space). Not used by the Flask app.

## Runtime Folders

**uploads/**
- Temporary storage for uploaded files (names list and template). Created by the app on demand.
- Not recommended to commit to Git; add to `.gitignore` if not already.

**output/**
- Generated certificates (PNG/PDF). Displayed on the results page and available for individual or bulk download.
- Not recommended to commit to Git; add to `.gitignore` if not already.

**position_test/**
- Images and overlays to help test or visualize positions. Useful during development; not required in production.

**__pycache__/** and **.venv/**
- Python bytecode cache and local virtual environment, respectively.
- Should be excluded from version control via `.gitignore`.

---

Excluded per request: Dockerfile, position_finder.py.