# AI-Powered Browser Automation Tool

An advanced web application that combines browser automation capabilities with an AI-powered reasoning engine to automate web tasks and provide intelligent analysis.

## Features

- **Browser Automation:** Automate web tasks like navigation, data extraction, and form filling
- **AI-Powered Analysis:** Leverage Ollama LLMs for intelligent reasoning and task planning
- **Modern UI:** Sleek retro-futuristic interface built with Next.js and TailwindCSS
- **Dual-Mode Interface:** Switch between automation tasks and AI assistant chat
- **Step-by-Step Reasoning:** See the AI's thought process as it works through complex tasks

## Architecture

This application integrates two main components:

1. **Flask Backend:** Handles browser automation using Selenium
2. **Next.js Frontend:** Provides a modern UI with TypeScript and component-based architecture

### Key Components

- **Browser Automation:** Uses Selenium for programmatic web interaction
- **AI Processor:** Integrates with Ollama to provide reasoning and analysis
- **Task Manager:** Coordinates between the UI and automation tasks
- **Agent System:** Breaks down tasks into logical steps with reasoning

## Prerequisites

- **Node.js**: v18+ recommended
- **Python**: 3.8+ with pip
- **Ollama**: Local LLM server with models like mistral
- **Chrome/Chromium**: For Selenium browser automation

## Setup & Installation

### 1. Install Dependencies

```bash
# Install frontend dependencies
cd integrated-app
npm install

# Install backend dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Make sure Ollama is running with the required models:

```bash
# Pull the necessary models (if not already done)
ollama pull mistral
```

### 3. Run the Development Environment

```bash
# Start the Next.js frontend and Flask backend concurrently
npm run dev:all
```

This will start:
- Next.js frontend on http://localhost:3000
- Flask backend on http://localhost:5001

## Usage

### Browser Automation Tab

1. Enter a URL to navigate to
2. Provide a description of the task you want to automate
3. Select the task type (web scraping, form filling, data extraction)
4. Click "Start Task" to begin the automation process
5. View results in real-time as they're processed

### AI Assistant Tab

1. Select your preferred Ollama model (e.g., mistral)
2. Ask a question or describe a task
3. Watch as the AI breaks it down into steps with reasoning
4. Review the comprehensive final answer

## Development

### Project Structure

```
integrated-app/
├── src/
│   ├── app/               # Next.js app directory
│   │   ├── api/           # Next.js API routes
│   │   │   ├── flask/     # Flask backend proxy
│   │   │   ├── models/    # Ollama models endpoint
│   │   │   └── run-agent/ # Agent execution endpoint
│   ├── components/        # React components
│   ├── lib/               # Shared libraries
│   └── styles/            # CSS styles
├── backend/               # Flask backend
│   ├── app.py             # Main Flask application
│   └── task_manager.py    # Task orchestration
└── automation/            # Browser automation modules
    ├── ai_processor.py    # AI text processing
    └── browser_automation.py  # Selenium browser control
```

## License

MIT
