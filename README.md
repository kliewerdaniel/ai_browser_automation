# AI-Powered Browser Automation Tool

This application automates repetitive web tasks by leveraging browser automation for web interactions and AI for data processing and summarization. It allows users to define automation tasks (e.g., gathering news summaries, data extraction) via a simple web interface.

## Project Overview

**Key Components:**
- **Frontend:** User interface for task configuration and result display (HTML, CSS, JavaScript).
- **Backend:** Flask-based server handling API requests, task scheduling, and integration with both Browser-Use and Ollama.
- **Automation Scripts:** Python modules that utilize the Browser-Use library to perform web automation.
- **AI Processing:** Integration with Ollama's language models to process and summarize data collected from the web.

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)
- Node.js and npm (optional, for additional development tools)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-browser-automation.git
   cd ai-browser-automation
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Note about placeholder dependencies**
   
   The `requirements.txt` file contains placeholder comments for the Browser-Use library and Ollama SDK. As these are hypothetical or in-development libraries, you may need to replace these with actual packages or install them from specific sources when they become available.

## Running the Application

1. **Start the Flask server**
   ```bash
   cd backend
   python app.py
   ```

2. **Access the web interface**
   
   Open your browser and navigate to: `http://localhost:5000`

## Usage

1. **Create a new automation task**
   - Enter a target URL
   - Provide a description of what you want to automate
   - Select the task type
   - Click "Start Task"

2. **View task results**
   - The results will appear in the "Task Results" section
   - Previous tasks can be viewed in the "Recent Tasks" section

3. **Task types**
   - **Web Scraping:** Extract data from websites
   - **Form Filling:** Automate form submissions
   - **Data Extraction:** Extract specific types of data

## Project Structure

```
ai_browser_automation/
├── frontend/                # Frontend files
│   ├── index.html           # Main HTML file
│   ├── styles.css           # CSS styles
│   └── app.js               # Frontend JavaScript
├── backend/                 # Flask backend
│   ├── app.py               # Main Flask application
│   └── task_manager.py      # Task management module
├── automation/              # Automation scripts
│   ├── browser_automation.py # Browser automation module
│   └── ai_processor.py      # AI processing module
├── tests/                   # Test files
└── docs/                    # Documentation
```

## Development

This project follows an iterative development approach:

1. **Environment Setup & Basic API**
2. **Frontend & User Interaction**
3. **Browser Automation Implementation**
4. **AI Integration**
5. **Testing, Optimization, and Deployment**

## License

[MIT License](LICENSE)

## Contributors

- Your Name <your.email@example.com>
