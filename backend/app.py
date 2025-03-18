"""
Main application file for the AI-Powered Browser Automation Tool.
This file initializes the Flask server and defines API endpoints.
"""
import logging
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Import task manager
from task_manager import task_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all domains on all routes

@app.route('/api/test', methods=['GET'])
def test_connection():
    """API endpoint to test connectivity."""
    logger.info("Test connection endpoint called")
    return jsonify({
        "status": "success",
        "message": "API connection successful!"
    })

@app.route('/api/task', methods=['POST'])
def create_task():
    """API endpoint to create a new automation task."""
    try:
        task_data = request.get_json()
        # Validate required fields
        if not task_data or 'url' not in task_data or 'description' not in task_data:
            return jsonify({
                "status": "error",
                "message": "Missing required fields: url and description"
            }), 400
        
        logger.info(f"Task creation request received for URL: {task_data['url']}")
        
        # Create a task using the task manager
        task_type = task_data.get('task_type', 'web_scrape')
        task = task_manager.create_task(
            url=task_data['url'],
            description=task_data['description'],
            task_type=task_type
        )
        
        # Start task execution
        task_manager.execute_task(task.id)
        
        return jsonify({
            "status": "success",
            "message": "Task created and started successfully",
            "task": task.to_dict()
        })
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to create task: {str(e)}"
        }), 500

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task(task_id):
    """API endpoint to get a specific task's details."""
    task = task_manager.get_task(task_id)
    if not task:
        return jsonify({
            "status": "error",
            "message": f"Task with ID {task_id} not found"
        }), 404
    
    return jsonify({
        "status": "success",
        "task": task.to_dict()
    })

@app.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    """API endpoint to get all tasks."""
    tasks = task_manager.get_all_tasks()
    return jsonify({
        "status": "success",
        "tasks": [task.to_dict() for task in tasks]
    })

# Serve frontend files
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve frontend files."""
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    return send_from_directory(frontend_dir, path)

if __name__ == '__main__':
    logger.info("Starting Flask server")
    # Use port 5001 instead of 5000 (which is often used by AirPlay on macOS)
    app.run(debug=True, host='0.0.0.0', port=5001)
