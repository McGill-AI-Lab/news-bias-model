# from datasets import load_dataset
# from tqdm import tqdm
#
#
# import os
# import json
#
# def save_to_jsonfile(row, output_file):
#     """
#     Saves article data to a JSON file where each publisher is a top-level key,
#     and its value is a list of articles belonging to that publisher.
#     """
#
#     # Create the article data WITHOUT the publisher key
#     # because the publisher will be the top-level key.
#     article_data = {
#         "requested_url": row["requested_url"],
#         "responded_url": row["responded_url"],
#         "title": row["title"],
#         "date": row["publishing_date"],
#         "text": row['plain_text']
#     }
#
#     # Check if the file exists and has data, then load it.
#     # We expect the top-level structure to be a dict: { "PublisherName": [ {...}, {...} ], ... }
#     if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
#         with open(output_file, "r", encoding="utf-8") as file:
#             existing_data = json.load(file)
#
#         # If the existing data isn't a dictionary for some reason, reset it to an empty dict
#         if not isinstance(existing_data, dict):
#             existing_data = {}
#     else:
#         existing_data = {}
#
#     # Use the article's publisher as the key.
#     # If the publisher doesn't exist yet in existing_data, initialize an empty list.
#     publisher = row.publisher
#     if publisher not in existing_data:
#         existing_data[publisher] = []
#
#     # Append this article's data under the publisher key
#     existing_data[publisher].append(article_data)
#
#     # Save the updated structure back to the JSON file
#     with open(output_file, "w", encoding="utf-8") as file:
#         json.dump(existing_data, file, ensure_ascii=False, indent=4)
#
#     print(f"Article data appended under publisher '{publisher}' in {output_file}")
#     print(article_data)
#
#
# # Load the news articles **crawled** in the year 2016 (but not necessarily published in 2016), in streaming mode
# dataset = load_dataset("stanford-oval/ccnews", name="2017", streaming=False, num_proc=8) # `name` can be one of 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024
#
# # Print information about the dataset
# print(dataset)
#
#
# print("count the number of articles:")
# # Count the number of articles (in 2016)
# row_count = 0
# for _ in tqdm(dataset["train"], desc="Counting rows", unit=" rows", unit_scale=True, unit_divisor=1000):
#     row_count += 1
#
# # Print the number of rows
# print(f"\nTotal number of articles in 2016 dataset: {row_count}")
#
# i=0
#
# # Extract all English (en) articles
# for row in tqdm(dataset["train"], desc="Extracting articles", unit=" rows", unit_scale=True, unit_divisor=1000):
#     if row["language"] == "en":
#         save_to_jsonfile(row, "data/stanford_oval_ccnews/st_ccnews_2017.json")
#         i += 1
#         print(f"{i}th article saved to the folder")

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

# Load the dataset in streaming mode with a filter for English rows
dataset = load_dataset("stanford-oval/ccnews", name="2017", streaming=True)

# Filter for English articles
english_articles = dataset["train"].filter(lambda x: x["language"] == "en")

# Initialize counters
output_file = "data/stanford_oval_ccnews/st_ccnews_2017.json"
total_size = 0
article_count = 0

# Process and save filtered articles
with tqdm(desc="Processing English articles", unit=" rows", unit_scale=True, unit_divisor=1024) as pbar:
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
