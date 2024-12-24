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








### Full scraper for Washington Post
# import json
# import time as t
# from selenium import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from bs4 import BeautifulSoup
#
# # Constants
# NEWS_DOMAIN = "https://www.washingtonpost.com/"
# # The "Load more" button text can vary. Adjust if needed:
# LOAD_MORE_XPATH = "//*[contains(text(), 'Load more')]"
# COOKIES_POP_OVER_XPATH = "//*[contains(text(), 'Reject All')]"
# ARTICLES_PER_SECTION = 100000
# CLICK_DELAY = 0.1  # seconds
#
# # Sections with their specific URLs
# SECTION_URLS = {
#     "Politics":              "https://www.washingtonpost.com/politics/",
#     "Elections":            "https://www.washingtonpost.com/elections/",
#     "Opinions":             "https://www.washingtonpost.com/opinions/",
#     "National":             "https://www.washingtonpost.com/national/",
#     "World":                "https://www.washingtonpost.com/world/",
#     "Style":                "https://www.washingtonpost.com/style/",
#     "Sports":               "https://www.washingtonpost.com/sports/",
#     "Business":             "https://www.washingtonpost.com/business/",
#     "Climate":              "https://www.washingtonpost.com/climate-environment/",
#     "Well+Being":           "https://www.washingtonpost.com/wellness/",
#     "D.C., Md. & Va.":      "https://www.washingtonpost.com/dc-md-va/",
#     "Obituaries":           "https://www.washingtonpost.com/obituaries/",
#     "Weather":              "https://www.washingtonpost.com/weather/",
#     "Arts & Entertainment": "https://www.washingtonpost.com/arts-entertainment/",
#     # "Recipes":              "https://www.washingtonpost.com/recipes/",
#     # "Trending":           "https://www.washingtonpost.com/trending/"  # if valid
# }
#
# # Use a global set to avoid duplicates across sections
# url_set = set()
#
# # Loop through each section
# for section_name, section_url in SECTION_URLS.items():
#     print(f"\nScraping section '{section_name}' -> {section_url}")
#
#     # Set up WebDriver (Firefox with a custom user agent)
#     options = Options()
#     options.set_preference(
#         "general.useragent.override",
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
#         + "(KHTML, like Gecko) Firefox/91.0 Safari/537.36"
#     )
#     driver = webdriver.Firefox(options=options)
#     driver.get(section_url)
#
#     # Attempt to dismiss any cookie pop-up
#     try:
#         cookies_button = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, COOKIES_POP_OVER_XPATH))
#         )
#         cookies_button.click()
#     except:
#         pass  # If "Reject All" didn't appear, do nothing
#
#     prev_count = 0
#     while True:
#         # Let the page stabilize
#         t.sleep(CLICK_DELAY)
#
#         # Parse the current page
#         soup = BeautifulSoup(driver.page_source, "html.parser")
#
#         # Extract all <a> tags that look like article links
#         article_links = soup.find_all("a", href=True)
#         for link in article_links:
#             href = link["href"]
#             # Keep only WP links or relative links that likely point to an article
#             if href.startswith("/") or href.startswith(NEWS_DOMAIN):
#                 # If it's a relative link, convert to absolute
#                 if href.startswith("/"):
#                     href = NEWS_DOMAIN.rstrip("/") + href
#                 url_set.add(href)
#
#         # Check if we've collected enough articles in this section
#         if len(url_set) - prev_count >= ARTICLES_PER_SECTION:
#             print(f"Reached {ARTICLES_PER_SECTION} articles in section '{section_name}'. Stopping pagination.")
#             break
#
#         prev_count = len(url_set)
#
#         # Attempt to click "Load more"
#         try:
#             load_more_button = WebDriverWait(driver, 5).until(
#                 EC.presence_of_element_located((By.XPATH, LOAD_MORE_XPATH))
#             )
#             load_more_button.click()
#         except:
#             print(f"No more 'Load more' button (or timeout) in section '{section_name}'. Moving on.")
#             break
#
#     driver.quit()
#
# # Convert set to a list
# all_urls = sorted(url_set)
# print(f"\nScraping done! Total unique article URLs collected: {len(all_urls)}")
#
# # Construct the JSON structure you requested
# scraped_data = {
#     NEWS_DOMAIN: all_urls
# }
#
# # Save to a JSON file named 'trial_fullscrape.json'
# output_filename = "trial_fullscrape.json"
# with open(output_filename, "w", encoding="utf-8") as f:
#     json.dump(scraped_data, f, indent=4)
#
# print(f"\nJSON saved to '{output_filename}' with the structure:\n")
# print(scraped_data)

