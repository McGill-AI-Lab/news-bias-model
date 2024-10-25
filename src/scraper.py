import newspaper
import json
from tqdm import tqdm
import os
import nltk
import re
from unidecode import unidecode
# nltk.download()


class Scraper:
    def __init__(self, url):
        self.url = url
        self.dataFilePath = 'src/data/news-data.json'
        print(f"Starting to build the source...")
        self.source = newspaper.build(
            self.url, number_threads=18, memoize_articles=False
        )  # Can adjust threads as needed

    def scrape(self):
        articleLinks = self.source.articles
        print(f"Got {len(articleLinks)} articles!")

        articleDataset = []
        with tqdm(total=len(articleLinks), desc="Extracting Article Data") as pbar:
            for article in [
                article for article in articleLinks if "video" not in article.url
            ]:  # don't want videos
                try:
                    article.download()
                    article.parse()
                    article.nlp()
                    articleData = {
                        "url": article.url,
                        "title": self.clean_text(article.title),
                        "authors": article.authors,
                        # "summary": article.summary,
                        'text': self.clean_text(article.text),
                        "published": str(article.publish_date),
                    }
                    articleDataset.append(articleData)
                except Exception as e:
                    print(f"Failed to process article {article.url}:\n{e}\n")

                pbar.update(1)
                
                
        self.add_articles(self.url, articleDataset)
        
    # decode escape sequences and remove special characters
    def clean_text(self, text):
        clean_text = text.encode("ascii", "ignore").decode()
        clean_text = clean_text.replace("\n", "").replace("\u2019", "'")
        clean_text = unidecode(clean_text)
        return clean_text
    
    def add_articles(self, sourceName, new_articles):
        data = self.load_existing_data(self.dataFilePath)
        
        if sourceName not in data:
            data[sourceName] = []
        
        data[sourceName].extend(new_articles)
        
        self.save_data(self.dataFilePath, data)
        
    def load_existing_data(self, filePath):
        if os.path.exists(filePath):
            if os.path.getsize(filePath) == 0:
                print(f"{filePath} is empty. Initializing new data structure.")
                return {}
            
            with open(filePath, 'r') as file:
                return json.load(file)
        return {}

    def save_data(self, filePath, data):
        with open(filePath, 'w') as file:
            json.dump(data, file, indent=4)


# newssource = 'https://cnbc.com/'
# articleLinkInput = str(input('What link would you like to scrape articles from?\n(Leave empty to use the link in the code)\n'))
# articleLink = newssource if articleLinkInput.strip() == '' else articleLinkInput
# scraper = Scraper(articleLink)
# scraper.scrape()


list_of_newspapers = [
    "https://nytimes.com",
    "https://washingtonpost.com",
    "https://usatoday.com",
    "https://wsj.com",
    "https://latimes.com",
    "https://nypost.com",
    "https://chicagotribune.com",
    "https://bostonglobe.com",
    "https://sfchronicle.com",
    "https://dallasnews.com",
    "https://houstonchronicle.com",
    "https://inquirer.com",
    "https://startribune.com",
    "https://seattletimes.com",
    "https://miamiherald.com",
    "https://freep.com",
    "https://denverpost.com",
    "https://orlandosentinel.com",
    "https://azcentral.com",
    "https://baltimoresun.com",
    "https://sacbee.com",
    "https://sandiegouniontribune.com",
    "https://stltoday.com",
    "https://tampabay.com",
    "https://cleveland.com",
    "https://kansascity.com",
    "https://charlotteobserver.com",
    "https://post-gazette.com",
    "https://tennessean.com",
    "https://ajc.com",
    "https://dispatch.com",
    "https://cincinnati.com",
    "https://indystar.com",
    "https://jsonline.com",
    "https://newsobserver.com",
    "https://oregonlive.com",
    "https://courier-journal.com",
    "https://desmoinesregister.com",
    "https://reviewjournal.com",
    "https://palmbeachpost.com",
    "https://fresnobee.com",
    "https://staradvertiser.com",
    "https://sltrib.com",
    "https://oklahoman.com",
    "https://star-telegram.com",
    "https://nola.com",
    "https://richmond.com",
    "https://abqjournal.com",
    "https://commercialappeal.com",
    "https://buffalonews.com",
    "https://theistanbulchronicle.com",
]

if __name__ == "__main__":
    for newspaper_url in list_of_newspapers:
        print(f"Starting to scrape articles from: {newspaper_url}")
        scraper = Scraper(newspaper_url)
        scraper.scrape()
        print(
            f"Finished scraping {newspaper_url}!, result: {scraper.source.size()} articles"
        )
