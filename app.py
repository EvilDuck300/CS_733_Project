from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import json
from typing import Optional

# Import all systems
from utils.retrieval_gnn import GNNRetrieval
from utils.slide_generator import SlideGenerator
from utils.evaluator import SlideEvaluator
from utils.presentation_builder import create_presentation_from_slides_data
from utils.vlm_analyzer import VLMAnalyzer, analyze_presentation_vlm

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

def get_slide_generator():
    """Get or initialize slide generator"""
    global slide_generator
    if slide_generator is None:
        try:
            slide_generator = SlideGenerator()
        except (ValueError, ImportError) as e:
            print(f"Warning: Slide generator not available: {e}")
            print("You can upload the JSON retrieval output to Gemini website to generate PowerPoint.")
    return slide_generator

def get_evaluator():
    """Get or initialize evaluator"""
    global evaluator
    if evaluator is None:
        try:
            evaluator = SlideEvaluator()
        except (ValueError, ImportError) as e:
            print(f"Warning: Evaluator not available: {e}")
            print("You can upload the JSON retrieval output to Gemini website to generate PowerPoint.")
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
            try:
                print("Starting Slide Generation stage...")
                generator = get_slide_generator()
                if generator:
                    # Generate 3 versions of slides
                    slide_versions = generator.generate_multiple_versions(
                        retrieval_json_path=json_filepath,
                        num_versions=3,
                        num_slides=3
                    )
                    
                    if slide_versions:
                        # Save each version
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
                        
                        submission_data['status'] = 'slides_generated'
                        submission_data['slide_versions'] = versions_data
                        print(f"Generated {len(slide_versions)} slide versions")
                        
                        # ==================== EVALUATION STAGE ====================
                        try:
                            print("Starting Evaluation stage...")
                            eval_system = get_evaluator()
                            if eval_system:
                                evaluations = []
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
                                
                                # FEEDBACK LOOP 4: Quality Iteration - Check if scores meet threshold
                                all_scores_meet_threshold = all(
                                    eval_data.get('overall_score', 0) >= EVALUATION_THRESHOLD 
                                    for eval_data in evaluations
                                )
                                
                                if not all_scores_meet_threshold:
                                    print(f"Some scores below threshold ({EVALUATION_THRESHOLD}). Attempting quality iteration...")
                                    # Try to generate better versions
                                    try:
                                        improved_versions = []
                                        for i in range(min(2, MAX_ITERATIONS)):  # Try up to 2 more iterations
                                            new_slides = generator.generate_slides(
                                                retrieval_json_path=json_filepath,
                                                num_slides=3
                                            )
                                            new_eval = eval_system.evaluate_slides(
                                                slides_data=new_slides,
                                                retrieval_json_path=json_filepath,
                                                description=description,
                                                audience_type=audience_type
                                            )
                                            
                                            if new_eval.get('overall_score', 0) >= EVALUATION_THRESHOLD:
                                                # Save improved version
                                                version_num = len(versions_data) + 1
                                                version_filename = f"{submission_id}_slides_v{version_num}.json"
                                                version_filepath = os.path.join(app.config['SLIDES_OUTPUT_FOLDER'], version_filename)
                                                
                                                with open(version_filepath, 'w', encoding='utf-8') as f:
                                                    json.dump(new_slides, f, indent=2, ensure_ascii=False)
                                                
                                                new_eval['version_number'] = version_num
                                                evaluations.append(new_eval)
                                                improved_versions.append({
                                                    'version_number': version_num,
                                                    'file_path': version_filepath
                                                })
                                                
                                                if len(improved_versions) >= 1:  # Add at least 1 improved version
                                                    break
                                        
                                        if improved_versions:
                                            versions_data.extend(improved_versions)
                                            print(f"Added {len(improved_versions)} improved version(s)")
                                    except Exception as e:
                                        print(f"Quality iteration failed: {e}")
                                
                                # Save evaluations
                                eval_filename = f"{submission_id}_evaluations.json"
                                eval_filepath = os.path.join(app.config['SLIDES_OUTPUT_FOLDER'], eval_filename)
                                with open(eval_filepath, 'w', encoding='utf-8') as f:
                                    json.dump(evaluations, f, indent=2, ensure_ascii=False)
                                
                                submission_data['status'] = 'evaluation_completed'
                                submission_data['evaluations'] = evaluations
                                submission_data['evaluation_file'] = eval_filepath
                                print(f"Evaluated {len(evaluations)} slide versions")
                        except Exception as e:
                            print(f"Error in Evaluation stage: {str(e)}")
                            submission_data['evaluation_error'] = str(e)
                else:
                    print("Warning: Slide generator not available (missing OpenAI API key)")
            except Exception as e:
                print(f"Error in Slide Generation stage: {str(e)}")
                submission_data['slide_generation_error'] = str(e)
            
        except Exception as e:
            print(f"Error in Retrieval stage: {str(e)}")
            submission_data['status'] = 'retrieval_failed'
            submission_data['retrieval_error'] = str(e)
        
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
        print(f"Error processing submission: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/review/<submission_id>')
def review_slides(submission_id):
    """Render the critic in the loop review page"""
    return render_template('review.html', submission_id=submission_id)

@app.route('/api/slides/<submission_id>')
def get_slides(submission_id):
    """Get all slide versions and evaluations for a submission"""
    try:
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
        
    except Exception as e:
        print(f"Error loading slides: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/select-slide', methods=['POST'])
def select_slide():
    """Handle user selection of best slide version"""
    try:
        data = request.json
        submission_id = data.get('submission_id')
        version_number = data.get('version_number')
        feedback = data.get('feedback', '')
        
        if not submission_id or not version_number:
            return jsonify({'error': 'Missing submission_id or version_number'}), 400
        
        # Load selected version
        version_filepath = os.path.join(app.config['SLIDES_OUTPUT_FOLDER'], f"{submission_id}_slides_v{version_number}.json")
        
        if not os.path.exists(version_filepath):
            return jsonify({'error': 'Slide version not found'}), 404
        
        with open(version_filepath, 'r', encoding='utf-8') as f:
            slides_data = json.load(f)
        
        # Create PowerPoint presentation
        pptx_filename = f"{submission_id}_final_presentation.pptx"
        pptx_filepath = os.path.join(app.config['PRESENTATIONS_FOLDER'], pptx_filename)
        
        create_presentation_from_slides_data(slides_data, pptx_filepath)
        
        # Save selection record
        selection_data = {
            'submission_id': submission_id,
            'selected_version': version_number,
            'feedback': feedback,
            'presentation_path': pptx_filepath,
            'timestamp': datetime.now().isoformat()
        }
        
        selection_filepath = os.path.join(app.config['SLIDES_OUTPUT_FOLDER'], f"{submission_id}_selection.json")
        with open(selection_filepath, 'w', encoding='utf-8') as f:
            json.dump(selection_data, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Slide selected successfully',
            'presentation_path': pptx_filepath,
            'download_url': f'/api/download/{submission_id}'
        }), 200
        
    except Exception as e:
        print(f"Error selecting slide: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<submission_id>')
def download_presentation(submission_id):
    """Download the final PowerPoint presentation"""
    try:
        pptx_filename = f"{submission_id}_final_presentation.pptx"
        pptx_filepath = os.path.join(app.config['PRESENTATIONS_FOLDER'], pptx_filename)
        
        if not os.path.exists(pptx_filepath):
            return jsonify({'error': 'Presentation not found'}), 404
        
        return send_file(pptx_filepath, as_attachment=True, download_name=pptx_filename)
        
    except Exception as e:
        print(f"Error downloading presentation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-vlm/<submission_id>', methods=['POST'])
def analyze_presentation_with_vlm(submission_id):
    """Analyze PowerPoint presentation using VLM (Gemini Vision)"""
    try:
        pptx_filename = f"{submission_id}_final_presentation.pptx"
        pptx_filepath = os.path.join(app.config['PRESENTATIONS_FOLDER'], pptx_filename)
        
        if not os.path.exists(pptx_filepath):
            return jsonify({'error': 'Presentation not found'}), 404
        
        # Get analysis type from request (optional)
        data = request.json or {}
        analysis_type = data.get('analysis_type', 'comprehensive')
        
        # Analyze with VLM
        result = analyze_presentation_vlm(pptx_filepath)
        
        # Save analysis results
        analysis_filename = f"{submission_id}_vlm_analysis.json"
        analysis_filepath = os.path.join(app.config['SLIDES_OUTPUT_FOLDER'], analysis_filename)
        with open(analysis_filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': 'VLM analysis completed',
            'analysis': result,
            'analysis_file': analysis_filepath
        }), 200
        
    except Exception as e:
        print(f"Error analyzing presentation with VLM: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/vlm-instructions/<submission_id>')
def get_vlm_instructions(submission_id):
    """Get instructions for analyzing PowerPoint with Gemini website"""
    try:
        pptx_filename = f"{submission_id}_final_presentation.pptx"
        pptx_filepath = os.path.join(app.config['PRESENTATIONS_FOLDER'], pptx_filename)
        
        if not os.path.exists(pptx_filepath):
            return jsonify({'error': 'Presentation not found'}), 404
        
        analyzer = VLMAnalyzer()
        instructions = analyzer.analyze_with_gemini_website(pptx_filepath)
        
        return jsonify({
            'success': True,
            'instructions': instructions,
            'download_url': f'/api/download/{submission_id}'
        }), 200
        
    except Exception as e:
        print(f"Error getting VLM instructions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def handle_feedback():
    """Handle user feedback for content/style correction - implements feedback loops"""
    try:
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
            
            try:
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
                
            except Exception as e:
                return jsonify({'error': f'Error re-running retrieval: {str(e)}'}), 500
        
        # FEEDBACK LOOP 2 & 3: Information/Style Correction - Re-run slide generation
        elif feedback_type in ['style', 'information']:
            print(f"Feedback Loop {'3' if feedback_type == 'style' else '2'}: Re-generating slides")
            return regenerate_slides(submission_id, json_filepath, original_desc, audience_type, feedback_text)
        
        else:
            return jsonify({'error': 'Invalid feedback type'}), 400
        
    except Exception as e:
        print(f"Error handling feedback: {str(e)}")
        return jsonify({'error': str(e)}), 500

def regenerate_slides(submission_id: str, json_filepath: str, description: str, 
                      audience_type: str, style_feedback: str = '') -> dict:
    """Helper function to regenerate slides (used in feedback loops)"""
    try:
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
        
    except Exception as e:
        print(f"Error regenerating slides: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/regenerate', methods=['POST'])
def regenerate_with_quality_check():
    """FEEDBACK LOOP 4: Quality Iteration - Regenerate until scores are high enough"""
    try:
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
        
    except Exception as e:
        print(f"Error in quality iteration: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File size exceeds 50MB limit'}), 413

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

