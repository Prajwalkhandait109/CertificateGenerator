import os
import io
import base64
import logging
import zipfile

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_file, abort, jsonify
)
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

from certificate_generator import create_certificates_in_memory

# ---------------------------------------------------------------------------
# Load environment variables from .env file (if present)
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-please-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx', 'png', 'jpg', 'jpeg'}

# CSRF protection
csrf = CSRFProtect(app)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    return jsonify(status='ok'), 200


@app.route('/generate', methods=['POST'])
def generate_certificates():
    # Validate files are present
    if 'namesFile' not in request.files or 'templateFile' not in request.files:
        flash('Missing required files')
        return redirect(url_for('index'))

    names_file = request.files['namesFile']
    template_file = request.files['templateFile']

    if names_file.filename == '' or template_file.filename == '':
        flash('No selected files')
        return redirect(url_for('index'))

    if not (names_file and allowed_file(names_file.filename) and
            template_file and allowed_file(template_file.filename)):
        flash('Invalid file types. Allowed: CSV/XLSX for names, PNG/JPG for template.')
        return redirect(url_for('index'))

    # Read files into memory (no disk writes)
    names_data = names_file.read()
    template_data = template_file.read()

    # Parse form parameters
    try:
        font_size = max(10, min(int(request.form.get('fontSize', 60)), 200))
    except (ValueError, TypeError):
        flash('Invalid font size value')
        return redirect(url_for('index'))

    text_color = request.form.get('textColor', 'black')

    try:
        position_x = int(request.form.get('positionX', 700))
        position_y = int(request.form.get('positionY', 700))
    except (ValueError, TypeError):
        flash('Invalid position values')
        return redirect(url_for('index'))

    font_family = request.form.get('fontFamily', 'Arial')
    output_type = request.form.get('outputType', 'png')

    # Generate certificates in memory
    try:
        cert_results = create_certificates_in_memory(
            names_data=names_data,
            template_data=template_data,
            font_size=font_size,
            text_color=text_color,
            position=(position_x, position_y),
            font_family=font_family,
            output_type=output_type,
        )

        # Build base64 data for each certificate (for preview + individual download)
        certificates = []
        for filename, file_bytes in cert_results:
            is_image = filename.lower().endswith(('.png', '.jpg', '.jpeg'))
            mime = 'image/png' if is_image else 'application/pdf'
            b64 = base64.b64encode(file_bytes).decode('ascii')
            certificates.append({
                'filename': filename,
                'b64': b64,
                'mime': mime,
                'is_image': is_image,
            })

        # Build the ZIP file in memory
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename, file_bytes in cert_results:
                zf.writestr(filename, file_bytes)
        zip_buf.seek(0)
        zip_b64 = base64.b64encode(zip_buf.getvalue()).decode('ascii')

        logger.info("Generated %d certificates (in-memory, Vercel-safe)", len(certificates))

        return render_template(
            'results.html',
            certificates=certificates,
            zip_b64=zip_b64,
        )

    except ValueError as e:
        flash(str(e))
        return redirect(url_for('index'))
    except Exception:
        logger.exception("Certificate generation failed")
        flash('An error occurred while generating certificates. Please try again.')
        return redirect(url_for('index'))


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum upload size is 16 MB.')
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)