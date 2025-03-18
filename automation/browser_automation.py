"""
Browser automation module using Selenium.
This module handles web interactions like navigation, data extraction, and form interactions.
"""
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BrowserAutomation:
    """Class to handle browser automation tasks using Selenium."""
    
    def __init__(self, headless=True):
        """
        Initialize the browser automation with Selenium WebDriver.
        
        Args:
            headless (bool): Whether to run the browser in headless mode
        """
        self.headless = headless
        logger.info(f"Initializing browser automation (headless: {headless})")
        
        # Set up Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        
        # Initialize the WebDriver
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.driver.implicitly_wait(10)  # seconds
        
        # Initialize WebDriverWait with a timeout of 10 seconds
        self.wait = WebDriverWait(self.driver, 10)
    
    def navigate_to_url(self, url):
        """
        Navigate to a specific URL.
        
        Args:
            url (str): The URL to navigate to
            
        Returns:
            bool: Success status
        """
        try:
            logger.info(f"Navigating to URL: {url}")
            self.driver.get(url)
            # Wait for the page to load
            time.sleep(2)  # Basic wait for page load
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to URL {url}: {str(e)}")
            return False
    
    def extract_data(self, selectors):
        """
        Extract data from the current page using CSS selectors.
        
        Args:
            selectors (dict): Dictionary of name:selector pairs
            
        Returns:
            dict: Extracted data with names as keys
        """
        try:
            logger.info(f"Extracting data using selectors: {selectors}")
            
            # Get the page source and parse with BeautifulSoup for more robust extraction
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
            results = {}
            
            for name, selector in selectors.items():
                try:
                    # First try using Selenium
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if elements:
                        # If we found multiple elements, combine their text
                        results[name] = "\n".join([elem.text for elem in elements])
                    else:
                        # If Selenium couldn't find anything, try with BeautifulSoup
                        soup_elements = soup.select(selector)
                        if soup_elements:
                            results[name] = "\n".join([elem.get_text() for elem in soup_elements])
                        else:
                            results[name] = ""
                except Exception as selector_error:
                    logger.warning(f"Failed to extract data for selector {selector}: {str(selector_error)}")
                    results[name] = ""
            
            return results
        except Exception as e:
            logger.error(f"Failed to extract data: {str(e)}")
            return {}
    
    def fill_form(self, form_data):
        """
        Fill a form with the provided data.
        
        Args:
            form_data (dict): Dictionary of selector:value pairs
            
        Returns:
            bool: Success status
        """
        try:
            logger.info(f"Filling form with data: {form_data}")
            
            for selector, value in form_data.items():
                try:
                    # Wait for the element to be present and interactable
                    element = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    
                    # Clear existing value (if it's an input)
                    try:
                        element.clear()
                    except:
                        pass  # Some elements can't be cleared
                    
                    # Send the value
                    element.send_keys(value)
                    logger.info(f"Filled element {selector} with value {value}")
                except Exception as e:
                    logger.warning(f"Failed to fill element {selector}: {str(e)}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Failed to fill form: {str(e)}")
            return False
    
    def click_element(self, selector):
        """
        Click an element on the page.
        
        Args:
            selector (str): CSS selector for the element to click
            
        Returns:
            bool: Success status
        """
        try:
            logger.info(f"Clicking element with selector: {selector}")
            
            # Wait for the element to be clickable
            element = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            
            # Scroll the element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            
            # Wait briefly after scrolling
            time.sleep(0.5)
            
            # Click the element
            element.click()
            
            # Wait briefly after clicking
            time.sleep(0.5)
            
            return True
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {str(e)}")
            return False
    
    def close(self):
        """Close the browser."""
        logger.info("Closing browser")
        try:
            self.driver.quit()
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")

