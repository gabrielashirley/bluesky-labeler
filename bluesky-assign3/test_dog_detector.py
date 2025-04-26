"""
Test script for the dog image detector.
"""

import os
import argparse
import csv
import json
from atproto import Client
from dotenv import load_dotenv
from dog_detector import DogImageDetector
from image_extractor import ImageExtractor
from pylabel.label import post_from_url

def main():
    parser = argparse.ArgumentParser(description="Test dog image detection")
    parser.add_argument("csv_file", help="CSV file with test cases")
    parser.add_argument("--images-dir", default="labeler-inputs/dog-list-images",
                       help="Directory with reference dog images")
    args = parser.parse_args()
    
    # Initialize components
    detector = DogImageDetector(args.images_dir)
    extractor = ImageExtractor()
    
    # Set up authenticated client
    load_dotenv(override=True)
    USERNAME = os.getenv("USERNAME")
    PW = os.getenv("PW")
    
    if not USERNAME or not PW:
        print("ERROR: Missing USERNAME or PW environment variables")
        print("Please create a .env file with your Bluesky credentials")
        return
        
    client = Client()
    try:
        client.login(USERNAME, PW)
        print(f"Logged in as {USERNAME}")
    except Exception as e:
        print(f"Login failed: {e}")
        return
    
    # Process test cases
    correct = 0
    total = 0
    
    with open(args.csv_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        
        for row in reader:
            if len(row) >= 2:
                url = row[0]
                expected_str = row[1]
                
                # Parse expected JSON string to list
                try:
                    expected = json.loads(expected_str)
                except json.JSONDecodeError:
                    expected = [expected_str] if expected_str else []
                
                # Get post data
                try:
                    post_data = post_from_url(client, url)
                    if not post_data:
                        print(f"Could not fetch post: {url}")
                        continue
                except Exception as e:
                    print(f"Error fetching post {url}: {e}")
                    continue
                
                # Extract images and check for dogs
                image_urls = extractor.extract_image_urls(post_data)
                is_dog = False
                
                for img_url in image_urls:
                    if detector.is_dog_image_url(img_url):
                        is_dog = True
                        break
                
                # Compare with expected result
                actual = ["dog"] if is_dog else []
                is_correct = (actual == expected)
                
                # Print result
                mark = "✓" if is_correct else "✗"
                print(f"{mark} {url}")
                
                if is_correct:
                    correct += 1
                total += 1
    
    # Print summary
    if total > 0:
        print(f"\nResults: {correct}/{total} correct ({correct/total:.2%})")
    else:
        print("\nNo test cases processed")

if __name__ == "__main__":
    main()
