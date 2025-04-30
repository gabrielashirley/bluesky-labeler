"""Implementation of automated moderator"""

import os
import re
import urllib.parse
import pandas as pd
from typing import List
from atproto import Client

from dog_detector import DogImageDetector
from image_extractor import ImageExtractor
from pylabel.label import post_from_url

T_AND_S_LABEL = "t-and-s"
DOG_LABEL = "dog"
THRESH = 0.3

class AutomatedLabeler:
    """Automated labeler implementation"""

    def __init__(self, client: Client, input_dir):
        self.client = client
        self.input_dir = input_dir
        
        # Load T&S words and domains using pandas (Milestone 2)
        try:
            self.word_df = pd.read_csv(os.path.join(self.input_dir, "t-and-s-words.csv"))
            self.domain_df = pd.read_csv(os.path.join(self.input_dir, "t-and-s-domains.csv"))
        except Exception as e:
            print(f"[ERROR] Failed to load input CSVs from {self.input_dir}: {e}")
        
        # Load news domains (Milestone 3)
        try:
            self.news_df = pd.read_csv(os.path.join(self.input_dir, "news-domains.csv"))
        except Exception as e:
            self.news_df = None
            print(f"[INFO] No news-domains.csv found in {self.input_dir}: {e}")
        
        # Initialize dog detection (Milestone 4)
        self.dog_hashes = []
        dog_image_dir = os.path.join(self.input_dir, "dog-list-images")
        if os.path.exists(dog_image_dir):
            self.dog_detector = DogImageDetector(dog_image_dir)
        
        self.image_extractor = ImageExtractor()
    
    def _contains_ts_word(self, text: str) -> bool:
        """Check if text contains any Trust and Safety words (Milestone 2)"""
        if not text or not hasattr(self, 'word_df') or self.word_df.empty:
            return False
        
        text_lower = text.lower()
        for _, row in self.word_df.iterrows():
            word = str(row[0]).strip().lower()
            # Use word boundary to match whole words
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, text_lower):
                return True
        return False
    
    def _contains_ts_domain(self, text: str) -> bool:
        """Check if text contains any Trust and Safety domains (Milestone 3)"""
        if not text or not hasattr(self, 'domain_df') or self.domain_df.empty:
            return False
        
        text_lower = text.lower()
        for _, row in self.domain_df.iterrows():
            domain = str(row[0]).strip().lower()
            if domain in text_lower:
                return True
        return False
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text (Milestone 3)"""
        if not text:
            return []
        
        # Simple URL regex pattern
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        return re.findall(url_pattern, text)
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL (Milestone 3)"""
        try:
            parsed_url = urllib.parse.urlparse(url)
            # Get domain without 'www.' prefix
            domain = parsed_url.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return ""
    
    def _get_news_labels(self, text: str) -> List[str]:
        """Extract labels for news sources linked in the text (Milestone 3)"""
        if not text or not hasattr(self, 'news_df') or self.news_df is None or self.news_df.empty:
            return []
        
        # Extract URLs from text
        urls = self._extract_urls(text)
        if not urls:
            return []
        
        # Track which news sources have been found to avoid duplicates
        found_labels = set()
        
        # Check each URL for news domains
        for url in urls:
            domain = self._extract_domain(url)
            if not domain:
                continue
            
            # Check if this domain matches any of our news domains
            for _, row in self.news_df.iterrows():
                if len(row) >= 2:
                    news_domain = str(row[0]).strip().lower()
                    label = str(row[1]).strip()
                    
                    if domain == news_domain or domain.endswith(f".{news_domain}"):
                        found_labels.add(label)
                        break
        
        return list(found_labels)
   
    def moderate_post(self, url: str) -> List[str]:
        """
        Apply moderation to the post specified by the given url
        """
        # Get post data
        try:
            post_data = post_from_url(self.client, url)
            if not post_data:
                return []
                
            # Access the text content based on the actual structure
            post_record = post_data.value
            text = post_record.text if hasattr(post_record, 'text') else ""
            
        except Exception as e:
            print(f"Error getting post: {e}")
            return []
        
        labels = []
        
        # Check for dog images (Milestone 4)
        try:
            if hasattr(self, 'dog_detector'):
                image_urls = self.image_extractor.extract_image_urls(post_data)
                for img_url in image_urls:
                    if self.dog_detector.is_dog_image_url(img_url):
                        return [DOG_LABEL]  # Return immediately for dog images
        except Exception:
            pass
        
        # Check for T&S words and domains (Milestone 2)
        try:
            if self._contains_ts_word(text) or self._contains_ts_domain(text):
                labels.append(T_AND_S_LABEL)
        except Exception as e:
            print(f"Error checking T&S content: {e}")
        
        # Check for news sources (Milestone 3)
        try:
            news_labels = self._get_news_labels(text)
            labels.extend(news_labels)
        except Exception as e:
            print(f"Error checking news sources: {e}")
            
        return labels
