# News Bias Using Word Embeddings

### Data
From https://huggingface.co/datasets/stanford-oval/ccnews, we downloaded all of the parquet files for 2024. 
In parquet2csv.ipynb:
1) Got a list of publishers the collection of all parquet files using polars and ho wmany times each publisher appears in the dataset.
2) We filtered for publishers with more than 1500 articles.
3) We then manually chose publishers we thought could be interesting to look at (i.e. publishers that are popular, from conflicted regions, might be biased, etc.)
4) We then created a df with all of the articles from the chosen publishers and saved it as a csv into newspaper2024.csv
In almost all of these processes, polars.lazy_scan was used and found to be immensely helpful in speeding up the process.

2024.csv includes all english articles from 2024 of chosen newspaper outlets from the CC_NEWS dataset. It has a row per article.

newspaper2024.csv collects all of the articles for a newspaper and stores them inside a cell as one single row. It has the followign columns:
header = [
"Publisher",
"Year",
"Political Alignment" *,
"Articles",
"Article Count",
"Corpus" *,
"Corpus Word Count" *,
"Unique Word Count" *
Note: * means that the column is not filled out yet.
Note: We should add Country column, and fill out political alignment for each newspaper.

### CSV TO JSON

Inside bias_analysis.ipynb, we preprocessed our articles for each newspaper and saved them as a json file with the following fields:

newspapers.json 
```json
{"Publisher": "abcactionnews.com", "Year": 2024, "Political Alignment": "(not filled yet)", "Articles": [], "Article Count": 0, "Corpus": "[[][]..]", "Corpus Word Count": 0, "Unique Word Count": 0}
```
This json is \n deliminted (NDJSON) so we don't have to load all of the file to parse through it.
We will share the csv and the json through hugging face as each of them are around 10 GBs. Email emir.sahin@mail.mcgill.ca if you would like access to it.
### Bias Analysis
Inside bias_analysis.ipynb, we iterate through each "line" (publisher) in the json and train a word2vec on the corpus.
We then save the word2vec model and the word vectors to /models/2024/ folder

We calculate how each geopolitical entity is represented in the corpus by portrayal_word = cosine_similarity(good, geopolitical_entity) - cosine_similarity(bad, geopolitical_entity)
We then save the portrayals for each geopolitical entity for each newspaper into a json file.

Here are the visualizations of how each newspaper portrays Israel-Palestine and Russia-Ukraine conflicts:
![output](https://github.com/user-attachments/assets/8e14ed2e-6ba2-4ae7-aff7-35499af71c1b)
![output1](https://github.com/user-attachments/assets/1dd765ab-52e1-4903-be5e-1ff3ba5662f4)


Contributers:
Emir Sahin: CC_NEWS + the research
Jacob Leader: Repo maintanance + scraping
Oscar, Jacob S, Dory: Scraping

