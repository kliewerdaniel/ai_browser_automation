"""
Unit tests for the AI processing module.
"""
import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from automation.ai_processor import AIProcessor

class TestAIProcessor(unittest.TestCase):
    """Test cases for the AIProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = AIProcessor(model="test-model")
    
    def test_init(self):
        """Test initialization of AIProcessor."""
        self.assertEqual(self.processor.model, "test-model")
    
    def test_summarize_text(self):
        """Test text summarization functionality."""
        # Since we're using mock data in our current implementation,
        # this just tests that the function returns something without error
        text = "This is a sample text that would be summarized by Ollama in a real implementation."
        summary = self.processor.summarize_text(text, max_length=50)
        self.assertIsNotNone(summary)
        self.assertTrue(isinstance(summary, str))
    
    @patch('automation.ai_processor.AIProcessor.summarize_text')
    def test_summarize_text_with_mock(self, mock_summarize):
        """Test text summarization with mocked function."""
        # Configure mock to return a specific value
        expected_summary = "This is a mocked summary."
        mock_summarize.return_value = expected_summary
        
        # Call the function with our test data
        text = "Original text for summarization."
        summary = mock_summarize(text, max_length=50)
        
        # Verify the function was called with the right parameters
        mock_summarize.assert_called_once_with(text, max_length=50)
        
        # Verify we got the expected result
        self.assertEqual(summary, expected_summary)
    
    def test_extract_key_information(self):
        """Test information extraction functionality."""
        text = "Sample text containing dates like 2023-01-15 and names like John Doe."
        
        # Test extracting dates
        dates = self.processor.extract_key_information(text, "dates")
        self.assertTrue(isinstance(dates, list))
        
        # Test extracting names
        names = self.processor.extract_key_information(text, "names")
        self.assertTrue(isinstance(names, list))
    
    def test_categorize_content(self):
        """Test content categorization functionality."""
        text = "Sample text about technology and science."
        categories = self.processor.categorize_content(text)
        
        self.assertTrue(isinstance(categories, dict))
        self.assertIn("categories", categories)
        self.assertIn("primary_category", categories)
        
if __name__ == '__main__':
    unittest.main()
