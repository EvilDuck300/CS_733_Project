from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import json
from typing import Optional
from dotenv import load_dotenv

# Import all systems
from utils.retrieval_gnn import GNNRetrieval
from utils.slide_generator import SlideGenerator
from utils.evaluator import SlideEvaluator
from utils.presentation_builder import create_presentation_from_slides_data

load_dotenv()

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
JSON_OUTPUT_FOLDER = 'retrieval_output'
SLIDES_OUTPUT_FOLDER = 'slides_output'
PRESENTATIONS_FOLDER = 'presentations'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
EVALUATION_THRESHOLD = 75.0  # Minimum score for acceptance
MAX_ITERATIONS = 3  # Maximum iterations for quality improvement

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(JSON_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(SLIDES_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(PRESENTATIONS_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JSON_OUTPUT_FOLDER'] = JSON_OUTPUT_FOLDER
app.config['SLIDES_OUTPUT_FOLDER'] = SLIDES_OUTPUT_FOLDER
app.config['PRESENTATIONS_FOLDER'] = PRESENTATIONS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize systems
retrieval_system = GNNRetrieval()
slide_generator: Optional[SlideGenerator] = None
evaluator: Optional[SlideEvaluator] = None

# Get API key from environment (do not hardcode secrets)
# Check for GEOGRAPHY_KEY
GEOGRAPHY_KEY = os.getenv("GEOGRAPHY_KEY")
if GEOGRAPHY_KEY:
    print(f"✓ Gemini API key found (length: {len(GEOGRAPHY_KEY)})")
else:
    print("⚠ Warning: GEOGRAPHY_KEY environment variable not set")
    print("  → Set GEOGRAPHY_KEY to use slide generation and evaluation features")

def get_slide_generator():
    """Get or initialize slide generator (using Gemini API)"""
    global slide_generator
    if slide_generator is None:
        # Pass API key directly if available
        api_key = GEOGRAPHY_KEY or os.getenv('GEOGRAPHY_KEY')
        slide_generator = SlideGenerator(api_key=api_key)
        
        # Diagnostic output
        if hasattr(slide_generator, 'client') and slide_generator.client is None:
            print("⚠ Warning: SlideGenerator initialized but client is None")
            if not api_key:
                print("  → API key not found in environment variable GEOGRAPHY_KEY")
        else:
            print("✓ SlideGenerator initialized successfully with Gemini API client")
    
    return slide_generator

def get_evaluator():
    """Get or initialize evaluator (using Gemini API)"""
    global evaluator
    if evaluator is None:
        # Pass API key directly if available
        api_key = GEOGRAPHY_KEY or os.getenv('GEOGRAPHY_KEY')
        evaluator = SlideEvaluator(api_key=api_key)
        
        # Diagnostic output
        if hasattr(evaluator, 'client') and evaluator.client is None:
            print("⚠ Warning: SlideEvaluator initialized but client is None")
            if not api_key:
                print("  → API key not found in environment variable GEOGRAPHY_KEY")
        else:
            print("✓ SlideEvaluator initialized successfully with Gemini API client")
    
    return evaluator

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
                overlap=3,
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
            
            # ==================== SLIDE GENERATION STAGE ====================
            print("Starting Slide Generation stage...")
            generator = get_slide_generator()
            if not generator:
                return jsonify({'error': 'Generator failed to initialize (check API key or dependencies)'}), 500
            
            # Check if generator has a valid client
            if hasattr(generator, 'client') and generator.client is None:
                return jsonify({
                    'error': 'Gemini API client not initialized. Please check your GEMINI_API_KEY environment variable.'
                }), 500
            
            # Generate 3 versions of slides
            print(f"Calling generate_multiple_versions with json_filepath: {json_filepath}")
            try:
                slide_versions = generator.generate_multiple_versions(
                    retrieval_json_path=json_filepath,
                    num_versions=3,
                    num_slides=3
                )
                if slide_versions is None:
                    print(f"generate_multiple_versions returned: None")
                else:
                    print(f"generate_multiple_versions returned: {type(slide_versions)}, length: {len(slide_versions)}")
            except Exception as e:
                import traceback
                error_msg = f"Exception during slide generation: {str(e)}"
                print(error_msg)
                traceback.print_exc()
                return jsonify({'error': error_msg}), 500
            
            if not slide_versions or len(slide_versions) == 0:
                error_msg = 'Failed to generate slides. All versions failed. Check console logs for details.'
                print(error_msg)
                return jsonify({'error': error_msg}), 500
            
            print(f"Generated {len(slide_versions)} slide versions.")
            
            # Save each version
            versions_data = []
            for i, version in enumerate(slide_versions):
                version_filename = f"{submission_id}_slides_v{i+1}.json"
                version_filepath = os.path.join(app.config['SLIDES_OUTPUT_FOLDER'], version_filename)
                
                try:
                    with open(version_filepath, 'w', encoding='utf-8') as f:
                        json.dump(version, f, indent=2, ensure_ascii=False)
                    
                    versions_data.append({
                        'version_number': i + 1,
                        'file_path': version_filepath
                    })
                    print(f"Saved slide version {i+1} to {version_filepath}")
                except Exception as e:
                    print(f"Error saving version {i+1}: {e}")
                    continue
            
            if not versions_data:
                return jsonify({'error': 'Failed to save any slide versions'}), 500
            
            submission_data['slide_versions'] = versions_data
            submission_data['status'] = 'slides_generated'
            
            # ==================== EVALUATION STAGE ====================
            print("Starting Evaluation stage...")
            eval_system = get_evaluator()
            evaluations = []
            if eval_system:
                for version_data in versions_data:
                    try:
                        with open(version_data['file_path'], 'r', encoding='utf-8') as f:
                            version_slides = json.load(f)
                        
                        evaluation = eval_system.evaluate_slides(
                            slides_data=version_slides,
                            retrieval_json_path=json_filepath,
                            description=description,
                            audience_type=audience_type
                        )
                        
                        evaluation['version_number'] = version_data['version_number']
                        evaluations.append(evaluation)
                    except Exception as e:
                        print(f"Error evaluating version {version_data['version_number']}: {e}")
                        # Continue with other versions even if one fails
                        continue
                
                if evaluations:
                    # Save evaluations
                    eval_filename = f"{submission_id}_evaluations.json"
                    eval_filepath = os.path.join(app.config['SLIDES_OUTPUT_FOLDER'], eval_filename)
                    with open(eval_filepath, 'w', encoding='utf-8') as f:
                        json.dump(evaluations, f, indent=2, ensure_ascii=False)
                    
                    print("Evaluation file successfully saved.")
                    submission_data['evaluations'] = evaluations
                    submission_data['status'] = 'evaluation_completed'
                else:
                    print("Warning: No evaluations were generated")
                    submission_data['status'] = 'slides_generated'  # Keep status as slides_generated
            
            # Return success response
            return jsonify({
                'success': True,
                'message': 'Form submitted and processed successfully',
                'submission_id': submission_id,
                'status': submission_data['status'],
                'json_output_path': submission_data.get('json_output_path'),
                'relevant_chunks_count': submission_data.get('relevant_chunks_count', 0),
                'total_chunks': submission_data.get('total_chunks', 0),
                'has_slides': 'slide_versions' in submission_data,
                'num_versions': len(submission_data.get('slide_versions', [])),
                'has_evaluations': 'evaluations' in submission_data
            }), 200

        except Exception as e:
            # Catching errors within the processing pipeline (retrieval, gen, eval)
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Processing Error: {str(e)}'}), 500

    except Exception as e:
        # Catching errors during file upload and initial validation
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Upload/Validation Error: {str(e)}'}), 500
@app.route('/review/<submission_id>')
def review_slides(submission_id):
    """Render the critic in the loop review page"""
    return render_template('review.html', submission_id=submission_id)

@app.route('/api/slides/<submission_id>')
def get_slides(submission_id):
    """Get all slide versions and evaluations for a submission"""
    # Load evaluations
    eval_filepath = os.path.join(app.config['SLIDES_OUTPUT_FOLDER'], f"{submission_id}_evaluations.json")
    
    if not os.path.exists(eval_filepath):
        return jsonify({'error': 'Evaluations not found'}), 404
    
    with open(eval_filepath, 'r', encoding='utf-8') as f:
        evaluations = json.load(f)
    
    # Load slide versions
    versions_data = []
    for eval_data in evaluations:
        version_num = eval_data['version_number']
        version_filepath = os.path.join(app.config['SLIDES_OUTPUT_FOLDER'], f"{submission_id}_slides_v{version_num}.json")
        
        if os.path.exists(version_filepath):
            with open(version_filepath, 'r', encoding='utf-8') as f:
                slides_data = json.load(f)
            
            versions_data.append({
                'version_number': version_num,
                'slides': slides_data,
                'evaluation': eval_data
            })
    
    return jsonify({
        'success': True,
        'versions': versions_data
    }), 200

@app.route('/api/select-slide', methods=['POST'])
def select_slide():
    """Handle user selection of a slide version and generate presentation"""
    data = request.json
    submission_id = data.get('submission_id')
    version_number = data.get('version_number')
    feedback = data.get('feedback', '')
    
    if not submission_id or not version_number:
        return jsonify({'error': 'Missing submission_id or version_number'}), 400
    
    try:
        # Load the selected slide version
        version_filepath = os.path.join(app.config['SLIDES_OUTPUT_FOLDER'], f"{submission_id}_slides_v{version_number}.json")
        
        if not os.path.exists(version_filepath):
            return jsonify({'error': f'Slide version {version_number} not found'}), 404
        
        with open(version_filepath, 'r', encoding='utf-8') as f:
            slides_data = json.load(f)
        
        # Save feedback if provided
        if feedback:
            feedback_data = {
                'submission_id': submission_id,
                'version_number': version_number,
                'feedback': feedback,
                'timestamp': datetime.now().isoformat()
            }
            feedback_filepath = os.path.join(app.config['SLIDES_OUTPUT_FOLDER'], f"{submission_id}_selection_feedback.json")
            with open(feedback_filepath, 'w', encoding='utf-8') as f:
                json.dump(feedback_data, f, indent=2)
        
        # Create PowerPoint presentation
        presentation_filename = f"{submission_id}_version_{version_number}.pptx"
        presentation_filepath = os.path.join(app.config['PRESENTATIONS_FOLDER'], presentation_filename)
        
        create_presentation_from_slides_data(slides_data, presentation_filepath)
        
        return jsonify({
            'success': True,
            'message': 'Presentation created successfully',
            'download_url': f'/api/download-presentation/{presentation_filename}'
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error creating presentation: {str(e)}'}), 500

@app.route('/api/feedback', methods=['POST'])
def handle_feedback():
    """Handle user feedback for content/style correction - implements feedback loops"""
    data = request.json
    submission_id = data.get('submission_id')
    feedback_type = data.get('feedback_type')  # 'content', 'style', 'information'
    feedback_text = data.get('feedback', '')
    original_description = data.get('original_description', '')
    
    if not submission_id or not feedback_type:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Load original submission data
    json_filepath = os.path.join(app.config['JSON_OUTPUT_FOLDER'], f"{submission_id}_retrieval_output.json")
    if not os.path.exists(json_filepath):
        return jsonify({'error': 'Original submission not found'}), 404
    
    with open(json_filepath, 'r', encoding='utf-8') as f:
        retrieval_data = json.load(f)
    
    metadata = retrieval_data.get('metadata', {})
    original_desc = metadata.get('description', '')
    audience_type = metadata.get('audience_type', 'general')
    pdf_path = metadata.get('pdf_path', '')
    
    # Save feedback
    feedback_data = {
        'submission_id': submission_id,
        'feedback_type': feedback_type,
        'feedback_text': feedback_text,
        'original_description': original_description or original_desc,
        'timestamp': datetime.now().isoformat()
    }
    
    feedback_filepath = os.path.join(app.config['SLIDES_OUTPUT_FOLDER'], f"{submission_id}_feedback_{feedback_type}.json")
    with open(feedback_filepath, 'w', encoding='utf-8') as f:
        json.dump(feedback_data, f, indent=2)
    
    # FEEDBACK LOOP 1: Content Correction - Re-run retrieval
    if feedback_type == 'content':
        updated_description = feedback_text if feedback_text else original_description or original_desc
        print(f"Feedback Loop 1: Re-running retrieval with updated description")
        
        retrieval_output = retrieval_system.process_document(
            pdf_path=pdf_path,
            description=updated_description,
            audience_type=audience_type,
            chunk_size=500,
            overlap=50,
            similarity_threshold=0.5,
            top_k=20
        )
        
        # Save updated JSON
        json_filepath = os.path.join(app.config['JSON_OUTPUT_FOLDER'], f"{submission_id}_retrieval_output.json")
        retrieval_system.save_to_json(retrieval_output, json_filepath)
        
        # Re-generate slides
        return regenerate_slides(submission_id, json_filepath, updated_description, audience_type)
    
    # FEEDBACK LOOP 2 & 3: Information/Style Correction - Re-run slide generation
    elif feedback_type in ['style', 'information']:
        print(f"Feedback Loop {'3' if feedback_type == 'style' else '2'}: Re-generating slides")
        return regenerate_slides(submission_id, json_filepath, original_desc, audience_type, feedback_text)
    
    else:
        return jsonify({'error': 'Invalid feedback type'}), 400

def regenerate_slides(submission_id: str, json_filepath: str, description: str, 
                      audience_type: str, style_feedback: str = '') -> dict:
    """Helper function to regenerate slides (used in feedback loops)"""
    generator = get_slide_generator()
    if not generator:
        return jsonify({'error': 'Slide generator not available'}), 500
    
    # Generate new versions
    slide_versions = generator.generate_multiple_versions(
        retrieval_json_path=json_filepath,
        num_versions=3,
        num_slides=3
    )
    
    if not slide_versions:
        return jsonify({'error': 'Failed to generate slides'}), 500
    
    # Save versions
    versions_data = []
    for i, version in enumerate(slide_versions):
        version_filename = f"{submission_id}_slides_v{i+1}.json"
        version_filepath = os.path.join(app.config['SLIDES_OUTPUT_FOLDER'], version_filename)
        
        with open(version_filepath, 'w', encoding='utf-8') as f:
            json.dump(version, f, indent=2, ensure_ascii=False)
        
        versions_data.append({
            'version_number': i + 1,
            'file_path': version_filepath
        })
    
    # Re-evaluate
    eval_system = get_evaluator()
    evaluations = []
    if eval_system:
        for version_data in versions_data:
            with open(version_data['file_path'], 'r', encoding='utf-8') as f:
                version_slides = json.load(f)
            
            evaluation = eval_system.evaluate_slides(
                slides_data=version_slides,
                retrieval_json_path=json_filepath,
                description=description,
                audience_type=audience_type
            )
            
            evaluation['version_number'] = version_data['version_number']
            evaluations.append(evaluation)
    
    # Save evaluations
    eval_filename = f"{submission_id}_evaluations.json"
    eval_filepath = os.path.join(app.config['SLIDES_OUTPUT_FOLDER'], eval_filename)
    with open(eval_filepath, 'w', encoding='utf-8') as f:
        json.dump(evaluations, f, indent=2, ensure_ascii=False)
    
    return jsonify({
        'success': True,
        'message': 'Slides regenerated successfully',
        'num_versions': len(versions_data),
        'has_evaluations': len(evaluations) > 0,
        'redirect_url': f'/review/{submission_id}'
    }), 200

@app.route('/api/regenerate', methods=['POST'])
def regenerate_with_quality_check():
    """FEEDBACK LOOP 4: Quality Iteration - Regenerate until scores are high enough"""
    data = request.json
    submission_id = data.get('submission_id')
    min_score = data.get('min_score', EVALUATION_THRESHOLD)
    max_iterations = data.get('max_iterations', MAX_ITERATIONS)
    
    if not submission_id:
        return jsonify({'error': 'Missing submission_id'}), 400
    
    json_filepath = os.path.join(app.config['JSON_OUTPUT_FOLDER'], f"{submission_id}_retrieval_output.json")
    if not os.path.exists(json_filepath):
        return jsonify({'error': 'Submission not found'}), 404
    
    with open(json_filepath, 'r', encoding='utf-8') as f:
        retrieval_data = json.load(f)
    
    metadata = retrieval_data.get('metadata', {})
    description = metadata.get('description', '')
    audience_type = metadata.get('audience_type', 'general')
    
    generator = get_slide_generator()
    eval_system = get_evaluator()
    
    if not generator or not eval_system:
        return jsonify({'error': 'Generator or evaluator not available'}), 500
    
    # Iterate until we get good scores
    best_score = 0
    best_version = None
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"Quality iteration {iteration}/{max_iterations}")
        
        # Generate one version
        slides_data = generator.generate_slides(
            retrieval_json_path=json_filepath,
            num_slides=3
        )
        
        # Evaluate
        evaluation = eval_system.evaluate_slides(
            slides_data=slides_data,
            retrieval_json_path=json_filepath,
            description=description,
            audience_type=audience_type
        )
        
        score = evaluation.get('overall_score', 0)
        print(f"Iteration {iteration} score: {score}")
        
        if score > best_score:
            best_score = score
            best_version = slides_data
            best_version['evaluation'] = evaluation
        
        # Check if we've reached threshold
        if score >= min_score:
            print(f"Threshold reached! Score: {score}")
            break
    
    if not best_version:
        return jsonify({'error': 'Failed to generate acceptable slides'}), 500
    
    # Save best version
    version_filepath = os.path.join(app.config['SLIDES_OUTPUT_FOLDER'], f"{submission_id}_slides_best.json")
    with open(version_filepath, 'w', encoding='utf-8') as f:
        json.dump(best_version, f, indent=2, ensure_ascii=False)
    
    return jsonify({
        'success': True,
        'message': f'Generated slides with score {best_score:.1f} after {iteration} iterations',
        'score': best_score,
        'iterations': iteration,
        'meets_threshold': best_score >= min_score
    }), 200

@app.route('/api/generate-three-versions/<submission_id>', methods=['POST'])
def generate_three_ppt_versions(submission_id):
    """Generate 3 different themed PowerPoint presentations"""
    # Load JSON file
    json_filepath = os.path.join(app.config['JSON_OUTPUT_FOLDER'], f"{submission_id}_retrieval_output.json")
    if not os.path.exists(json_filepath):
        return jsonify({'error': 'Retrieval output not found'}), 404
    
    # Import the generator function
    from generate_three_ppt_versions import generate_three_ppt_versions
    
    # Generate presentations
    output_dir = app.config['PRESENTATIONS_FOLDER']
    generated_files = generate_three_ppt_versions(json_filepath, output_dir)
    
    if generated_files:
        return jsonify({
            'success': True,
            'message': f'Generated {len(generated_files)} themed presentations',
            'files': [os.path.basename(f) for f in generated_files],
            'download_urls': [f'/api/download-presentation/{os.path.basename(f)}' for f in generated_files]
        }), 200
    else:
        return jsonify({'error': 'Failed to generate presentations'}), 500

@app.route('/api/download-presentation/<filename>')
def download_presentation_file(filename):
    """Download a specific presentation file"""
    filepath = os.path.join(app.config['PRESENTATIONS_FOLDER'], filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'Presentation not found'}), 404
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File size exceeds 50MB limit'}), 413

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

