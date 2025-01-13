import json
import os
from preprocess import Preprocessor
from gensim.models import Word2Vec


# ### Preprocess every article in the newspaper to create a corpus
# Our corpus will have the format of lists (list of sentences) of lists (sentences)
# We first create a list where each element is the text from a different article of the newspaper.
# We then run preprocess_newspaper(article_list) on this list. 

def create_article_list(extracted_file, newspaper_name):
    """
    Takes in the file of extracted news and the newspaper name.
    Outputs an article (text) list for the given newspaper.
    """

    # Load the JSON file
    with open(extracted_file, "r") as json_file:
        data = json.load(json_file)

    # Extract newspaper data
    newspaper = data.get(newspaper_name, [])  # Default to an empty list if not found
    newspaper_articles = []

    # Loop through articles in the newspaper
    for article in newspaper:
        # Check if article has a valid "text" key
        if article and isinstance(article, dict) and "text" in article:
            newspaper_articles.append(article["text"])  # Use append to add the text to the list

    print(f"Extracted {len(newspaper_articles)} articles from {newspaper_name}.")
    return newspaper_articles



def preprocess_newspaper(article_list):
    """ 
    Takes in article list and returns a list of list which is preprocessed article in the form 
        of every element in the list is a sentence which consist of lists of words
    """

    if not article_list:  # Handle empty or None input
        print("No articles provided for preprocessing.")
        return []

    preprocessed_article_list = []

    for i, article in enumerate(article_list):
        preprocessed_article_list.extend(preprocess_article(article))  # extends preproccessed
        # articles to newspaper's article list
        print(f"article {i} preprocessed")

    return preprocessed_article_list


# Lets try with CNN
article_list = create_article_list("data/news-data-extracted.json", "cnn.com")
print(article_list)
preprocessed = preprocess_newspaper(article_list)
print(preprocessed)


# Create helper functions to analyze our newspaper and corpus. These functions will help us see: 
# - how many articles are there in the newspaper about our selected topic (Israel-Palestine) since we only scraped relevant articles
# - corpus size (word count) before and after preprocessing, which will result in some reductions
# - number of unique words and sentences
# - number of occurance of a unique word in the preprocessed corpus

# create get_article_number, corpus size, and other helper functions

def no_of_articles(article_list):
    return len(article_list)


def corpus_size_before(article_list):
    corpus = article_list

    corpus_size = 0
    for article in article_list:
        corpus_size += len(article.split())

    return corpus_size


def corpus_size_after(preprocessed_article_list):
    corpus = preprocessed_article_list

    corpus_size = 0
    for sentence in corpus:
        for word in sentence:
            corpus_size += 1

    return corpus_size


def no_of_unique_words(preprocessed_article_list):
    words = []

    for sentence in preprocessed_article_list:
        for word in sentence:
            if word in words:
                pass
            else:
                words.append(word)

    return len(words)

def no_of_sentences(preprocessed_article_list):
    return len(preprocessed_article_list)


""" Occurance Counter """

# Palestine
def occurance(target_word, preprocessed_article_list):
    counter = 0

    for sentence in preprocessed_article_list:
        for word in sentence:
            if word == f"{target_word}":
                counter += 1
    
    return counter


# ### Training function
# Trains a word2vec using gensim library and return the paths for model weights and word vectors

def train(newspaper_name, sentence_list):

    # Ensure the directory exists
    os.makedirs(newspaper_name, exist_ok=True)

    # Train Word2Vec model
    # Initialize the model with parameters
    model = Word2Vec(
        sentences=sentence_list,
        vector_size=300,
        window=5, # max distance between word and furthest word
        min_count=10, # ignores words with <10 occurances
        sg=1, # skip-gram
        workers=4, # Threads
        negative=20 # Negative sampling
    )

    # Train and save the model
    model.train(sentence_list, total_examples=len(sentence_list), epochs=20)
    
    model_path = os.path.join(newspaper_name, f"{newspaper_name}_w2v.model")
    model_path_txt = model_path.replace('.model','.txt')
    model_path_bin = model_path.replace('.model','.bin')
    
    model.save(model_path)
    
    # Save just the word vectors in a text and binary format
    model.wv.save_word2vec_format(model_path_txt, binary=False)
    model.wv.save_word2vec_format(model_path_bin, binary=True)


    return (
        model_path,
        model_path_txt,
        model_path_bin
    )


# ### Calculate portrayal

def calculate_portrayal(model, palestinian_words, israeli_words, positive_portrayal_words, negative_portrayal_words): # target_words and portrayal_words are lists
    palestine_portrayal_scores = {}
    israel_portrayal_scores = {}

    # Access the list of words in the vocabulary
    vocabulary_words = list(model.wv.key_to_index.keys())

    # no of portrayal words
    pos_count = 0
    for word in positive_portrayal_words:
        if word in vocabulary_words:
            pos_count += 1
            
    neg_count = 0
    for word in negative_portrayal_words:
        if word in vocabulary_words:
            neg_count += 1       


    for word in palestinian_words:
        palestine_portrayal_scores[word] = 0
        for positive in positive_portrayal_words:
            if positive in vocabulary_words:
                palestine_portrayal_scores[word] += (model.wv.similarity(f"{word}", f"{positive}")/pos_count)
        for negative in negative_portrayal_words:
            if positive in vocabulary_words:
                palestine_portrayal_scores[word] -= (model.wv.similarity(f"{word}", f"{negative}")/neg_count)

    for word in israeli_words:
        israel_portrayal_scores[word] = 0
        for positive in positive_portrayal_words:
            if positive in vocabulary_words:
                israel_portrayal_scores[word] += (model.wv.similarity(f"{word}", f"{positive}")/pos_count)
        for negative in negative_portrayal_words:
            if positive in vocabulary_words:
                israel_portrayal_scores[word] -= (model.wv.similarity(f"{word}", f"{negative}")/neg_count)

    return palestine_portrayal_scores, israel_portrayal_scores


# Should I include gaza, if yes, add an occurance function and add it to the target word_list and portrayal

# Save newspaper dictionary


def save_newspaper_dict(newspaper_dict):
    # File path for the JSON file
    file_path = "preprocessed_newspapers_dict.json"

    # Open the JSON file
    with open(file_path, "r") as json_file:
        data = json.load(json_file)  # Load existing data

    # Iterate over items in the dictionary
    for key, value in newspaper_dict.items():  # Use .items() to get key-value pairs
        if key not in data:
            data[key] = value  # Save new key-value pair

    # Save updated data back to the file
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

def load_preprocessed_newspapers(json_file):
    """
    Load preprocessed newspapers from a JSON file.
    """
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)
                if isinstance(data, dict):
                    print(f"Successfully loaded preprocessed newspapers from {json_file}.")
                    return data
                else:
                    print("Error: JSON data is not a dictionary. Returning an empty dictionary.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON file {json_file}: {e}")
    else:
        print(f"File {json_file} does not exist. Starting with an empty dictionary.")

    return {}


newspaper_list = ["cnn.com", "WashingtonPost.com"]

def master(extracted_file, newspaper_list):
    """
    Get a list of newspapers
    Create a dictionary of newspapers, which is a dictionary
    For every newspaper, have the following keys:
    # of articles, corpus size (before preprocessing), # of unique words (before preprocessing),
    list of articles (only text) (before preprocessing),
    preprocessed articles (a list of sentences, which are a list of words)
    corpus size (after preprocessing), # of unique words (after preprocessing),
    how many times each target word appears (palestine, israel, hamas, idf, netanyahu, sinwar, etc.)
    train a word2vec, save the model and the weights,
    bias score for palestine, israel, hamas, idf, etc,
    Add the following key to each articles
    """

    preprocessed_newspapers = load_preprocessed_newspapers("preprocessed_newspapers_dict.json")


    # check if the newspaper is already preprocessed, if it is skip it
    for newspaper in newspaper_list:
        if f"{newspaper}" not in preprocessed_newspapers:
            preprocessed_newspapers[newspaper] = {}
            dict_newspaper = preprocessed_newspapers[newspaper]

            article_list = create_article_list(extracted_file, newspaper)
            sentence_list = preprocess_newspaper(article_list)

            dict_newspaper["no_of_articles"] = no_of_articles(article_list)
            dict_newspaper["corpus_size_before_preprocess"] = corpus_size_before(article_list)
            dict_newspaper["corpus_size"] = corpus_size_after(sentence_list)
            dict_newspaper["no_of_unique_words"] = no_of_unique_words(sentence_list)
            dict_newspaper["no_of_sentences"] = no_of_sentences(sentence_list)
            dict_newspaper["occurance_palestine"] = occurance("palestine", sentence_list)
            dict_newspaper["occurance_palestinian"] = occurance("palestinian", sentence_list)
            dict_newspaper["occurance_hamas"] = occurance("hamas", sentence_list)
            dict_newspaper["occurance_sinwar"] = occurance("sinwar", sentence_list)
            dict_newspaper["occurance_israel"] = occurance("israel", sentence_list)
            dict_newspaper["occurance_israeli"] = occurance("israeli", sentence_list)
            dict_newspaper["occurance_idf"] = occurance("idf", sentence_list)
            dict_newspaper["occurance_netanyahu"] = occurance("netanyahu", sentence_list)
            dict_newspaper["model_location"] = ""
            dict_newspaper["vectors_txt_location"] = ""
            dict_newspaper["vectors_bin_location"] = ""
            dict_newspaper["portrayal_palestine"] = {}
            dict_newspaper["portrayal_palestine_score"] = 0
            dict_newspaper["portrayal_israel"] = {}
            dict_newspaper["portrayal_israel_score"] = 0
            dict_newspaper["palestine-israel_score"] = 0
            dict_newspaper["articles"] = article_list
            dict_newspaper["preprocessed"] = sentence_list

            # actually fill out the values for model-related keys
            dict_newspaper["model_location"], dict_newspaper["vectors_txt_location"], dict_newspaper["vectors_bin_location"] = train(newspaper, sentence_list)

            # Load the model from a file
            model = Word2Vec.load(f"{newspaper}/{newspaper}_w2v.model")


            palestinian_words = ["palestine", "palestinian", "hamas", "sinwar"]
            israeli_words = ["israel", "israeli", "idf", "netanyahu"]

            # positive categories: general (good etc), victim, 
            positive_portrayal_words = ["positive", "good", "victim", "resilient", "justified", "defend", "innocent", "rightful", "humane"]
            negative_portrayal_words = ["negative", "bad", "aggressor", "attacker", "brutal", "illegal", "terrorist", "barbaric", "massacre", "invade"]

            dict_newspaper["portrayal_palestine"], dict_newspaper["portrayal_israel"] = calculate_portrayal(model,  palestinian_words, israeli_words, positive_portrayal_words, negative_portrayal_words)
            print(f"{newspaper}", dict_newspaper["portrayal_palestine"], dict_newspaper["portrayal_israel"])

            for key, value in dict_newspaper["portrayal_palestine"].items():
                dict_newspaper["portrayal_palestine_score"] += (value/4)  # divide by four to get the average

            for key, value in dict_newspaper["portrayal_israel"].items():
                dict_newspaper["portrayal_israel_score"] += (value/4)

            dict_newspaper["palestine-israel_score"] = dict_newspaper["portrayal_palestine_score"] - dict_newspaper["portrayal_israel_score"]
            print("palestinian are better portrayed by: ", dict_newspaper["palestine-israel_score"])

            save_newspaper_dict(preprocessed_newspapers)
            
    return preprocessed_newspapers


processed_newspapers = master("data/news-data-extracted.json", newspaper_list)


model = Word2Vec.load(f"WashingtonPost.com/WashingtonPost.com_w2v.model")


model.wv.similarity("attacker", "terrorist")

if __name__ == "__main__":












# from newspaper import Article # Newspaper3K, NOT 4k
# import json
# from tqdm import tqdm
# from multiprocessing import Pool
# import time
# # import unidecode

# def getData(path):
#     with open(path, 'r') as f:
#         url_dict = json.load(f)

#     return url_dict

# def processArticle(url):
#     try:
#         paper = Article(url) # Makes a new Article instance
#         paper.download() # Gets the HTML content
#         paper.parse() # Makes a new Article instance
#     except Exception as e:
#         # print(f"Error processing {url}: {e}")
#         return None  # Return None if an error occurs

#     title = paper.title
#     authors = paper.authors
#     date = paper.publish_date
#     text = paper.text

#     newspaper_data = {
#         "url": url,
#         "title": cleanText(title),
#         "authors": authors,
#         "date": str(date),
#         "text": cleanText(text)
#     }

#     return newspaper_data


# def cleanText(text):
#     clean_text = text.encode("ascii", "ignore").decode() # Gets rid of chars that arent ASCII ex. accented chars
#     clean_text = clean_text.replace("\n", "").replace("\u2019", "'") # Removes annoying escape sequences
#     # clean_text = unidecode(clean_text) # Makes it plain text
#     return clean_text

# def extractData(url_list):
#     newspaper_source_data = []
#     # pool = Pool(processes=10)
#     batches = batchUrls(url_list, 1000)
#     error_list = []

#     for batch_num, batch in enumerate(batches):
#         time.sleep(5)
#         with tqdm(total=len(batch), desc=f"Extracting Article Data (batch {batch_num + 1})") as pbar:
#             with Pool(processes=4) as pool:
#                 for url in batch:
#                     pool.apply_async(
#                         processArticle,  # process article asynchronously
#                         args=(url,),  # args expects a tuple, so we give it a tuple with one item
#                         callback=lambda single_newspaper_data: appendData(newspaper_source_data, single_newspaper_data, pbar, error_list, url) # appends the result after processArticle has run, passes data by reference, so we can update it                    )
#                     )

#                 # print("DONE, CLOSING")
#                 pool.close()
#                 pool.join()

#     # Wait for all processes to finish
#     return newspaper_source_data, error_list

# def batchUrls(urls, batch_size):
#     batches = []
#     start_num = 0

#     while start_num < len(urls):
#         batch = urls[start_num:start_num + batch_size]
#         batches.append(batch)
#         start_num += batch_size  # Move to the next batch

#     print(f"Made {len(batches)} batches of {batch_size} urls each")

#     return batches

# def appendData(data, single_newspaper_data, pbar, error_list, url):
#     pbar.update(1)
#     if single_newspaper_data is not None:
#         data.append(single_newspaper_data)
#     else:
#         error_list.append(url)

# def main(url_dict):
#     data = {}
#     keys = url_dict.keys()
#     error_data = {}
#     for key in keys:
#         print(f"Now extracting the {key} urls...")
#         url_list = url_dict.get(key, [])
#         extracted_data, error_list = extractData(url_list) # starts async pool with all urls passed
#         data[key] = extracted_data # saved extracted data as value for the key which is the same as the key the urls were from
#         error_data[key] = error_list
#         # actualArticles = [article for article in extracted_data if article is not None]
#         print(f"Out of {len(url_list)} urls, {len(extracted_data)} articles were extracted. ({round((len(extracted_data)/len(url_list)) * 100, 3)}%)")

#     return data, error_data

# def writeData(data, path="fullscrape_extracted.json"):
#     with open(path, 'w') as f: # 'w' means 'open for writing, trucates the file first'
#         json.dump(data, f, indent=4)

# if __name__ == "__main__":
#     url_json = getData("trial_fullscrape.json")
#     preprocessor = Preprocessor()

#     data, error_data = main(url_json)
#     print(f"{len(data)} articles extracted in total.")
#     url_json = getData(r"trial_fullscrape.json")
#     data = main(url_json)
#     # print(data)
#     writeData(data, "fullscrape_extracted.json")
#     writeData(error_data, "src/data/error_urls.json")
#     print("Completed!")
        

