import newspaper
import json
from tqdm import tqdm
from multiprocessing import Pool
import unidecode


def getData(path):
    with open(path, 'r') as f:
        url_dict = json.load(f)
    
    return url_dict
    
def processArticle(url):
    paper = newspaper.article(url) # Makes a new Article instance

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
    data = []
    pool = Pool(processes=32)  # may be too high, not sure

    # tqdm gives us a progress bar, args are self-explanitory
    with tqdm(total=len(url_list), desc=f"Extracting Article Data") as pbar:
        for url in url_list:
            pool.apply_async(
                processArticle,  # process article asynchronously
                args=(url,), # args expects a tuple, so we give it a tuple with one item
                callback=lambda single_newspaper_data: appendData(data, single_newspaper_data, pbar) # appends the result after processArticle has run, passes data by reference, so we can update it
            )

        pool.close()
        pool.join()  # Wait for all processes to finish

    return data

def appendData(data, single_newspaper_data, pbar):
    data.append(single_newspaper_data)
    pbar.update(1)
    
def main(url_dict):
    data = {}
    keys = url_dict.keys()
    
    for key in keys:
        print(f"Now extracting the {key} urls...")
        url_list = url_dict.get(key, [])
        extracted_data = extractData(url_list) # starts async pool with all urls passed
        data[key] = extracted_data # saved extracted data as value for the key which is the same as the key the urls were from
        
    return data

def writeData(data, path="src/data/news-data-extracted.json"):
    with open(path, 'w') as f: # 'w' means 'open for writing, trucates the file first'
        json.dump(data, f, indent=4)
        
if __name__ == "__main__":
    url_json = getData("src/data/article_urls.json")
    data = main(url_json)
    # print(data)
    writeData(data, "src/data/news-data-extracted.json")
    

