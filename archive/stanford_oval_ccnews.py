# from datasets import load_dataset
# from tqdm import tqdm
# import os
# import json
#
# def save_to_jsonfile(row, output_file):
#     """
#     Saves article data to a JSON file where each publisher is a top-level key,
#     and its value is a list of articles belonging to that publisher.
#     """
#     article_data = {
#         "requested_url": row["requested_url"],
#         "responded_url": row["responded_url"],
#         "title": row["title"],
#         "date": row["published_date"],
#         "text": row['plain_text']
#     }
#
#     if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
#         with open(output_file, "r", encoding="utf-8") as file:
#             existing_data = json.load(file)
#         if not isinstance(existing_data, dict):
#             existing_data = {}
#     else:
#         existing_data = {}
#
#     publisher = row["publisher"]
#     if publisher not in existing_data:
#         existing_data[publisher] = []
#
#     existing_data[publisher].append(article_data)
#
#     with open(output_file, "w", encoding="utf-8") as file:
#         json.dump(existing_data, file, ensure_ascii=False, indent=4)
#
#     print(f"Article data appended under publisher '{publisher}' in {output_file}")
#     print(article_data)
#
# # Load the dataset
# dataset = load_dataset(r"stanford-oval/ccnews", name="2016", streaming=True)
#
# print("Extracting articles:")
# # Use tqdm without a total to skip pre-counting rows
# i = 0
# for row in tqdm(dataset["train"], desc="Processing articles", unit="article"):
#     if row["language"] == "en":
#         save_to_jsonfile(row, "data/stanford_oval_ccnews/st_ccnews_2016.json")
#         i += 1
#         print(f"{i}th article saved to the folder")

import os
import json
import time
import logging
from datasets import load_dataset
from tqdm import tqdm

# Set up a logger to capture file access issues
logging.basicConfig(filename="file_access.log", level=logging.ERROR)

def save_to_jsonfile(row, output_file, retries=5, delay=0.5):
    """
    Saves article data to a JSON file where each publisher is a top-level key,
    and its value is a list of articles belonging to that publisher.
    Retries file operations a few times to avoid transient file lock issues.
    """
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Prepare the article data for JSON
    article_data = {
        "requested_url": row["requested_url"],
        "responded_url": row["responded_url"],
        "title": row["title"],
        "date": row["published_date"],
        "text": row["plain_text"],
    }

    # Attempt to open/write JSON with retries
    for attempt in range(retries):
        try:
            # If file exists and is non-empty, load existing JSON data
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                with open(output_file, "r", encoding="utf-8") as file:
                    existing_data = json.load(file)
                # Make sure the loaded data is a dictionary
                if not isinstance(existing_data, dict):
                    existing_data = {}
            else:
                existing_data = {}

            # Append the new article data under the given publisher
            publisher = row["publisher"]
            if publisher not in existing_data:
                existing_data[publisher] = []
            existing_data[publisher].append(article_data)

            # Write the updated data back to the file
            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(existing_data, file, ensure_ascii=False, indent=4)

            # Print debug info and break out of retry loop if successful
            print(f"Article data appended under publisher '{publisher}' in {output_file}")
            print(article_data)
            break

        except OSError as e:
            # This catches file-related issues, including file locks
            logging.error(f"Failed to save file {output_file} on attempt {attempt+1}: {e}")
            # If we still have retries left, wait a bit and retry
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                # Raise the error if out of retries
                raise


# Load the dataset (streaming = True means we don’t get a length upfront)
dataset = load_dataset("stanford-oval/ccnews", name="2016", streaming=True)

print("Extracting articles:")
output_path = os.path.join("../src/data", "stanford_oval_ccnews", "st_ccnews_2016.json")
i = 0

for row in tqdm(dataset["train"], desc="Processing articles", unit="article"):
    # Only process English articles
    if row["language"] == "en":
        save_to_jsonfile(row, output_path)
        i += 1
        print(f"{i}th article saved to the folder")
