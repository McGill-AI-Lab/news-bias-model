import newspaper
import json
import re
from tqdm import tqdm
import os
import nltk
nltk.download()


class Scraper:
    def __init__(self, url):
        self.url = url

        print(f"Starting to build the source from {self.url}...")
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
                        "title": article.title,
                        "authors": article.authors,
                        # "summary": article.summary,
                        "text": article.text,
                        "published": str(article.publish_date),
                    }
                    articleDataset.append(articleData)
                except Exception as e:
                    print(f"Failed to process article {article.url}: {e}")

                pbar.update(1)

        # Ensure the 'data' directory exists
        os.makedirs("data", exist_ok=True)

        # Check if the file exists
        file_path = "data/news-data.json"
        if os.path.exists(file_path):
            # Load existing data
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
            # Append new data
            existing_data.extend(articleDataset)
            # Write back to the file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=4)
        else:
            # Write new data
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(articleDataset, f, indent=4)


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


for newspaper_url in list_of_newspapers:
    print(f"Starting to scrape articles from: {newspaper_url}")
    scraper = Scraper(newspaper_url)
    scraper.scrape()
    print(
        f"Finished scraping {newspaper_url}!, result: {scraper.source.size()} articles"
    )
