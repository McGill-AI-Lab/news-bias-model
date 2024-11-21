from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

keywords = [
    # Geopolitical Context
    "Israel-Palestine conflict",
    "Gaza crisis",
    "West Bank tensions",
    "Middle East peace talks",
    "Occupied territories",
    "Jerusalem unrest",

    # Events/Actions
    "Ceasefire Israel Palestine",
    "Israeli airstrikes Gaza",
    "Hamas attacks Israel",
    "Rocket attacks Gaza",
    "Israeli military operations",
    "IDF offensive",
    "Palestinian protests",
    "Settler violence West Bank",

    # Humanitarian/International Response
    "Humanitarian crisis Gaza",
    "Civilian casualties Gaza",
    "UN response Israel Palestine",
    "International sanctions Israel",
    "Peace efforts Israel Palestine",
    "Refugee crisis Gaza",
    "Aid for Palestinians",

    # Key Political Figures/Groups
    "Benjamin Netanyahu Gaza",
    "Hamas Israel",
    "Fatah Israel",
    "Mahmoud Abbas Palestine",
    "Israeli government response",
    "Palestinian Authority",

    # International Relations
    "U.S. Israel policy",
    "UN Security Council Israel",
    "Iran Israel tensions",
    "Arab world Israel relations",
    "Egypt Gaza border"
]

driver = webdriver.Chrome()
url_set = []

for query in keywords:
    print(f"Starting to search for {query}")
    condition = True
    i = 1 #page number
    while condition:

        url = f'https://www.chicagotribune.com/page/{i}/?s={query}&post_type&category_name&orderby=date&order=desc&sp%5Bf%5D=2023-10-07&sp%5Bt%5D=2024-11-18&obit__spotlight&obit__site_name'
        driver.get(url)

        try:
            # Wait for the elements to be visible
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article"))
            )
        except:
            print("Timeout or no content available. Exiting loop.")
            condition = False
            break

        #Parsing with bs4
        soup = BeautifulSoup(driver.page_source, 'lxml')

        #Identifying newspapers to scrape
        news_blocks = soup.find_all('article')
        for block in news_blocks:
            link_tag = block.find('figure').a
            link = link_tag.get('href')
            url_set.append(link)

        i+=1

driver.quit()

no_duplicate_url_list = list(set(url_set))

data = {
    "https://www.chicagotribune.com/": no_duplicate_url_list
}
with open(r'data/article_urls.json', 'w') as f:
    json.dump(data, f, indent=4)