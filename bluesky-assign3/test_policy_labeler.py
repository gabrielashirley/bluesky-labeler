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

def save_results_to_csv(results, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['post_index', 'text', 'label'])
        writer.writeheader()
        for index, text, label in results:
            writer.writerow({
                'post_index': index,
                'text': text,
                'label': label if label else "[]"
            })

if __name__ == "__main__":
    csv_path = "./bluesky-assign3/test-data/input-posts-panic.csv"
    posts = load_posts_from_csv(csv_path)
    results = run_labeler_on_posts(posts)
    save_results_to_csv(results, './bluesky-assign3/output-csv/labeled_output.csv')
    print_results(results)