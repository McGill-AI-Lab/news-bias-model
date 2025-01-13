from datasets import load_dataset
from tqdm import tqdm
import os
import json

def save_to_jsonfile(row, output_file):
    """
    Saves article data to a JSON file where each publisher is a top-level key,
    and its value is a list of articles belonging to that publisher.
    """
    article_data = {
        "requested_url": row["requested_url"],
        "responded_url": row["responded_url"],
        "title": row["title"],
        "date": row["publishing_date"],
        "text": row['plain_text']
    }

    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        with open(output_file, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
        if not isinstance(existing_data, dict):
            existing_data = {}
    else:
        existing_data = {}

    publisher = row["publisher"]
    if publisher not in existing_data:
        existing_data[publisher] = []

    existing_data[publisher].append(article_data)

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

# Load the dataset in streaming mode
dataset = load_dataset("stanford-oval/ccnews", name="2017", streaming=True)

# Filter for English articles
english_articles = dataset["train"].filter(lambda x: x["language"] == "en")

# Initialize counters
output_file = "data/stanford_oval_ccnews/st_ccnews_2017.json"
total_size = 0
article_count = 0

# Process and save filtered articles
with tqdm(desc="Processing English articles", unit="rows", unit_scale=True, unit_divisor=1024) as pbar:
    for row in english_articles:
        # Save to JSON
        save_to_jsonfile(row, output_file)
        article_count += 1

        # Update progress
        row_size = len(json.dumps(row))  # Approximate row size in bytes
        total_size += row_size
        pbar.update(row_size / 1024)  # Convert bytes to KB

        # Optional: Print progress for every 100 articles
        if article_count % 100 == 0:
            print(f"{article_count} articles processed. Approx size: {total_size / (1024**2):.2f} MB")

print(f"\nTotal articles saved: {article_count}")
print(f"Approximate dataset size: {total_size / (1024**3):.2f} GB")
