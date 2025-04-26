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
            
        # Other labeling logic here
        return []