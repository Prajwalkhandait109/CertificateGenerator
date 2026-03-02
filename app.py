import os
import io
import uuid
import time
import logging
import zipfile
import secrets
import threading

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_from_directory, send_file, abort, jsonify
)
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
import pandas as pd
from dotenv import load_dotenv

from certificate_generator import create_certificates

# ---------------------------------------------------------------------------
# Load environment variables from .env file (if present)
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__)

# CRITICAL FIX #1 — Secret key from environment, not regenerated on restart
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-please-change-in-production')

# CRITICAL FIX #2 — Limit upload size to 16 MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['OUTPUT_FOLDER'] = os.environ.get('OUTPUT_FOLDER', 'output')
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx', 'png', 'jpg', 'jpeg'}

# HIGH FIX #8 — CSRF protection
csrf = CSRFProtect(app)

# ---------------------------------------------------------------------------
# Logging (replaces print statements in this file)
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Create necessary folders
# ---------------------------------------------------------------------------
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# ---------------------------------------------------------------------------
# HIGH FIX #9 — Background cleanup of stale uploads/output (> 1 hour old)
# ---------------------------------------------------------------------------
CLEANUP_MAX_AGE_SECONDS = 600  # 10 minutes

def _cleanup_stale_files():
    """Delete files and empty subdirectories older than CLEANUP_MAX_AGE_SECONDS."""
    while True:
        time.sleep(120)  # Run every 2 minutes
        cutoff = time.time() - CLEANUP_MAX_AGE_SECONDS
        for folder_name in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
            if not os.path.isdir(folder_name):
                continue
            for root, dirs, files in os.walk(folder_name, topdown=False):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    try:
                        if os.path.getmtime(fpath) < cutoff:
                            os.remove(fpath)
                            logger.info("Cleanup: removed stale file %s", fpath)
                    except OSError:
                        pass
                # Remove empty subdirectories
                for dname in dirs:
                    dpath = os.path.join(root, dname)
                    try:
                        if not os.listdir(dpath):
                            os.rmdir(dpath)
                            logger.info("Cleanup: removed empty dir %s", dpath)
                    except OSError:
                        pass
            

_cleanup_thread = threading.Thread(target=_cleanup_stale_files, daemon=True)
_cleanup_thread.start()


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


# HIGH FIX #10 — Health check endpoint for load balancers / monitoring
@app.route('/health')
def health():
    return jsonify(status='ok'), 200


@app.route('/generate', methods=['POST'])
def generate_certificates():
    # Check if the post request has the file parts
    if 'namesFile' not in request.files or 'templateFile' not in request.files:
        flash('Missing required files')
        return redirect(url_for('index'))

    names_file = request.files['namesFile']
    template_file = request.files['templateFile']

    # If user does not select files, browser submits empty files
    if names_file.filename == '' or template_file.filename == '':
        flash('No selected files')
        return redirect(url_for('index'))

    if not (names_file and allowed_file(names_file.filename) and
            template_file and allowed_file(template_file.filename)):
        flash('Invalid file types. Allowed: CSV/XLSX for names, PNG/JPG for template.')
        return redirect(url_for('index'))

    # Save the uploaded files
    names_filename = secure_filename(names_file.filename)
    template_filename = secure_filename(template_file.filename)

    names_path = os.path.join(app.config['UPLOAD_FOLDER'], names_filename)
    template_path = os.path.join(app.config['UPLOAD_FOLDER'], template_filename)

    names_file.save(names_path)
    template_file.save(template_path)

    # Get other form parameters with validation (MEDIUM FIX #12)
    try:
        font_size = int(request.form.get('fontSize', 60))
        font_size = max(10, min(font_size, 200))
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

    # CRITICAL FIX #5 — Per-session output folder so users don't share files
    session_id = str(uuid.uuid4())
    output_folder = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
    os.makedirs(output_folder, exist_ok=True)

    # Generate certificates
    try:
        create_certificates(
            excel_file=names_path,
            template_file=template_path,
            output_folder=output_folder,
            font_size=font_size,
            text_color=text_color,
            position=(position_x, position_y),
            font_family=font_family,
            output_type=output_type
        )

        # Get list of generated certificates
        certificates = [
            cert for cert in os.listdir(output_folder)
            if os.path.isfile(os.path.join(output_folder, cert))
        ]

        logger.info("Generated %d certificates in session %s", len(certificates), session_id)
        return render_template('results.html', certificates=certificates, session_id=session_id)

    except Exception:
        logger.exception("Certificate generation failed")
        flash('An error occurred while generating certificates. Please try again.')
        return redirect(url_for('index'))


# CRITICAL FIX #4 — Sanitize filenames to prevent path traversal
@app.route('/download/<session_id>/<filename>')
def download_file(session_id, filename):
    session_id = secure_filename(session_id)
    filename = secure_filename(filename)
    if not session_id or not filename:
        abort(404)
    directory = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
    if not os.path.isdir(directory):
        abort(404)
    return send_from_directory(directory, filename, as_attachment=True)


@app.route('/view/<session_id>/<filename>')
def view_file(session_id, filename):
    session_id = secure_filename(session_id)
    filename = secure_filename(filename)
    if not session_id or not filename:
        abort(404)
    directory = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
    if not os.path.isdir(directory):
        abort(404)
    return send_from_directory(directory, filename)


# CRITICAL FIX #3 — Rewritten download-all using send_file with BytesIO
@app.route('/download-all/<session_id>')
def download_all(session_id):
    session_id = secure_filename(session_id)
    if not session_id:
        abort(404)
    directory = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
    if not os.path.isdir(directory):
        abort(404)

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                zf.write(file_path, filename)

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='certificates.zip'
    )


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