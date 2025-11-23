import os
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
from certificate_generator import create_certificates

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx', 'png', 'jpg', 'jpeg'}

# Create necessary folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_certificates():
    # Check if the post request has the file parts
    if 'namesFile' not in request.files or 'templateFile' not in request.files:
        flash('Missing required files')
        return redirect(request.url)
    
    names_file = request.files['namesFile']
    template_file = request.files['templateFile']
    
    # If user does not select files, browser submits empty files without filenames
    if names_file.filename == '' or template_file.filename == '':
        flash('No selected files')
        return redirect(request.url)
    
    if not (names_file and allowed_file(names_file.filename) and 
            template_file and allowed_file(template_file.filename)):
        flash('Invalid file types')
        return redirect(request.url)
    
    # Save the uploaded files
    names_filename = secure_filename(names_file.filename)
    template_filename = secure_filename(template_file.filename)
    
    names_path = os.path.join(app.config['UPLOAD_FOLDER'], names_filename)
    template_path = os.path.join(app.config['UPLOAD_FOLDER'], template_filename)
    
    names_file.save(names_path)
    template_file.save(template_path)
    
    # Get other form parameters
    output_folder = app.config['OUTPUT_FOLDER']
    font_size = int(request.form.get('fontSize', 60))
    text_color = request.form.get('textColor', 'black')
    position_x = int(request.form.get('positionX', 700))
    position_y = int(request.form.get('positionY', 700))
    font_family = request.form.get('fontFamily', 'Arial')
    output_type = request.form.get('outputType', 'png')
    
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
        certificates = os.listdir(output_folder)
        certificates = [cert for cert in certificates if os.path.isfile(os.path.join(output_folder, cert))]
        
        return render_template('results.html', certificates=certificates)
    
    except Exception as e:
        flash(f'Error generating certificates: {str(e)}')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

@app.route('/view/<filename>')
def view_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

@app.route('/download-all')
def download_all():
    import zipfile
    import io
    
    # Create a zip file in memory
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for filename in os.listdir(app.config['OUTPUT_FOLDER']):
            file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
            if os.path.isfile(file_path):
                zf.write(file_path, filename)
    
    memory_file.seek(0)
    return send_from_directory(
        directory=app.config['OUTPUT_FOLDER'],
        path='../certificates.zip',
        as_attachment=True,
        download_name='certificates.zip',
        response_class=lambda: memory_file
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)