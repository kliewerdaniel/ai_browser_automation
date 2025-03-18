"""
Browser API module for Flask backend.
This module defines the API endpoints for browser automation.
"""
import logging
import uuid
import base64
from io import BytesIO
from flask import Blueprint, request, jsonify
from automation.browser_automation import BrowserAutomation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Blueprint for browser API routes
browser_api = Blueprint('browser_api', __name__)

# Store active browser sessions
browser_sessions = {}

def get_browser_session(session_id):
    """
    Get or create a browser session.
    
    Args:
        session_id (str): The session ID
        
    Returns:
        BrowserAutomation: The browser automation instance
    """
    if session_id not in browser_sessions:
        logger.info(f"Creating new browser session with ID: {session_id}")
        browser_sessions[session_id] = BrowserAutomation(headless=True)
    return browser_sessions[session_id]

def get_screenshot(browser):
    """
    Capture a screenshot from the browser.
    
    Args:
        browser (BrowserAutomation): The browser instance
        
    Returns:
        str: Base64 encoded screenshot
    """
    try:
        # Get screenshot as PNG
        screenshot = browser.driver.get_screenshot_as_png()
        # Encode as base64
        encoded = base64.b64encode(screenshot).decode('utf-8')
        return encoded
    except Exception as e:
        logger.error(f"Error capturing screenshot: {str(e)}")
        return None

@browser_api.route('/navigate', methods=['POST'])
def navigate_browser():
    """Navigate the browser to a URL"""
    data = request.json
    url = data.get('url')
    session_id = data.get('session_id', str(uuid.uuid4()))
    
    logger.info(f"Received navigation request: URL={url}, session_id={session_id}")
    
    if not url:
        logger.error("Navigation failed: URL is required but was not provided")
        return jsonify({
            'success': False,
            'error': 'URL is required'
        }), 400
    
    # Clean the URL - remove any trailing '>' or other unwanted characters
    url = url.strip('<>')
    
    # Ensure URL has a valid protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        logger.info(f"Added https:// protocol to URL: {url}")
    
    try:
        # Get or create browser session
        browser = get_browser_session(session_id)
        
        # Navigate to the URL
        logger.info(f"Attempting to navigate to: {url}")
        success = browser.navigate_to_url(url)
        
        # Get screenshot if navigation was successful
        screenshot = get_screenshot(browser) if success else None
        
        result = {
            'success': success,
            'session_id': session_id,
            'screenshot': screenshot,
            'url': url if success else None
        }
        
        logger.info(f"Navigation {'succeeded' if success else 'failed'} to {url}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error navigating to {url}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@browser_api.route('/extract', methods=['POST'])
def extract_data():
    """Extract data from the current page"""
    data = request.json
    selectors = data.get('selectors', {})
    session_id = data.get('session_id')
    
    if not session_id or session_id not in browser_sessions:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing session ID'
        }), 400
    
    try:
        browser = browser_sessions[session_id]
        
        # Extract data using selectors
        extracted_data = browser.extract_data(selectors)
        
        # Get screenshot
        screenshot = get_screenshot(browser)
        
        return jsonify({
            'success': True if extracted_data else False,
            'data': extracted_data,
            'screenshot': screenshot
        })
    except Exception as e:
        logger.error(f"Error extracting data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@browser_api.route('/click', methods=['POST'])
def click_element():
    """Click an element on the page"""
    data = request.json
    selector = data.get('selector')
    fallback_selector = data.get('fallback_selector')
    session_id = data.get('session_id')
    
    if not selector:
        return jsonify({
            'success': False,
            'error': 'Selector is required'
        }), 400
    
    if not session_id or session_id not in browser_sessions:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing session ID'
        }), 400
    
    try:
        browser = browser_sessions[session_id]
        
        # Click the element with the primary selector
        success = browser.click_element(selector)
        
        # If primary selector fails and a fallback is provided, try the fallback
        if not success and fallback_selector:
            logger.info(f"Primary selector '{selector}' failed, trying fallback selector: '{fallback_selector}'")
            success = browser.click_element(fallback_selector)
        
        # Get screenshot
        screenshot = get_screenshot(browser)
        
        return jsonify({
            'success': success,
            'screenshot': screenshot
        })
    except Exception as e:
        logger.error(f"Error clicking element {selector}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@browser_api.route('/fill', methods=['POST'])
def fill_form():
    """Fill a form on the page"""
    data = request.json
    form_data = data.get('form_data', {})
    session_id = data.get('session_id')
    
    if not form_data:
        return jsonify({
            'success': False,
            'error': 'Form data is required'
        }), 400
    
    if not session_id or session_id not in browser_sessions:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing session ID'
        }), 400
    
    try:
        browser = browser_sessions[session_id]
        
        # Fill the form
        success = browser.fill_form(form_data)
        
        # Get screenshot
        screenshot = get_screenshot(browser)
        
        return jsonify({
            'success': success,
            'screenshot': screenshot
        })
    except Exception as e:
        logger.error(f"Error filling form: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@browser_api.route('/screenshot', methods=['POST'])
def take_screenshot():
    """Take a screenshot of the current page"""
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in browser_sessions:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing session ID'
        }), 400
    
    try:
        browser = browser_sessions[session_id]
        
        # Get screenshot
        screenshot = get_screenshot(browser)
        
        return jsonify({
            'success': True if screenshot else False,
            'screenshot': screenshot
        })
    except Exception as e:
        logger.error(f"Error taking screenshot: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@browser_api.route('/close', methods=['POST'])
def close_browser():
    """Close the browser session"""
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in browser_sessions:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing session ID'
        }), 400
    
    try:
        browser = browser_sessions[session_id]
        
        # Close the browser
        browser.close()
        
        # Remove from sessions
        del browser_sessions[session_id]
        
        return jsonify({
            'success': True,
            'message': f'Browser session {session_id} closed'
        })
    except Exception as e:
        logger.error(f"Error closing browser: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
