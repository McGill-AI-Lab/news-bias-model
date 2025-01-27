from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time

#! THIS CODE ONLY GETS URLS

# Set up the Selenium WebDriver (you need to have ChromeDriver installed for Chrome)
driver = webdriver.Chrome()
query_list = ['palestine', 'israel', 'gaza', 'hamas', 'Jihad']

url_set = []

# Load the CNN search page
for query in query_list:
    print(f'Starting to query "{query}"')
    i = 0
    while True:
        i += 1
        url = f'https://nypost.com/search/{query}/page/{i}/'
        
        try:
            driver.get(url)
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "page__content"))
            )
        except:
            print("Timeout or no content available. Exiting loop.")
            break
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        story_links = [a['href'] for a in soup.select('.search-results__story .story__headline a')]
        
        if story_links:
            url_set.extend(story_links)
            print(f"Got {len(story_links)}!")
        else:
            break

driver.quit()
print(f"got {len(url_set)} links!")

links_list = list(set(url_set))
with open('urls.txt', 'a') as f:
    for url in links_list:
        f.write(f"{url}\n")

data = {
    "nypost.com": links_list
}
with open('data/news-data.json', 'w') as f:
    json.dumps(data, f, indent=4)
        
