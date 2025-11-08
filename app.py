# app.py
from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
import threading
from werkzeug.utils import secure_filename
import time
from database import (
    init_db, create_job, get_job, get_all_jobs, 
    get_job_progress, get_active_workers, get_all_workers,
    get_system_stats, mark_inactive_workers
)
from master_api import process_image_async, get_processing_status, get_heartbeat_consumer

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'bmp'}

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Initialize database
init_db()

# Start heartbeat monitoring immediately
print("💓 Initializing heartbeat monitoring...")
get_heartbeat_consumer()  # This will start the monitoring thread


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Main page with upload form."""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Monitoring dashboard page."""
    return render_template('dashboard.html')


@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Handle image upload and start processing."""
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Allowed: png, jpg, jpeg, bmp"}), 400
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    job_id = str(uuid.uuid4())
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{job_id}_processed_{filename}")
    
    file.save(input_path)
    
    # Start processing in background thread
    thread = threading.Thread(
        target=process_image_async,
        args=(job_id, input_path, output_path, filename)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "success": True,
        "job_id": job_id,
        "filename": filename,
        "message": "Image uploaded successfully. Processing started."
    }), 200


@app.route('/api/jobs/<job_id>/status', methods=['GET'])
def job_status(job_id):
    """Get processing status for a specific job."""
    progress = get_job_progress(job_id)
    if not progress:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify(progress), 200


@app.route('/api/jobs/<job_id>/result', methods=['GET'])
def job_result(job_id):
    """Get the processed image file."""
    job = get_job(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    if job['status'] != 'completed':
        return jsonify({"error": "Job not completed yet"}), 400
    
    if not job['processed_path'] or not os.path.exists(job['processed_path']):
        return jsonify({"error": "Processed image not found"}), 404
    
    return send_file(job['processed_path'], mimetype='image/jpeg')


@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """List all jobs."""
    jobs = get_all_jobs()
    return jsonify(jobs), 200


@app.route('/api/workers', methods=['GET'])
def list_workers():
    """Get all workers and their status."""
    mark_inactive_workers()  # Update inactive workers first
    workers = get_all_workers()
    return jsonify(workers), 200


@app.route('/api/workers/active', methods=['GET'])
def active_workers():
    """Get only active workers."""
    workers = get_active_workers()
    return jsonify({
        "active_count": len(workers),
        "workers": workers
    }), 200


@app.route('/api/stats', methods=['GET'])
def system_stats():
    """Get overall system statistics."""
    stats = get_system_stats()
    return jsonify(stats), 200


@app.route('/api/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a job and its associated files."""
    job = get_job(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    # Delete files if they exist
    if job.get('original_path') and os.path.exists(job['original_path']):
        os.remove(job['original_path'])
    if job.get('processed_path') and os.path.exists(job['processed_path']):
        os.remove(job['processed_path'])
    
    return jsonify({"success": True, "message": "Job deleted"}), 200


# ==================== ERROR HANDLERS ====================

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Maximum size is 50MB"}), 413


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ==================== BACKGROUND TASKS ====================

def cleanup_inactive_workers():
    """Background task to periodically mark inactive workers."""
    while True:
        time.sleep(10)  # Check every 10 seconds
        mark_inactive_workers()


# Start background cleanup thread
cleanup_thread = threading.Thread(target=cleanup_inactive_workers, daemon=True)
cleanup_thread.start()


if __name__ == '__main__':
    print("🚀 Starting Flask Web UI...")
    print("📍 Upload images at: http://localhost:5000")
    print("📊 Dashboard at: http://localhost:5000/dashboard")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
