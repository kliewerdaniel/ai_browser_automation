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
        # Use a patch to avoid loading actual models during tests
        with patch('transformers.pipeline'), \
             patch('transformers.AutoTokenizer.from_pretrained'), \
             patch('transformers.AutoModelForSeq2SeqLM.from_pretrained'), \
             patch('nltk.download'):
            self.processor = AIProcessor(model="test-model")
            # Mock the summarizer attribute
            self.processor.summarizer = None
    
    def test_init(self):
        """Test initialization of AIProcessor."""
        self.assertEqual(self.processor.model_name, "test-model")
        self.assertIsInstance(self.processor.categories, list)
    
    @patch('automation.ai_processor.AIProcessor._extract_sentences')
    def test_summarize_text(self, mock_extract):
        """Test text summarization functionality using the fallback method."""
        # Configure mock to return a specific value
        mock_extract.return_value = "This is a test summary."
        
        # Test with short text (should return the text as is)
        short_text = "This is a short text."
        summary = self.processor.summarize_text(short_text, max_length=50)
        self.assertEqual(summary, short_text)
        
        # Test with longer text (should use the fallback method)
        long_text = "This is a longer text that exceeds the max length. " * 10
        summary = self.processor.summarize_text(long_text, max_length=50)
        self.assertEqual(summary, "This is a test summary.")
        mock_extract.assert_called_once()
    
    def test_extract_key_information_dates(self):
        """Test date extraction functionality."""
        text = "Important dates: 01/15/2023, 2023-01-15, January 15, 2023, and 15 Jan 2023."
        dates = self.processor.extract_key_information(text, "dates")
        self.assertTrue(isinstance(dates, list))
        self.assertGreater(len(dates), 0)
        # At least one of the date formats should be detected
        self.assertTrue(any("01/15/2023" in date or "2023-01-15" in date or "January 15, 2023" in date for date in dates))
    
    def test_extract_key_information_names(self):
        """Test name extraction functionality."""
        text = "Mr. John Smith and Dr. Jane Doe are attending the conference with Robert Johnson."
        names = self.processor.extract_key_information(text, "names")
        self.assertTrue(isinstance(names, list))
        self.assertGreater(len(names), 0)
        # Check if at least one name was detected
        self.assertTrue(any("John Smith" in name or "Jane Doe" in name or "Robert Johnson" in name for name in names))
    
    def test_extract_key_information_prices(self):
        """Test price extraction functionality."""
        text = "The product costs $19.99 and the premium version is $299.50. In Europe it costs €149.99."
        prices = self.processor.extract_key_information(text, "prices")
        self.assertTrue(isinstance(prices, list))
        self.assertGreater(len(prices), 0)
        # Check if at least one price was detected
        self.assertTrue(any("$19.99" in price or "$299.50" in price or "€149.99" in price for price in prices))
    
    def test_categorize_content(self):
        """Test content categorization functionality."""
        # Test technology text
        tech_text = "The new computer software utilizes artificial intelligence to improve programming efficiency."
        tech_categories = self.processor.categorize_content(tech_text)
        self.assertTrue(isinstance(tech_categories, dict))
        self.assertIn("categories", tech_categories)
        self.assertIn("primary_category", tech_categories)
        
        # Test multiple categories text
        mixed_text = "The healthcare company's stock rose after they announced a new medical research breakthrough."
        mixed_categories = self.processor.categorize_content(mixed_text)
        self.assertTrue(isinstance(mixed_categories, dict))
        self.assertIn("categories", mixed_categories)
        self.assertGreater(len(mixed_categories["categories"]), 0)
    
    def test_extract_sentences(self):
        """Test the sentence extraction fallback summarization method."""
        # Test with few sentences (should return all)
        short_text = "This is sentence one. This is sentence two."
        summary = self.processor._extract_sentences(short_text, max_sentences=5)
        self.assertEqual(summary, short_text)
        
        # Test with many sentences (should return subset)
        long_text = " ".join([f"This is sentence {i}." for i in range(1, 11)])
        summary = self.processor._extract_sentences(long_text, max_sentences=3)
        self.assertLess(len(summary.split(".")), 11)  # Should have fewer sentences than original
        
if __name__ == '__main__':
    unittest.main()
