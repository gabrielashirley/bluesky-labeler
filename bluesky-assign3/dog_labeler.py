"""
Dog Labeler Integration Module

This module integrates the dog image detector and image extractor
with the Bluesky labeler framework to label posts containing dog images.
"""

from typing import Optional, Dict, Any
from atproto import Client
from dog_detector import DogImageDetector
from image_extractor import ImageExtractor
from pylabel.label import post_from_url

class DogLabeler:
    """
    A class for labeling Bluesky posts that contain dog images.
    
    This labeler uses perceptual hashing to detect dog images in Bluesky posts
    and applies the "dog" label when a match is found.
    """
    
    def __init__(self, dog_images_dir: str, client: Client = None):
        """
        Initialize the dog labeler.
        
        Args:
            dog_images_dir: Directory containing reference dog images
            client: Client to use for API requests (optional)
        """
        # Initialize the dog image detector
        self.detector = DogImageDetector(dog_images_dir)
        
        # Initialize the image extractor
        self.extractor = ImageExtractor()
        
        # Store the client
        self.client = client or Client()
        
        print(f"Dog labeler initialized with images from {dog_images_dir}")
    
    def contains_dog_image(self, post_data: Dict[str, Any]) -> bool:
        """
        Check if a post contains a dog image.
        
        Args:
            post_data: Dictionary containing post data
            
        Returns:
            True if the post contains a dog image, False otherwise
        """
        # Extract image URLs from the post
        image_urls = self.extractor.extract_image_urls(post_data)
        
        # Check each image for dog matches
        for url in image_urls:
            if self.detector.is_dog_image_url(url):
                return True
        
        return False
    
    def moderate_post(self, url: str) -> Optional[str]:
        """
        Moderate a post and return a label if it contains a dog image.
        
        Args:
            url: URL of the post to moderate
            
        Returns:
            "dog" if the post contains a dog image, None otherwise
        """
        # Retrieve post data
        post_data = post_from_url(self.client, url)
        if not post_data:
            print(f"Failed to retrieve post data from URL: {url}")
            return None
        
        # Check if the post contains a dog image
        if self.contains_dog_image(post_data):
            return "dog"
        
        return None
