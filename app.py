from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

# Import retrieval system
from utils.retrieval_gnn import GNNRetrieval

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
JSON_OUTPUT_FOLDER = 'retrieval_output'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(JSON_OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JSON_OUTPUT_FOLDER'] = JSON_OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize retrieval system
retrieval_system = GNNRetrieval()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main input form page"""
    return render_template('index.html')

@app.route('/api/submit', methods=['POST'])
def submit_form():
    """Handle form submission with PDF upload, audience type, and description"""
    try:
        # Validate PDF file
        if 'pdfFile' not in request.files:
            return jsonify({'error': 'No PDF file provided'}), 400
        
        pdf_file = request.files['pdfFile']
        
        if pdf_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(pdf_file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400
        
        # Validate audience type
        audience_type = request.form.get('audienceType', '').strip()
        if not audience_type:
            return jsonify({'error': 'Audience type is required'}), 400
        
        # Validate description
        description = request.form.get('description', '').strip()
        if not description:
            return jsonify({'error': 'Description is required'}), 400
        
        if len(description) > 1000:
            return jsonify({'error': 'Description exceeds 1000 characters'}), 400
        
        # Save uploaded file with unique name
        filename = secure_filename(pdf_file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        pdf_file.save(filepath)
        
        # Get file size
        file_size = os.path.getsize(filepath)
        
        # Create submission record
        submission_id = str(uuid.uuid4())
        submission_data = {
            'id': submission_id,
            'filename': filename,
            'saved_filename': unique_filename,
            'filepath': filepath,
            'file_size': file_size,
            'audience_type': audience_type,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'status': 'submitted'
        }
        
        print(f"Submission received: {submission_data}")
        
        # ==================== RETRIEVAL STAGE WITH GNN ====================
        try:
            print("Starting Retrieval stage with GNN...")
            retrieval_output = retrieval_system.process_document(
                pdf_path=filepath,
                description=description,
                audience_type=audience_type,
                chunk_size=500,
                overlap=50,
                similarity_threshold=0.5,
                top_k=20
            )
            
            # Save JSON output file
            json_filename = f"{submission_id}_retrieval_output.json"
            json_filepath = os.path.join(app.config['JSON_OUTPUT_FOLDER'], json_filename)
            retrieval_system.save_to_json(retrieval_output, json_filepath)
            
            print(f"Retrieval completed. JSON saved to: {json_filepath}")
            
            # Update submission data
            submission_data['status'] = 'retrieval_completed'
            submission_data['json_output_path'] = json_filepath
            submission_data['relevant_chunks_count'] = len(retrieval_output['relevant_chunks'])
            submission_data['total_chunks'] = len(retrieval_output['graph_structure']['nodes'])
            
        except Exception as e:
            print(f"Error in Retrieval stage: {str(e)}")
            submission_data['status'] = 'retrieval_failed'
            submission_data['retrieval_error'] = str(e)
            # Continue anyway - return partial success
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Form submitted and processed successfully',
            'submission_id': submission_id,
            'status': submission_data['status'],
            'json_output_path': submission_data.get('json_output_path'),
            'relevant_chunks_count': submission_data.get('relevant_chunks_count', 0),
            'total_chunks': submission_data.get('total_chunks', 0)
        }), 200
        
    except Exception as e:
        print(f"Error processing submission: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File size exceeds 50MB limit'}), 413

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

