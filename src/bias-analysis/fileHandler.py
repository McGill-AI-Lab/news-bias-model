import json
import os

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
                print("Starting with an empty dictionary.")
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
