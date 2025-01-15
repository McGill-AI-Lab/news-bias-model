import json
import os
from preprocess import Preprocessor
from gensim.models import Word2Vec
from tqdm.auto import tqdm
import pathlib


# ### Preprocess every article in the newspaper to create a corpus
# Our corpus will have the format of lists (list of sentences) of lists (sentences)
# We first create a list where each element is the text from a different article of the newspaper.
# We then run preprocess_newspaper(article_list) on this list. 

class FileHandler():
    def __init__(self):
        self.preprocessed_newspapers_path = "src/data/preprocessed_newspapers_dict.json"
        self.newspaper_data_path = "src/israel/data/news-data-extracted.json"
        self.portrayal_words_path = "src/bias-analysis/portrayal_words.json"

    def create_article_list(self, newspaper_name):
        """
        Takes in the file of extracted news and the newspaper name.
        
        returns: [str] || list of articles from the newspaper source
        """

        with open(self.newspaper_data_path, "r") as json_file:
            data = json.load(json_file)

        # Extract all articles from newspaper_source
        newspaper_source = data.get(newspaper_name, [])  # Default to an empty list if not found

        # Loop through articles from newspaper source
        newspaper_articles = []
        for article in newspaper_source:
            if article and isinstance(article, dict) and "text" in article: # Check if article has what we need

                newspaper_articles.append(article["text"])

        print(f"Extracted {len(newspaper_articles)} articles from {newspaper_name}. ({self.newspaper_data_path})")
        
        return newspaper_articles
    
    def save_preprocessed_newspapers(self, preprocessed_newspapers):
        '''
        Saves new newspapers to preprocessed_newspapers_dict.json, first checking if they have already been added
        '''
        # Get old data
        with open(self.preprocessed_newspapers_path, "r") as json_file:
            data = json.load(json_file)

        # add any new preprocessed newspapers (check if new in old)
        for key, value in preprocessed_newspapers.items():  # Use .items() to get key-value pairs
            if key not in data:
                data[key] = value

        # Save new data
        with open(self.preprocessed_newspapers_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
            
    def load_preprocessed_newspapers(self):
        """
        Load preprocessed newspapers from a JSON file.
        
        returns: {} containing preprocessed newspapers
        """
        if os.path.exists(self.preprocessed_newspapers_path):
            try:
                with open(self.preprocessed_newspapers_path, 'r') as file:
                    data = json.load(file)
                    if isinstance(data, dict):
                        print(f"Successfully loaded preprocessed newspapers from {self.preprocessed_newspapers_path}.")
                        return data
                    else:
                        print("Error: JSON data is not a dictionary. Returning an empty dictionary.")
                        
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON file {self.preprocessed_newspapers_path}: {e}")
        else:
            print(f"File {self.preprocessed_newspapers_path} does not exist. Starting with an empty dictionary.")

        return {}
    
    def load_portrayal_words(self):
        '''
        read JSON file with portrayal word lists 
        
        keys: palestinian_words, israeli_words, positive_portrayal_words, negative_portrayal_words
        returns: dict -> str:[str]
        '''
        with open(self.portrayal_words_path, "r") as json_file:
            words_dict = json.load(json_file)
        return words_dict


# Create helper functions to analyze our newspaper and corpus. These functions will help us see: 
# - how many articles are there in the newspaper about our selected topic (Israel-Palestine) since we only scraped relevant articles
# - number of unique words and sentences

class BiasAnalysis():
    def __init__(self):
        self.file_handler = FileHandler()
        self.preprocessor = Preprocessor()
        
        portrayal_words = self.file_handler.load_portrayal_words()
        self.palestinian_words = portrayal_words["palestinian_words"]
        self.israeli_words = portrayal_words["israeli_words"]
        self.positive_portrayal_words = portrayal_words["positive_portrayal_words"] # ex. humane, victim
        self.negative_portrayal_words = portrayal_words["negative_portrayal_words"] # ex. aggressor, terrorist

    def no_of_articles(self, article_list):
        return len(article_list)

    def corpus_size_before(self, article_list):
        
        corpus_size = 0
        for article in article_list:
            corpus_size += len(article.split())
            

        return corpus_size

    def corpus_size_after(self, preprocessed_article_list):
        corpus = preprocessed_article_list

        corpus_size = 0
        for sentence in corpus:
            for word in sentence:
                corpus_size += 1

        return corpus_size


    def no_of_unique_words(self, preprocessed_article_list):
        words = []

        for sentence in preprocessed_article_list:
            for word in sentence:
                if word in words:
                    pass
                else:
                    words.append(word)

        return len(words)

    def no_of_sentences(self, preprocessed_article_list):
        return len(preprocessed_article_list)

    # Palestine
    def occurance(target_word, preprocessed_article_list):
        counter = 0

        for sentence in preprocessed_article_list:
            for word in sentence:
                if word == f"{target_word}":
                    counter += 1
        
        return counter


    def train(self, newspaper_name, sentence_list):
        '''
        Trains a word2vec using gensim library and return the paths for model weights

        returns: tuple of file paths
        '''
        print("Starting model training")
        # Ensure the directory exists
        os.makedirs(newspaper_name, exist_ok=True)

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

        print("Starting Training...")
        model.train(sentence_list, total_examples=len(sentence_list), epochs=20)
        print("Trained Model")
        
        model_path = os.path.join(newspaper_name, f"{newspaper_name}_w2v.model")
        model_path_txt = model_path.replace('.model','.txt')
        model_path_bin = model_path.replace('.model','.bin')
        
        model.save(model_path)
        
        # Save just the word vectors in a text and binary format
        model.wv.save_word2vec_format(model_path_txt, binary=False)
        model.wv.save_word2vec_format(model_path_bin, binary=True)
        print("Saved Model")

        return (
            model_path,
            model_path_txt,
            model_path_bin
        )


    def calculate_portrayal(self, model):
        '''
        Finds how similar keywords are to pos / neg words (ex. israel & victim)
        '''
        palestine_portrayal_scores = {}
        israel_portrayal_scores = {}

        # Access the list of words in the vocabulary
        vocabulary_words = list(model.wv.key_to_index.keys())

        # no of portrayal words
        pos_count = 0
        for word in self.positive_portrayal_words:
            if word in vocabulary_words:
                pos_count += 1
                
        neg_count = 0
        for word in self.negative_portrayal_words:
            if word in vocabulary_words:
                neg_count += 1       

        for word in self.palestinian_words:
            palestine_portrayal_scores[word] = 0
            for positive in self.positive_portrayal_words:
                if positive in vocabulary_words:
                    palestine_portrayal_scores[word] += (model.wv.similarity(f"{word}", f"{positive}")/pos_count)
            for negative in self.negative_portrayal_words:
                if positive in vocabulary_words:
                    palestine_portrayal_scores[word] -= (model.wv.similarity(f"{word}", f"{negative}")/neg_count)

        for word in self.israeli_words:
            israel_portrayal_scores[word] = 0
            for positive in self.positive_portrayal_words:
                if positive in vocabulary_words:
                    israel_portrayal_scores[word] += (model.wv.similarity(f"{word}", f"{positive}")/pos_count)
            for negative in self.negative_portrayal_words:
                if positive in vocabulary_words:
                    israel_portrayal_scores[word] -= (model.wv.similarity(f"{word}", f"{negative}")/neg_count)

        return palestine_portrayal_scores, israel_portrayal_scores


    def create_dict(self, article_list, sentence_list, model_paths, portrayal_palestine_dict, portrayal_israel_dict):
        dict_newspaper = {}
        
        portrayal_palestine_score = 0
        for _, value in portrayal_palestine_dict.items():
            portrayal_palestine_score += (value/4)  # divide by four to get the average

        portrayal_israel_score = 0
        for _, value in portrayal_israel_dict.items():
            portrayal_israel_score += (value/4)
            
        palestine_israel_difference = portrayal_palestine_score - portrayal_israel_score
        print("Palestinians are better portrayed by: ", palestine_israel_difference)

        model_path, model_path_txt, model_path_bin = model_paths
        
        dict_newspaper["no_of_articles"] = self.no_of_articles(article_list)
        dict_newspaper["corpus_size_before_preprocess"] = self.corpus_size_before(article_list)
        dict_newspaper["corpus_size"] = self.corpus_size_after(sentence_list)
        dict_newspaper["no_of_unique_words"] = self.no_of_unique_words(sentence_list)
        dict_newspaper["no_of_sentences"] = self.no_of_sentences(sentence_list)
        
        dict_newspaper["occurance_palestine"] = self.occurance("palestine", sentence_list)
        dict_newspaper["occurance_palestinian"] = self.occurance("palestinian", sentence_list)
        dict_newspaper["occurance_hamas"] = self.occurance("hamas", sentence_list)
        dict_newspaper["occurance_sinwar"] = self.occurance("sinwar", sentence_list)
        dict_newspaper["occurance_israel"] = self.occurance("israel", sentence_list)
        dict_newspaper["occurance_israeli"] = self.occurance("israeli", sentence_list)
        dict_newspaper["occurance_idf"] = self.occurance("idf", sentence_list)
        dict_newspaper["occurance_netanyahu"] = self.occurance("netanyahu", sentence_list)
        
        dict_newspaper["model_location"] = model_path
        dict_newspaper["vectors_txt_location"] = model_path_txt
        dict_newspaper["vectors_bin_location"] = model_path_bin
        
        dict_newspaper["portrayal_palestine"] = portrayal_palestine_dict
        dict_newspaper["portrayal_palestine_score"] = portrayal_palestine_score
        dict_newspaper["portrayal_israel"] = portrayal_israel_dict
        dict_newspaper["portrayal_israel_score"] = portrayal_israel_score
        dict_newspaper["palestine-israel_score"] = palestine_israel_difference
        
        dict_newspaper["articles"] = article_list
        dict_newspaper["preprocessed"] = sentence_list
        
        return dict_newspaper


    def main(self, newspaper_list):
        """
        1. Get a list of newspapers
        2. Create a dictionary of newspapers, each being a dictionary -> {__: {},__:{},__:{}}
        3. For every newspaper, have the following keys:
                # of articles, corpus size (before preprocessing), # of unique words (before preprocessing),
                list of articles (only text) (before preprocessing),
                preprocessed articles (a list of sentences, which are a list of words)
                corpus size (after preprocessing), # of unique words (after preprocessing),
                how many times each target word appears (palestine, israel, hamas, idf, netanyahu, sinwar, etc.)
        4. Train a word2vec, save the model and the weights,
            bias score for palestine, israel, hamas, idf, etc,
        """

        preprocessed_newspapers = self.file_handler.load_preprocessed_newspapers()

        for newspaper in newspaper_list:
            # check if the newspaper is already preprocessed, if it is skip it
            if f"{newspaper}" not in preprocessed_newspapers:
                article_list = self.file_handler.create_article_list(newspaper)
                sentence_list = self.preprocessor.preprocess_newspaper(article_list)
                
                model_paths = self.train(newspaper, sentence_list)

                model = Word2Vec.load(f"{newspaper}/{newspaper}_w2v.model")
                portrayal_palestine, portrayal_israel = self.calculate_portrayal(model)
                
                # print(f"{newspaper}", portrayal_palestine, portrayal_israel)


                preprocesed_newspaper_data = self.create_dict(
                    article_list=article_list, 
                    sentence_list=sentence_list, 
                    model_paths=model_paths, 
                    portrayal_israel_dict=portrayal_israel, 
                    portrayal_palestine_dict=portrayal_palestine
                )
                preprocessed_newspapers[newspaper] = preprocesed_newspaper_data
                
                self.file_handler.save_newspaper_dict(preprocessed_newspapers)
                
        return preprocessed_newspapers
    
def run_flow():
    '''
    Controls what parts of the code to run
    True -> run master
    False -> only assess models
    
    returns: bool
    '''
    dir = pathlib.Path(".")
    found_models = list(dir.rglob("*.model")) # Recursively find all the files with the .model extentions
    if found_models:
        
        run_code_input = ''
        while len(run_code_input) != 1: # While not y or n
            run_code_input = str(input(f"\nWARNING: {len(found_models)} model(s) already exists, would you still like to create new models (y/n)\n'list' to display all the models\n"))
            
            if 'list' in run_code_input:
                print(*found_models, sep="\n\n")
            
        return run_code_input == 'y'
    
    return True # No models were found
            

if __name__ == "__main__":
    newspaper_list = ["cnn.com", "WashingtonPost.com"]
    run_master = run_flow()
    bias_analysis = BiasAnalysis()

    if run_master:
        processed_newspapers  = bias_analysis.main(newspaper_list)


    model = Word2Vec.load(f"WashingtonPost.com/WashingtonPost.com_w2v.model")

    result = model.wv.similarity("attacker", "israeli")
    # print(model.wv.most_similar('terrorism', topn=10))
    # print(model.wv.most_similar('peace', topn=10))
    # print(model.wv.most_similar('occupation', topn=10))
    print(f"Similarity Between 'attacker' and 'israeli' is {result} for washington post")
