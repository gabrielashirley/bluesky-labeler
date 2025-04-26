"""
Bluesky Image Extractor Module

This module provides functionality to extract image URLs from Bluesky posts.
"""

from typing import List, Dict, Any

class ImageExtractor:
    """
    A class for extracting image URLs from Bluesky posts.
    """
    
    @staticmethod
    def extract_image_urls(post_data: Dict[str, Any]) -> List[str]:
        """
        Extract image URLs from a Bluesky post.
        
        Args:
            post_data: Dictionary containing post data
            
        Returns:
            List of image URLs found in the post
        """
        if not post_data:
            return []
        
        image_urls = []
        
        try:
            # Handle response from client.get_post()
            if hasattr(post_data, 'value') and post_data.value:
                # Get the actual post data from the response
                post_value = post_data.value
                
                # Handle embed in post value
                if hasattr(post_value, 'embed') and post_value.embed:
                    embed = post_value.embed
                    
                    # Check if embed has images
                    if hasattr(embed, 'images') and embed.images:
                        for img in embed.images:
                            # For each image, get the blob reference
                            if hasattr(img, 'image') and img.image and hasattr(img.image, 'ref'):
                                ref = img.image.ref
                                if hasattr(ref, 'link'):
                                    # Construct URL from the reference
                                    link = ref.link
                                    url = f"https://bsky.social/xrpc/com.atproto.sync.getBlob?did=did:plc:swmumnkmw5osopckigoal7ox&cid={link}"
                                    image_urls.append(url)
            
            # Try extracting from raw data if no images found
            if not image_urls and hasattr(post_data, 'value') and hasattr(post_data.value, 'to_dict'):
                raw_data = post_data.value.to_dict()
                
                # Look for image references in the raw data
                if 'embed' in raw_data and 'images' in raw_data['embed']:
                    for img in raw_data['embed']['images']:
                        if 'image' in img and 'ref' in img['image']:
                            link = img['image']['ref'].get('$link')
                            if link:
                                url = f"https://bsky.social/xrpc/com.atproto.sync.getBlob?did=did:plc:swmumnkmw5osopckigoal7ox&cid={link}"
                                image_urls.append(url)
                    
        except Exception:
            pass
        
        return image_urls
