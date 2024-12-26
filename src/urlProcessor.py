from newspaper import Article # Newspaper3K, NOT 4k
import json
from tqdm import tqdm
from multiprocessing import Pool
import time
# import unidecode

def getData(path):
    with open(path, 'r') as f:
        url_dict = json.load(f)

    return url_dict

def processArticle(url):
    try:
        paper = Article(url) # Makes a new Article instance
        paper.download() # Gets the HTML content
        paper.parse() # Makes a new Article instance
    except Exception as e:
        # print(f"Error processing {url}: {e}")
        return None  # Return None if an error occurs

    title = paper.title
    authors = paper.authors
    date = paper.publish_date
    text = paper.text

    newspaper_data = {
        "url": url,
        "title": cleanText(title),
        "authors": authors,
        "date": str(date),
        "text": cleanText(text)
    }

    return newspaper_data


def cleanText(text):
    clean_text = text.encode("ascii", "ignore").decode() # Gets rid of chars that arent ASCII ex. accented chars
    clean_text = clean_text.replace("\n", "").replace("\u2019", "'") # Removes annoying escape sequences
    # clean_text = unidecode(clean_text) # Makes it plain text
    return clean_text

def extractData(url_list):
    newspaper_source_data = []
    # pool = Pool(processes=10)
    batches = batchUrls(url_list, 1000)
    error_list = []

    for batch_num, batch in enumerate(batches):
        time.sleep(5)
        with tqdm(total=len(batch), desc=f"Extracting Article Data (batch {batch_num + 1})") as pbar:
            with Pool(processes=4) as pool:
                for url in batch:
                    pool.apply_async(
                        processArticle,  # process article asynchronously
                        args=(url,),  # args expects a tuple, so we give it a tuple with one item
                        callback=lambda single_newspaper_data: appendData(newspaper_source_data, single_newspaper_data, pbar, error_list, url) # appends the result after processArticle has run, passes data by reference, so we can update it                    )
                    )

                # print("DONE, CLOSING")
                pool.close()
                pool.join()

    # Wait for all processes to finish
    return newspaper_source_data, error_list

def batchUrls(urls, batch_size):
    batches = []
    start_num = 0

    while start_num < len(urls):
        batch = urls[start_num:start_num + batch_size]
        batches.append(batch)
        start_num += batch_size  # Move to the next batch

    print(f"Made {len(batches)} batches of {batch_size} urls each")

    return batches

def appendData(data, single_newspaper_data, pbar, error_list, url):
    pbar.update(1)
    if single_newspaper_data is not None:
        data.append(single_newspaper_data)
    else:
        error_list.append(url)

def main(url_dict):
    data = {}
    keys = url_dict.keys()
    error_data = {}
    for key in keys:
        print(f"Now extracting the {key} urls...")
        url_list = url_dict.get(key, [])
        extracted_data, error_list = extractData(url_list) # starts async pool with all urls passed
        data[key] = extracted_data # saved extracted data as value for the key which is the same as the key the urls were from
        error_data[key] = error_list
        # actualArticles = [article for article in extracted_data if article is not None]
        print(f"Out of {len(url_list)} urls, {len(extracted_data)} articles were extracted. ({round((len(extracted_data)/len(url_list)) * 100, 3)}%)")

    return data, error_data

def writeData(data, path="src/data/news-data-extracted.json"):
    with open(path, 'w') as f: # 'w' means 'open for writing, trucates the file first'
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    url_json = getData("src/trial_fullscrape.json")
    data, error_data = main(url_json)
    print(f"{len(data)} articles extracted in total.")
    writeData(data, "src/data/fullscrape_extracted.json")
    writeData(error_data, "src/data/error_urls.json")
    print("Completed!")
