"""
Task manager module for the AI-Powered Browser Automation Tool.
This module handles the orchestration of tasks, connecting the web API with automation modules.
"""
import logging
import uuid
import threading
import time
from enum import Enum

# Import automation modules
from automation.browser_automation import BrowserAutomation
from automation.ai_processor import AIProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Enum representing the possible statuses of a task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Task:
    """Class representing an automation task."""
    
    def __init__(self, url, description, task_type="web_scrape"):
        """
        Initialize a new task.
        
        Args:
            url (str): The URL to automate
            description (str): Description of the task
            task_type (str): Type of task (e.g., 'web_scrape', 'form_fill')
        """
        self.id = str(uuid.uuid4())
        self.url = url
        self.description = description
        self.task_type = task_type
        self.status = TaskStatus.PENDING
        self.created_at = time.time()
        self.updated_at = self.created_at
        self.result = None
        self.error = None
    
    def to_dict(self):
        """
        Convert the task to a dictionary for JSON serialization.
        
        Returns:
            dict: Task as a dictionary
        """
        return {
            "id": self.id,
            "url": self.url,
            "description": self.description,
            "task_type": self.task_type,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "result": self.result,
            "error": self.error
        }
    
    def update_status(self, status, error=None):
        """
        Update the status of the task.
        
        Args:
            status (TaskStatus): New status
            error (str, optional): Error message if status is FAILED
        """
        self.status = status
        if error:
            self.error = error
        self.updated_at = time.time()

class TaskManager:
    """Class to manage automation tasks."""
    
    def __init__(self):
        """Initialize the task manager."""
        self.tasks = {}
        self.lock = threading.Lock()
    
    def create_task(self, url, description, task_type="web_scrape"):
        """
        Create a new task.
        
        Args:
            url (str): The URL to automate
            description (str): Description of the task
            task_type (str): Type of task
            
        Returns:
            Task: The created task
        """
        task = Task(url, description, task_type)
        with self.lock:
            self.tasks[task.id] = task
        logger.info(f"Created task {task.id} for URL: {url}")
        return task
    
    def get_task(self, task_id):
        """
        Get a task by ID.
        
        Args:
            task_id (str): ID of the task
            
        Returns:
            Task or None: The task if found, None otherwise
        """
        with self.lock:
            return self.tasks.get(task_id)
    
    def get_all_tasks(self):
        """
        Get all tasks.
        
        Returns:
            list: List of all tasks
        """
        with self.lock:
            return list(self.tasks.values())
    
    def execute_task(self, task_id):
        """
        Execute a task asynchronously.
        
        Args:
            task_id (str): ID of the task to execute
            
        Returns:
            bool: True if task was started, False otherwise
        """
        task = self.get_task(task_id)
        if not task or task.status != TaskStatus.PENDING:
            return False
        
        # Update task status to RUNNING
        task.update_status(TaskStatus.RUNNING)
        
        # Start a thread to execute the task
        thread = threading.Thread(target=self._task_worker, args=(task_id,))
        thread.daemon = True
        thread.start()
        
        logger.info(f"Started execution of task {task_id}")
        return True
    
    def _task_worker(self, task_id):
        """
        Worker function to execute a task in a separate thread.
        
        Args:
            task_id (str): ID of the task to execute
        """
        task = self.get_task(task_id)
        if not task:
            return
        
        try:
            logger.info(f"Executing task {task_id}")
            
            # Initialize automation components
            browser = BrowserAutomation(headless=True)
            ai_processor = AIProcessor()
            
            # Navigate to URL
            if not browser.navigate_to_url(task.url):
                raise Exception(f"Failed to navigate to URL: {task.url}")
            
            result = {}
            
            # Handle different task types
            if task.task_type == "web_scrape":
                # Extract basic web page data
                data = browser.extract_data({
                    "main_content": "main, body",
                    "title": "h1, title",
                    "paragraphs": "p"
                })
                
                # Process with AI
                if "main_content" in data and data["main_content"]:
                    summary = ai_processor.summarize_text(data["main_content"])
                    result = {
                        "title": data.get("title", "No title found"),
                        "summary": summary
                    }
                else:
                    result = {
                        "title": data.get("title", "No title found"),
                        "error": "Could not extract main content"
                    }
                
            elif task.task_type == "form_fill":
                # Parse form data from description
                try:
                    # Expecting description in format: "field1=value1,field2=value2"
                    form_data = {}
                    if "," in task.description:
                        for field_data in task.description.split(","):
                            if "=" in field_data:
                                field, value = field_data.split("=", 1)
                                form_data[field.strip()] = value.strip()
                    
                    # Fill the form with the provided data
                    if form_data:
                        success = browser.fill_form(form_data)
                        result = {
                            "success": success,
                            "message": "Form filled successfully" if success else "Failed to fill form"
                        }
                    else:
                        result = {
                            "success": False,
                            "message": "No valid form data found in description"
                        }
                except Exception as form_error:
                    result = {
                        "success": False,
                        "message": f"Form fill error: {str(form_error)}"
                    }
                
            elif task.task_type == "data_extraction":
                # Extract specific data based on the description
                try:
                    # Get the content and categorize it
                    data = browser.extract_data({
                        "main_content": "main, body",
                        "title": "h1, title"
                    })
                    
                    categories = ai_processor.categorize_content(data.get("main_content", ""))
                    
                    # Extract information based on the primary category
                    if "primary_category" in categories:
                        info_type = categories["primary_category"]
                        extracted_info = ai_processor.extract_key_information(
                            data.get("main_content", ""),
                            info_type
                        )
                        
                        result = {
                            "title": data.get("title", "No title found"),
                            "category": info_type,
                            "extracted_information": extracted_info
                        }
                    else:
                        result = {
                            "title": data.get("title", "No title found"),
                            "message": "Could not determine content category"
                        }
                except Exception as extract_error:
                    result = {
                        "success": False,
                        "message": f"Data extraction error: {str(extract_error)}"
                    }
            else:
                # Unknown task type
                result = {
                    "error": f"Unknown task type: {task.task_type}"
                }
            
            # Close the browser
            browser.close()
            
            # Store result
            task.result = result
            
            task.update_status(TaskStatus.COMPLETED)
            logger.info(f"Completed task {task_id}")
            
        except Exception as e:
            error_msg = f"Error executing task: {str(e)}"
            logger.error(error_msg)
            task.update_status(TaskStatus.FAILED, error_msg)

# Create a global instance of the task manager
task_manager = TaskManager()
