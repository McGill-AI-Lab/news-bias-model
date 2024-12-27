# 2024-11-12
# Jacob Sauvé
# Washington Post Scraper

# ! THIS CODE ONLY GETS URLS !

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time as t

# Constants
NEWS_SITE = "www.washingtonpost.com"
NEXT_BUTTON_TXT = "//*[contains(text(), 'Load more results')]"
COOKIES_POP_OVER_TXT = "//*[contains(text(), 'Reject All')]"
ARTICLES_PER_KEYWORD = 10000 # Must be an integer, ideally 10n
CLICK_DELAY = 0.5 # In seconds, time between auto clicks to allow page to load

keywords = [
    "Israel", 
    "Gaza", 
    "Jerusalem", 
    "IDF", 
    "Hamas", 
    "Palestine", 
]

url_set = list() # Set of scraped URLs


for keyword in keywords:
    # Set up WebDriver for Firefox (with custom user-agent to evade protection)
    options = Options()
    options.set_preference(
        "general.useragent.override",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, \
    like Gecko) Firefox/91.0 Safari/537.36"
        ) # Custom user agent to appear less like a bot
    driver = webdriver.Firefox(options=options)
    url = f"https://www.washingtonpost.com/search/?query={keyword}"   
    driver.get(url)
    
    print(f"\nBeginning scraping of {NEWS_SITE} for keyword '{keyword}'!")
    
    # Check for cookie acceptance pop-up and click "Reject All"
    try:
        cookies_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, COOKIES_POP_OVER_TXT))
        )
        cookies_button.click()
    except:
        pass
    
    # While the 'Load More' button exists, click on it, THEN scrape all URLs
    # Actually - only scraping a maximum of ARTICLES_PER_KEYWORD articles
    for load_more in range((ARTICLES_PER_KEYWORD)//10-1):
        t.sleep(CLICK_DELAY)
        # Check if more results exist
        try:
            next_button = WebDriverWait(driver, 10).until(
                # Check for Next button
                    EC.presence_of_element_located((By.XPATH, NEXT_BUTTON_TXT))
                )
            next_button.click()
            print(f"{(1+load_more)*10} articles loaded...")
        except:
            # Occurs if the button did not load, i.e. no more search results 
            print("Error: Timeout or no button found. Exiting loop...")
            break 

    
    soup = BeautifulSoup(driver.page_source, 'html.parser') # Beautify the HTML
    # Select 2nd section in HTML page (the link container)
    link_container = soup.find_all("section")[1]

    if link_container:
        # Scrape all articles
        results = link_container.find_all('a', href=True)
        links = [
            link.get('href') for link in results if link.get('href')
            ]
        print(f"Total: {len(links)} URLs scraped")
        url_set.extend(links)
        print("URLs successfully scraped!")
    else:
        print("Error: Link container was not found.")
        
    driver.quit()


url_list = list(set(url_set)) # Remove link duplicates
print(f"Number of articles: {len(url_list)}")
# Name file with timestamp for differentiation
path = t.strftime(
    f'news-bias-model/src/data/{NEWS_SITE}_%y-%m-%d-%Hh%Mmin%Ss_urls.txt',
    t.localtime()
)
# Save URLs to a .txt file, to be converted to json later
with open(path, 'a') as file:
    urls_chained = '"' + '", "'.join(url_list) + '"'
    file.write(f'"{NEWS_SITE}":[{urls_chained}]')

