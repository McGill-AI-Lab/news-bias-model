from gensim.utils import tokenize
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

# We need to preprocess our data. Preprocessing includes dividing articles into sentences using nltk library, since Word2Vec is trained by using list of words (sentences). Nltk uses a machine learning model to decide how to divide an article into sentences, so there will be some inaccuracies, however we can ignore these. After, we want all words to be lowercase. We want to remove all extremely high-frequency words which don't really contribute to any of the word embeddings for other words they co-occur with as these high-frequency word co-occur with a big portion of our corpus. These words are called "stop words" and some example would be "I", "you", "of", "there" etc. Then, we lemmatize words, i.e. try to convert each word to their root (running -> run). The goal of this process is that so we have more information about the word "run", instead of the information being distributed between various forms of the word ("runs", "running", "ran"). For more information on lemmatizers: https://www.geeksforgeeks.org/python-lemmatization-with-nltk/. Finally, we remove punctuation and put all of these functions in one "preprocess" function.

class Preprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words("english"))
        
    def tokenize_article(self, article):
        '''
        Tokenizes article into sentences, which are then tokenized into words
        
        input: ONE article
        returns: list of generator objects (each a sentence)
        '''
            
        sentences  = sent_tokenize(article, language="english") # divide article into sentences
        
        tokenized_article = []
        for sentence in sentences:
            tokenized_sentence = tokenize(sentence) # divide sentences into tokens (most of the time words but further split in some cases)
            tokenized_article.append(tokenized_sentence) 
        return tokenized_article

    def lowercase(self, tokenized_article):
        lowercase_article = []

        # Could use list comprehensions here
        for sentence in tokenized_article:
            current_sentence = []
            for word in sentence:
                current_sentence.append(word.lower())
            lowercase_article.append(current_sentence)

        return lowercase_article

    def remove_stopwords(self, tokenized_article):
        '''
        Removes stopwords (common words that carry no or little meaning -> to, there, the, when, where, etc.)
        '''
        
        # Iterate over the index and content of each sentence
        for i in range(len(tokenized_article)):
            # Create a new list for the filtered sentence
            filtered_sentence = []
            for word in tokenized_article[i]:
                if word not in self.stop_words:
                    filtered_sentence.append(word)
            # Replace the original sentence with the filtered sentence
            tokenized_article[i] = filtered_sentence
        return tokenized_article

    def lammetization(tokenized_article):
        lammetizer = WordNetLemmatizer()

        lammetized_article = []

        for sentence in tokenized_article:
            current_sentence = []
            for word in sentence:
                current_sentence.append(lammetizer.lemmatize(word))
            lammetized_article.append(current_sentence)

        return lammetized_article


    def remove_punctuation(tokenized_article):
        punc_removed_article = []

        for sentence in tokenized_article:
            punc_removed_sentence = []
            for word in sentence:
                # Split by punctuation, filter out empty strings, and join back if needed
                split_word = ''.join(re.split(r"[^\w]+", word))
                if split_word:  # Add non-empty words only
                    punc_removed_sentence.append(split_word)

            punc_removed_article.append(punc_removed_sentence)

        return punc_removed_article

    def preprocess_article(article):
        t_article = tokenize_article(article)
        l_article = lowercase(t_article)
        r_article = remove_stopwords(l_article)
        la_article = lammetization(r_article)
        re_article = remove_punctuation(la_article)
        return re_article


    print(stop_words)


    preprocessed = preprocess_article(first_article)