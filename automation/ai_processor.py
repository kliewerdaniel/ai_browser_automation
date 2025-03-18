"""
AI processing module for data summarization and analysis.
This module handles text processing using NLP techniques and ML models if available.
"""
import logging
import json
import os
import re
import sys
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check for available ML/NLP libraries
HAVE_NLTK = importlib.util.find_spec("nltk") is not None
HAVE_SKLEARN = importlib.util.find_spec("sklearn") is not None
HAVE_TRANSFORMERS = importlib.util.find_spec("transformers") is not None
HAVE_TORCH = importlib.util.find_spec("torch") is not None

# Import libraries if available
if HAVE_NLTK:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    
    # Download NLTK data if not already present
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

if HAVE_SKLEARN:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.preprocessing import MultiLabelBinarizer
    import numpy as np

if HAVE_TRANSFORMERS and HAVE_TORCH:
    import torch
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

class AIProcessor:
    """Class to handle AI processing tasks for text analysis."""
    
    def __init__(self, model="sshleifer/distilbart-cnn-12-6"):
        """
        Initialize the AI processor.
        
        Args:
            model (str): The pre-trained model to use for summarization (if available)
        """
        self.model_name = model
        logger.info(f"Initializing AI processor (target model: {model})")
        
        self.summarizer = None
        self.tokenizer = None
        self.model = None
        
        # Initialize advanced NLP capabilities if libraries are available
        if HAVE_TRANSFORMERS and HAVE_TORCH:
            # Try to initialize the summarization pipeline
            try:
                self.summarizer = pipeline(
                    "summarization", 
                    model=model,
                    device=0 if torch.cuda.is_available() else -1  # Use GPU if available
                )
                logger.info("Summarization pipeline initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize summarization pipeline: {str(e)}")
                
                # Try to use a backup model
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
                    self.model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
                    logger.info("Backup summarization model loaded successfully")
                except Exception as backup_error:
                    logger.warning(f"Failed to initialize backup model: {str(backup_error)}")
        else:
            logger.info("Running without advanced NLP models (transformers/torch not available)")
        
        # Configure classification capabilities
        self.categories = [
            "technology", "business", "science", "health", 
            "politics", "entertainment", "sports", "education",
            "travel", "food", "fashion", "art"
        ]
        
        # Initialize classifier if sklearn is available
        if HAVE_SKLEARN:
            self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
            self.classifier = MultinomialNB()
            self.mlb = MultiLabelBinarizer()
            
            # Initialize with sample data
            self._init_classifier()
        else:
            logger.info("Running without ML classification (scikit-learn not available)")
    
    def _init_classifier(self):
        """Initialize the classifier with sample data."""
        try:
            if HAVE_SKLEARN:
                # Sample training data - in a real implementation, this would be more extensive
                sample_texts = [
                    "Apple released a new iPhone with advanced AI capabilities.",
                    "The stock market reached a new high today with tech companies leading.",
                    "Scientists discovered a new species of deep-sea creatures.",
                    "The new healthcare bill was passed by the senate yesterday.",
                    "The movie won several awards at the film festival.",
                    "The team won the championship after an intense match.",
                    "The university launched a new online learning platform.",
                    "Visit the beautiful beaches of Bali for your next vacation.",
                    "This recipe for chocolate cake is simple and delicious.",
                    "The fashion show featured sustainable clothing designs.",
                    "The art exhibition showcased works from local artists."
                ]
                
                sample_categories = [
                    ["technology"],
                    ["business"],
                    ["science"],
                    ["politics", "health"],
                    ["entertainment"],
                    ["sports"],
                    ["education", "technology"],
                    ["travel"],
                    ["food"],
                    ["fashion"],
                    ["art"]
                ]
                
                # Transform the data and fit the classifier
                X = self.vectorizer.fit_transform(sample_texts)
                y = self.mlb.fit_transform(sample_categories)
                self.classifier.fit(X, y)
                logger.info("Classifier initialized with sample data")
            else:
                logger.debug("Classifier initialization skipped (sklearn not available)")
        except Exception as e:
            logger.error(f"Failed to initialize classifier: {str(e)}")
    
    def _extract_sentences(self, text, max_sentences=5):
        """
        Extract important sentences from text as a basic summarization method.
        
        Args:
            text (str): Text to summarize
            max_sentences (int): Maximum number of sentences to include
            
        Returns:
            str: Extracted summary
        """
        # Get sentences from text
        if not HAVE_NLTK:
            # If NLTK is not available, split by periods as a basic approach
            sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
        else:
            # Use NLTK to properly tokenize into sentences
            try:
                sentences = sent_tokenize(text)
            except Exception as e:
                logger.warning(f"Error in sentence tokenization: {str(e)}")
                sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
        
        # Return empty string if no sentences
        if not sentences:
            return ""
        
        # If there are only a few sentences, return them all
        if len(sentences) <= max_sentences:
            return " ".join(sentences)
        
        try:
            if HAVE_NLTK:
                # Simple scoring based on sentence position and length
                scores = []
                for i, sentence in enumerate(sentences):
                    # Position score - first and last sentences are important
                    position_score = 1.0 if i < 2 or i >= len(sentences) - 2 else 0.0
                    
                    # Length score - avoid very short sentences
                    length_score = min(1.0, len(word_tokenize(sentence)) / 20.0)
                    
                    # Calculate total score
                    total_score = position_score + length_score
                    scores.append((i, total_score))
                
                # Sort sentences by score and take the top ones
                sorted_sentences = sorted(scores, key=lambda x: x[1], reverse=True)
                top_indices = sorted([idx for idx, _ in sorted_sentences[:max_sentences]])
                
                # Return the top sentences in their original order
                return " ".join([sentences[i] for i in top_indices])
            else:
                # Simple fallback for when NLTK is not available - take first few sentences
                return " ".join(sentences[:max_sentences])
        except Exception as e:
            logger.warning(f"Error in extractive summarization: {str(e)}")
            # Ultra fallback - just take first few sentences
            return " ".join(sentences[:max_sentences])
    
    def summarize_text(self, text, max_length=200):
        """
        Summarize the given text using pre-trained models.
        
        Args:
            text (str): The text to summarize
            max_length (int): Maximum length of summary in words
            
        Returns:
            str: Summarized text
        """
        try:
            logger.info(f"Summarizing text (length: {len(text)})")
            
            # Clean up text - remove extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # If text is too short, return it as is
            if len(text.split()) <= max_length:
                return text
            
            # Option 1: Try using the Hugging Face pipeline if available
            if HAVE_TRANSFORMERS and HAVE_TORCH and self.summarizer:
                try:
                    # Split into chunks if text is too long
                    chunk_size = 1000  # Characters
                    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
                    
                    summaries = []
                    for chunk in chunks:
                        if len(chunk.split()) > 10:  # Only summarize if chunk has enough words
                            summary = self.summarizer(
                                chunk, 
                                max_length=min(max_length, 150),  # Limit each chunk's summary
                                min_length=10,
                                do_sample=False
                            )[0]['summary_text']
                            summaries.append(summary)
                    
                    # Combine summaries
                    full_summary = " ".join(summaries)
                    
                    # Ensure we don't exceed max_length words
                    words = full_summary.split()
                    if len(words) > max_length:
                        full_summary = " ".join(words[:max_length])
                    
                    return full_summary
                except Exception as pipeline_error:
                    logger.warning(f"Pipeline summarization failed: {str(pipeline_error)}")
            
            # Option 2: Backup method using the model directly if available
            if HAVE_TRANSFORMERS and HAVE_TORCH and hasattr(self, 'model') and hasattr(self, 'tokenizer'):
                try:
                    inputs = self.tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
                    summary_ids = self.model.generate(
                        inputs["input_ids"], 
                        max_length=150, 
                        min_length=40, 
                        length_penalty=2.0, 
                        num_beams=4,
                        early_stopping=True
                    )
                    return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                except Exception as model_error:
                    logger.warning(f"Model-based summarization failed: {str(model_error)}")
            
            # Option 3: Fallback to simple extractive summarization for all cases
            logger.info("Using extractive summarization")
            return self._extract_sentences(text, max_sentences=5)
            
        except Exception as e:
            logger.error(f"Failed to summarize text: {str(e)}")
            return "Error generating summary."
    
    def extract_key_information(self, text, info_type):
        """
        Extract specific types of information from text.
        
        Args:
            text (str): The text to analyze
            info_type (str): Type of information to extract (e.g., 'dates', 'names', 'prices')
            
        Returns:
            list: Extracted information items
        """
        try:
            logger.info(f"Extracting {info_type} from text")
            
            # Clean up text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Extract different types of information based on regex patterns
            if info_type == "dates" or info_type == "date":
                # Match common date formats
                date_patterns = [
                    r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # DD/MM/YYYY, MM/DD/YYYY
                    r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',     # YYYY/MM/DD
                    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[.]{0,1}\s+\d{1,2},\s+\d{4}\b',  # Month DD, YYYY
                    r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[.]{0,1}\s+\d{4}\b',  # DD Month YYYY
                ]
                
                results = []
                for pattern in date_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    results.extend(matches)
                
                return results
                
            elif info_type == "names" or info_type == "person":
                # Simple pattern for names (Mr./Mrs./Ms. followed by capitalized words)
                # Note: This is a simplistic approach. NER (Named Entity Recognition) would be better
                name_patterns = [
                    r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Titles with names
                    r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'  # Simple FirstName LastName
                ]
                
                results = []
                for pattern in name_patterns:
                    matches = re.findall(pattern, text)
                    results.extend(matches)
                
                return results
                
            elif info_type == "prices" or info_type == "price":
                # Match common price formats
                price_patterns = [
                    r'\$\d+(?:,\d{3})*(?:\.\d{2})?',  # $X,XXX.XX
                    r'\d+(?:,\d{3})*(?:\.\d{2})?\s+(?:dollars|USD)',  # X,XXX.XX dollars/USD
                    r'(?:EUR|€)\s*\d+(?:,\d{3})*(?:\.\d{2})?',  # EUR X,XXX.XX or € X,XXX.XX
                ]
                
                results = []
                for pattern in price_patterns:
                    matches = re.findall(pattern, text)
                    results.extend(matches)
                
                return results
                
            elif info_type == "emails" or info_type == "email":
                # Match email addresses
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                return re.findall(email_pattern, text)
                
            elif info_type == "urls" or info_type == "url":
                # Match URLs
                url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*(?:\?[\w=&]*)?'
                return re.findall(url_pattern, text)
                
            else:
                # For other types, extract key phrases using NLP techniques if available
                if HAVE_NLTK:
                    sentences = sent_tokenize(text)
                    words = [word_tokenize(sentence.lower()) for sentence in sentences]
                    
                    # Filter sentences that contain the info_type keyword
                    relevant_sentences = [
                        sentence for sentence, words in zip(sentences, words) 
                        if info_type.lower() in words or info_type.lower()[:-1] in words  # Handle plurals
                    ]
                else:
                    # Simple fallback without NLTK
                    sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
                    # Basic search for sentences containing the keyword
                    relevant_sentences = [
                        sentence for sentence in sentences
                        if info_type.lower() in sentence.lower() or 
                        (len(info_type) > 3 and info_type.lower()[:-1] in sentence.lower())  # Handle plurals
                    ]
                
                return relevant_sentences if relevant_sentences else [f"No information about {info_type} found"]
                
        except Exception as e:
            logger.error(f"Failed to extract {info_type}: {str(e)}")
            return []
    
    def categorize_content(self, text):
        """
        Categorize the content of the text.
        
        Args:
            text (str): The text to categorize
            
        Returns:
            dict: Category information with confidence scores
        """
        try:
            logger.info("Categorizing text content")
            
            # Clean and prepare the text
            cleaned_text = re.sub(r'\s+', ' ', text).strip()
            
            # Option 1: Use ML-based classification if scikit-learn is available
            if HAVE_SKLEARN and hasattr(self, 'vectorizer') and hasattr(self, 'classifier'):
                try:
                    # Transform the input text
                    X = self.vectorizer.transform([cleaned_text])
                    
                    # Get prediction probabilities
                    y_proba = self.classifier.predict_proba(X)
                    
                    # Convert probabilities to category scores
                    categories = {}
                    for i, category in enumerate(self.mlb.classes_):
                        categories[category] = float(y_proba[0][i])
                    
                    # Sort categories by score
                    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
                    
                    # Get primary category (highest score)
                    primary_category = sorted_categories[0][0] if sorted_categories else "unknown"
                    
                    return {
                        "categories": dict(sorted_categories),
                        "primary_category": primary_category
                    }
                except Exception as sklearn_error:
                    logger.warning(f"ML classification failed: {str(sklearn_error)}")
                    # Fall back to keyword-based approach
            
            # Option 2: Fallback to keyword-based categorization
                # Fallback to keyword-based categorization
                keyword_categories = {
                    "technology": ["computer", "software", "hardware", "tech", "digital", "code", "programming", "ai", "artificial intelligence"],
                    "business": ["company", "market", "stock", "finance", "investment", "profit", "loss", "business", "economy"],
                    "science": ["research", "scientist", "study", "experiment", "discovery", "journal", "physics", "chemistry", "biology"],
                    "health": ["medical", "health", "doctor", "patient", "hospital", "disease", "treatment", "symptom", "medicine"],
                    "politics": ["government", "president", "election", "vote", "policy", "political", "democrat", "republican", "law"],
                    "entertainment": ["movie", "film", "actor", "actress", "director", "music", "song", "celebrity", "show", "tv"],
                    "sports": ["game", "team", "player", "coach", "score", "win", "lose", "championship", "tournament", "sports"],
                }
                
                # Count keyword occurrences for each category
                scores = {category: 0 for category in keyword_categories}
                
                lower_text = cleaned_text.lower()
                for category, keywords in keyword_categories.items():
                    for keyword in keywords:
                        scores[category] += lower_text.count(f" {keyword} ")
                
                # Normalize scores
                total_score = sum(scores.values())
                if total_score > 0:
                    normalized_scores = {
                        category: min(score / total_score * 3, 1.0) for category, score in scores.items()
                    }
                else:
                    normalized_scores = {category: 0.1 for category in scores}
                
                # Determine primary category
                primary_category = max(normalized_scores.items(), key=lambda x: x[1])[0]
                
                return {
                    "categories": normalized_scores,
                    "primary_category": primary_category
                }
                
        except Exception as e:
            logger.error(f"Failed to categorize content: {str(e)}")
            return {"categories": {}, "primary_category": "unknown"}
