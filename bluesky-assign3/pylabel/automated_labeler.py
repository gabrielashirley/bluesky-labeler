"""Implementation of automated moderator"""

import os
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
        self.dog_detector = DogImageDetector(os.path.join(input_dir, "dog-list-images"))
        self.image_extractor = ImageExtractor()
        # Load T&S words and domains
        self.ts_words = self._load_ts_words(os.path.join(input_dir, "t-and-s-words.csv"))
        self.ts_domains = self._load_ts_domains(os.path.join(input_dir, "t-and-s-domains.csv"))

    def _load_ts_words(self, file_path: str) -> List[str]:
        """Load Trust and Safety words from CSV file"""
        words = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if row and row[0].strip():  # Skip empty rows
                        words.append(row[0].strip().lower())
        except Exception as e:
            print(f"Error loading T&S words: {e}")
        return words
    
    def _load_ts_domains(self, file_path: str) -> List[str]:
        """Load Trust and Safety domains from CSV file"""
        domains = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if row and row[0].strip():  # Skip empty rows
                        domains.append(row[0].strip().lower())
        except Exception as e:
            print(f"Error loading T&S domains: {e}")
        return domains
    
    def _contains_ts_word(self, text: str) -> bool:
        """Check if text contains any Trust and Safety words"""
        if not text or not self.ts_words:
            return False
        
        text_lower = text.lower()
        for word in self.ts_words:
            # Use word boundary to match whole words
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, text_lower):
                return True
        return False
    
    def _contains_ts_domain(self, text: str) -> bool:
        """Check if text contains any Trust and Safety domains"""
        if not text or not self.ts_domains:
            return False
        
        text_lower = text.lower()
        for domain in self.ts_domains:
            if domain in text_lower:
                return True
        return False
    
    def moderate_post(self, url: str) -> List[str]:
        """
        Apply moderation to the post specified by the given url
        """
        # Get post data
        try:
            post = post_from_url(self.client, url)
            if not post:
                return []
        except Exception:
            return []
        
        # Check for dog images first (Milestone 4)
        try:
            image_urls = self.image_extractor.extract_image_urls(post)
            for img_url in image_urls:
                if self.dog_detector.is_dog_image_url(img_url):
                    return [DOG_LABEL]
        except Exception:
            pass
        
        # Check for T&S words and domains
        try:
            # Extract text content from post
            text = post.get('text', '')
            
            # Check if post contains any T&S words or domains
            if self._contains_ts_word(text) or self._contains_ts_domain(text):
                return [T_AND_S_LABEL]
        except Exception as e:
            print(f"Error checking T&S content: {e}")
            
        # No labels to apply
        return []
   
    