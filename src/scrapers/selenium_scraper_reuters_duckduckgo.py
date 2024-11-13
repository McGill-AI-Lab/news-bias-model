# 2024-11-12
# Jacob Sauvé
# Scraper using DuckDuckGo which should work for any news site
# Modified here to scrape Reuters

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time as t
import os


# Constants
START_DATE = "2023-10-07" # earliest date for scraped articles (October 7th)
NEXT_BUTTON_ID = "more-results"
LINK_CONTAINER_CLASS = "react-results--main"


# Construct a query to DuckDuckGo-search for multiple keywords at once on a
# given news site
current_date = t.strftime('%y-%m-%d', t.localtime())
keywords = [
    "Israel", 
    "Gaza", 
    "Jerusalem", 
    "IDF", 
    "Hamas", 
    "Palestine", 
]
# keyword_string = "+".join(keywords)


news_site = "www.reuters.com" # Only Reuters
url_set = list() # Initialise list of scraped URLs

for keyword in keywords:
    # DDG search operators:
    # https://duckduckgo.com/duckduckgo-help-pages/results/syntax/
    query = keyword + f"+site%3A{news_site}&df={START_DATE}..{current_date}"
    url = "https://duckduckgo.com/?q=" + query
    
    
    # Set up WebDriver for Firefox (with custom user-agent to evade protection)
    options = Options()
    options.set_preference(
        "general.useragent.override",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, \
    like Gecko) Firefox/91.0 Safari/537.36"
        )
    driver = webdriver.Firefox(options=options) 
    driver.get(url)
    
    print(f"\nBeginning scraping of {news_site}!")
    
    # While the 'Load More' button exists, click on it, THEN scrape all URLs 
    while True:
        t.sleep(0.01)
        # check if more results exist
        try:
            next_button = WebDriverWait(driver, 10).until(
                # check for Next button
                    EC.presence_of_element_located((By.ID, NEXT_BUTTON_ID))
                )
            next_button.click()
        except:
            print("Error: Timeout or no button found. Exiting loop...")
            break 


    # Scrape all articles
    soup = BeautifulSoup(driver.page_source, 'html.parser') # beautify the HTML   
    link_container = soup.find("ol", class_ = LINK_CONTAINER_CLASS)

    if link_container:
        results = link_container.find_all('a', href=True)
        links = [
            link.get('href') for link in results if "http" in link.get('href')
            ]
        print(f"Total: {len(links)} URLs scraped")
        url_set.extend(links)
    else:
        print("Error: Link container was not found.")
        
    driver.quit()


url_list = list(set(url_set))
print(f"Number of articles: {len(url_list)}")
# Name file with timestamp for differentiation
path = t.strftime(f'~/Desktop/{news_site}_%y-%m-%d-%Hh%Mmin%Ss_urls.txt', t.localtime())
with open(os.path.expanduser(path), 'w') as file: # expands '~' to home directory
    urls_chained = '"' + '", "'.join(url_list) + '"'
    file.write(f'"{news_site}":[{urls_chained}]')