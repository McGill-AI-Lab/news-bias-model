import newspaper
import json
from tqdm import tqdm
import os
import nltk
from unidecode import unidecode
from multiprocessing.pool import ThreadPool
from newspaper import ContentExtractor
# def get_urls line 600
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
        articleLinks = self.source.articles #[0:15]
        articleLinks = [article for article in articleLinks if "video" not in article.url]
        print(f"Got {len(articleLinks)} articles!")
        print(articleLinks[15].url)

        articleDataset = []
        errorMessages = []
        workers = 64
        pool = ThreadPool(workers)
        with tqdm(total=len(articleLinks), desc=f"Extracting Article Data ({self.url})") as pbar:
            for article in articleLinks:
                pool.apply_async(
                    self.process_article, args=(article, ), callback=lambda result: self.log_article(pbar, articleDataset, errorMessages, result)
                    )
            pool.close()
            pool.join()
        print(
            f"Finished scraping {self.url}\nResult: {len(articleDataset)}/{len(articleLinks)} successfully scraped.\n"
        )
                
        self.add_articles(self.url, articleDataset)
        
        with open("src/error_messages.txt", "a") as f:
            for errorMessage in errorMessages:
                f.write(f"{errorMessage}\n")
        
    def log_article(self, pbar, articleDataset, errorMessages, result):
        if result[0]:
            articleDataset.append(result[1])
            pbar.update(1)
        else:
            errorMessages.append(result[2])
        
    def process_article(self, article):
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
        except Exception as e:
            return (False, article.url, e)
        return (True, articleData, None)
        
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

extentions_list =[
    "",
    "/politics/",
    "/world/",
    "/war/",
]
if __name__ == "__main__":
    file = open("src/error_messages.txt", "w")
    file.close() # Reset the error logging file at start
    for newspaper_url in list_of_newspapers:
        for extention in extentions_list:
            url = newspaper_url + extention
            print(f"Starting to scrape articles from: {url}")
            scraper = Scraper(url)
            scraper.scrape()

