import newspaper
import json
import re
from tqdm import tqdm     

class Scraper:
    def __init__(self, url):
        self.url = url
        
        print(f"Starting to build the source from {self.url}...")
        self.source = newspaper.build(self.url, number_threads=18, memoize_articles=False) # Can adjust threads as needed
        
    def scrape(self):
        articleLinks = self.source.articles
        print(f"Got {len(articleLinks)} articles!")
        
        articleDataset = []
        with tqdm(total=len(articleLinks), desc="Extracting Article Data") as pbar:
            for article in [article for article in articleLinks if 'video' not in article.url]: # dont want videos
                try:
                    article.download()
                    article.parse()
                    article.nlp()
                    articleData = {
                        'url': article.url,
                        'title': article.title,
                        'authors': article.authors,
                        'summary': article.summary,
                        'text': article.text.encode('utf-8').decode('unicode_escape'),
                        'published': str(article.publish_date),
                    }
                    articleDataset.append(articleData)
                except Exception as e:
                    print(f"Failed to process article {article.url}: {e}")
                    
                pbar.update(1)

        with open('data/news-data.json', 'w') as f:
            json.dump(articleDataset, f, indent=4)

if __name__ == '__main__':
    newssource = 'https://cnbc.com/'
    articleLinkInput = str(input('What link would you like to scrape articles from?\n(Leave empty to use the link in the code)\n'))
    articleLink = newssource if articleLinkInput.strip() == '' else articleLinkInput
    scraper = Scraper(articleLink)
    scraper.scrape()
