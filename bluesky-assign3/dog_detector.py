"""
Dog Image Detector Module

This module provides functionality to detect dog images using perceptual hashing.
It compares input images against a database of known dog images and determines
if they match within a specified threshold.
"""

import os
from typing import List, Optional
import requests
from io import BytesIO
from PIL import Image
from perception import hashers

# Default threshold
THRESH = 0.3

class DogImageDetector:
    """
    A class for detecting dog images using perceptual hashing.
    """
    
    def __init__(self, dog_images_dir: str, hash_size: int = 16, threshold: float = THRESH):
        """
        Initialize the dog image detector.
        
        Args:
            dog_images_dir: Directory containing reference dog images
            hash_size: Size of the perceptual hash (default: 16)
            threshold: Maximum normalized Hamming distance for a match (default: THRESH)
        """
        self.hash_size = hash_size
        self.threshold = threshold
        
        # Initialize the PHash hasher from Perception library
        self.hasher = hashers.PHash(hash_size=self.hash_size)
        
        # Build the database of dog image hashes
        self.dog_hashes = self._build_hash_database(dog_images_dir)

    def _build_hash_database(self, images_dir: str) -> List[str]:
        """
        Build a database of perceptual hashes from reference dog images.
        
        Args:
            images_dir: Directory containing reference dog images
            
        Returns:
            List of perceptual hashes (strings) for the reference images
        """
        hashes = []
        
        # Validate directory existence
        if not os.path.isdir(images_dir):
            raise ValueError(f"Directory not found: {images_dir}")
        
        # Process each image in the directory
        for filename in os.listdir(images_dir):
            try:
                # Open and process the image
                img_path = os.path.join(images_dir, filename)
                img = Image.open(img_path)
                
                # Compute and store the hash
                img_hash = self.hasher.compute(img)
                hashes.append(img_hash)
                
            except Exception:
                # Skip invalid images
                pass
        
        return hashes
    
    def download_image(self, url: str) -> Optional[Image.Image]:
        """
        Download an image from a URL.
        """
        try:
            # Set a reasonable timeout and headers to mimic a browser
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, stream=True, timeout=10, headers=headers)
            
            # Check if the request was successful
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
            return None
                
        except Exception:
            return None
    
    def compute_image_hash(self, image: Image.Image) -> Optional[str]:
        """
        Compute the perceptual hash of an image.
        """
        if image is None:
            return None
            
        try:
            return self.hasher.compute(image)
        except Exception:
            return None
    
    def calculate_hash_distance(self, hash1: str, hash2: str) -> float:
        """
        Calculate the normalized Hamming distance between two perceptual hashes.
        """
        return self.hasher.compute_distance(hash1, hash2)
    
    def is_dog_image(self, image: Image.Image) -> bool:
        """
        Check if an image matches any of the reference dog images.
        """
        if image is None:
            return False
        
        # Compute hash for the input image
        image_hash = self.compute_image_hash(image)
        if not image_hash:
            return False
        
        # Check against each dog hash
        for dog_hash in self.dog_hashes:
            distance = self.calculate_hash_distance(image_hash, dog_hash)
            
            # If distance is below threshold, it's a match
            if distance <= self.threshold:
                return True
        
        return False
    
    def is_dog_image_url(self, url: str) -> bool:
        """
        Check if an image at a URL matches any of the reference dog images.
        """
        image = self.download_image(url)
        return self.is_dog_image(image)
