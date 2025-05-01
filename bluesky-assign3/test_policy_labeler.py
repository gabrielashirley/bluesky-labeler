import csv
from policy_proposal_labeler import PanicLanguageLabeler

def load_posts_from_csv(file_path):
    posts = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            posts.append(row['text'])
    return posts

def run_labeler_on_posts(posts):
    labeler = PanicLanguageLabeler()
    results = []
    for i, text in enumerate(posts):
        label = labeler.moderate_post(text)
        results.append((i + 1, text, label))
    return results

def print_results(results):
    for index, text, label in results:
        print(f"Post {index}:\nText: {text}\nLabel: {label}\n")

if __name__ == "__main__":
    csv_path = "./bluesky-assign3/test-data/panic-test.csv"  # Make sure this file exists!
    posts = load_posts_from_csv(csv_path)
    results = run_labeler_on_posts(posts)
    print_results(results)