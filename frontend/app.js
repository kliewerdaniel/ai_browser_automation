/**
 * AI-Powered Browser Automation Tool - Frontend Application
 * 
 * This script handles the frontend functionality including form submissions,
 * API calls, result display, and task history management.
 */

// Configuration
const API_BASE_URL = 'http://localhost:5000/api';
const POLL_INTERVAL = 2000; // Poll for task updates every 2 seconds

// Cache DOM elements
const elements = {
    taskForm: document.getElementById('taskForm'),
    url: document.getElementById('url'),
    description: document.getElementById('description'),
    taskType: document.getElementById('taskType'),
    taskStatus: document.getElementById('taskStatus'),
    taskResults: document.getElementById('taskResults'),
    tasksList: document.getElementById('tasksList'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    notificationArea: document.getElementById('notificationArea')
};

// Store the current task being displayed
let currentTask = null;
let activeTasks = {};
let pollingInterval = null;

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initialize the application
    init();
    
    // Form submission
    elements.taskForm.addEventListener('submit', handleFormSubmit);
    
    // Test API connection on load
    testApiConnection();
});

/**
 * Initialize the application
 */
function init() {
    // Start polling for task updates
    startTaskPolling();
    
    // Load existing tasks
    fetchAllTasks();
}

/**
 * Test connection to the API
 */
async function testApiConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/test`);
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification('API connection successful', 'success');
        } else {
            showNotification('API connection issue', 'error');
        }
    } catch (error) {
        console.error('API connection error:', error);
        showNotification('Cannot connect to the API. Is the server running?', 'error');
    }
}

/**
 * Handle form submission to create a new task
 * @param {Event} event - Form submit event
 */
async function handleFormSubmit(event) {
    event.preventDefault();
    
    // Get form values
    const formData = {
        url: elements.url.value,
        description: elements.description.value,
        task_type: elements.taskType.value
    };
    
    // Validate form data
    if (!formData.url || !formData.description) {
        showNotification('Please fill in all required fields', 'error');
        return;
    }
    
    // Show loading overlay
    elements.loadingOverlay.classList.add('active');
    
    try {
        // Create task API call
        const response = await fetch(`${API_BASE_URL}/task`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Reset form
            elements.taskForm.reset();
            
            // Update current task
            currentTask = data.task;
            
            // Add to active tasks
            activeTasks[data.task.id] = data.task;
            
            // Update UI
            updateTaskStatus(data.task);
            
            // Show success message
            showNotification('Task created successfully', 'success');
            
            // Update task list
            addTaskToList(data.task);
        } else {
            showNotification(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('Error creating task:', error);
        showNotification('Failed to create task. Check console for details.', 'error');
    } finally {
        // Hide loading overlay
        elements.loadingOverlay.classList.remove('active');
    }
}

/**
 * Fetch all existing tasks
 */
async function fetchAllTasks() {
    try {
        const response = await fetch(`${API_BASE_URL}/tasks`);
        const data = await response.json();
        
        if (data.status === 'success') {
            // Clear the task list
            clearTasksList();
            
            if (data.tasks.length === 0) {
                // Show empty state
                elements.tasksList.innerHTML = '<p class="empty-state">No recent tasks to display.</p>';
                return;
            }
            
            // Add tasks to the list
            data.tasks.forEach(task => {
                addTaskToList(task);
                
                // Add to active tasks if not completed
                if (task.status !== 'completed' && task.status !== 'failed') {
                    activeTasks[task.id] = task;
                }
            });
            
            // Set the current task to the most recent one
            if (data.tasks.length > 0) {
                currentTask = data.tasks[0];
                updateTaskStatus(currentTask);
                updateTaskResults(currentTask);
            }
        } else {
            console.error('Error fetching tasks:', data.message);
        }
    } catch (error) {
        console.error('Error fetching tasks:', error);
    }
}

/**
 * Start polling for task updates
 */
function startTaskPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
    
    pollingInterval = setInterval(pollActiveTasks, POLL_INTERVAL);
}

/**
 * Poll for updates on active tasks
 */
async function pollActiveTasks() {
    const activeTaskIds = Object.keys(activeTasks);
    
    if (activeTaskIds.length === 0) {
        return;
    }
    
    for (const taskId of activeTaskIds) {
        try {
            const response = await fetch(`${API_BASE_URL}/task/${taskId}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                const task = data.task;
                
                // Update the task in our active tasks
                activeTasks[taskId] = task;
                
                // Update the task in the list
                updateTaskInList(task);
                
                // If this is the current task, update the display
                if (currentTask && currentTask.id === taskId) {
                    updateTaskStatus(task);
                    updateTaskResults(task);
                    currentTask = task;
                }
                
                // If task is completed or failed, remove from active tasks
                if (task.status === 'completed' || task.status === 'failed') {
                    delete activeTasks[taskId];
                    
                    // Show notification
                    const notificationType = task.status === 'completed' ? 'success' : 'error';
                    const message = task.status === 'completed' 
                        ? 'Task completed successfully' 
                        : `Task failed: ${task.error || 'Unknown error'}`;
                    
                    showNotification(message, notificationType);
                }
            }
        } catch (error) {
            console.error(`Error polling task ${taskId}:`, error);
        }
    }
}

/**
 * Update the task status display
 * @param {Object} task - The task object
 */
function updateTaskStatus(task) {
    if (!task) return;
    
    let statusHTML = '';
    
    // Show different status based on task state
    switch (task.status) {
        case 'pending':
            statusHTML = `
                <div class="status-pending">
                    <p>Task is pending execution.</p>
                </div>
            `;
            break;
        case 'running':
            statusHTML = `
                <div class="status-running">
                    <p>Task is currently running...</p>
                    <div class="spinner" style="width:20px;height:20px;display:inline-block;margin-left:10px;"></div>
                </div>
            `;
            break;
        case 'completed':
            statusHTML = `
                <div class="status-completed">
                    <p>Task completed successfully!</p>
                </div>
            `;
            break;
        case 'failed':
            statusHTML = `
                <div class="status-failed">
                    <p>Task failed: ${task.error || 'Unknown error'}</p>
                </div>
            `;
            break;
    }
    
    elements.taskStatus.innerHTML = statusHTML;
}

/**
 * Update the task results display
 * @param {Object} task - The task object
 */
function updateTaskResults(task) {
    if (!task || !task.result) {
        elements.taskResults.innerHTML = '<p>No results available yet.</p>';
        return;
    }
    
    // Display the task results
    let resultsHTML = '';
    
    if (task.result.title) {
        resultsHTML += `<div class="result-item">
            <div class="result-title">${task.result.title}</div>
        `;
        
        if (task.result.summary) {
            resultsHTML += `<div class="result-summary">${task.result.summary}</div>`;
        }
        
        resultsHTML += '</div>';
    } else if (typeof task.result === 'object') {
        // Display each property of the result object
        for (const [key, value] of Object.entries(task.result)) {
            resultsHTML += `<div class="result-item">
                <div class="result-title">${key}</div>
                <div class="result-summary">${value}</div>
            </div>`;
        }
    } else {
        // Fallback for simple result types
        resultsHTML = `<div class="result-item">
            <div class="result-summary">${JSON.stringify(task.result)}</div>
        </div>`;
    }
    
    elements.taskResults.innerHTML = resultsHTML;
}

/**
 * Add a task to the task list
 * @param {Object} task - The task object
 */
function addTaskToList(task) {
    // Remove empty state if present
    const emptyState = elements.tasksList.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    // Create task item element
    const taskItem = document.createElement('div');
    taskItem.className = 'task-item';
    taskItem.dataset.taskId = task.id;
    
    // Set the HTML content
    taskItem.innerHTML = `
        <div class="task-info">
            <div class="task-url">${task.url}</div>
            <div class="task-description">${task.description}</div>
        </div>
        <div class="task-status status-${task.status}">${task.status}</div>
    `;
    
    // Add click event to view this task
    taskItem.addEventListener('click', () => {
        currentTask = task;
        updateTaskStatus(task);
        updateTaskResults(task);
        
        // Highlight the selected task
        const selectedTasks = elements.tasksList.querySelectorAll('.selected');
        selectedTasks.forEach(el => el.classList.remove('selected'));
        taskItem.classList.add('selected');
    });
    
    // Add to the list (at the beginning)
    if (elements.tasksList.firstChild) {
        elements.tasksList.insertBefore(taskItem, elements.tasksList.firstChild);
    } else {
        elements.tasksList.appendChild(taskItem);
    }
}

/**
 * Update a task in the task list
 * @param {Object} task - The task object
 */
function updateTaskInList(task) {
    const taskItem = elements.tasksList.querySelector(`[data-task-id="${task.id}"]`);
    
    if (taskItem) {
        // Update status display
        const statusElement = taskItem.querySelector('.task-status');
        statusElement.className = `task-status status-${task.status}`;
        statusElement.textContent = task.status;
    }
}

/**
 * Clear the tasks list
 */
function clearTasksList() {
    elements.tasksList.innerHTML = '';
}

/**
 * Show a notification
 * @param {string} message - The notification message
 * @param {string} type - The notification type ('success', 'error', 'info')
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    // Set notification content
    notification.innerHTML = `
        <span>${message}</span>
        <button class="notification-close">&times;</button>
    `;
    
    // Add close button functionality
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', () => {
        elements.notificationArea.removeChild(notification);
    });
    
    // Add to notification area
    elements.notificationArea.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode === elements.notificationArea) {
            elements.notificationArea.removeChild(notification);
        }
    }, 5000);
}
