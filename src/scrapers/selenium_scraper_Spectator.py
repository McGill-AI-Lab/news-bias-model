from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime


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
cut_off_date = datetime(2023,10, 7)
for query in keywords:
    print(f"Starting to search for {query}")
    condition = True
    i = 1
    while condition:

        url = f'https://www.spectator.co.uk/?s={query}&page={i}'
        driver.get(url)

        try:
            # Wait for the elements to be visible
            WebDriverWait(driver, 60).until(
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

            #retrieving the date of posting
            #Some recent papers instead mark "X hours ago"

            date_element = block.find('header', attrs = {"class":'search-card__header'}).span
            if date_element is not None:
                date_element = date_element.text
                try:
                    post_date = datetime.strptime(date_element, "%d %B %Y")

                except ValueError: #this is for newspapers that have "X hours ago"
                    post_date = datetime.now()

                if post_date < cut_off_date:  #stop scraping once no longer in time frame of interest
                    condition = False
                    break

                else:
                    link_tag = block.find('a', {'class': 'search-card__title-link'})
                    link = link_tag.get('href')
                    if 'article' in link: #avoids podcasts
                        print('Just got ' + link)
                        url_set.append(link)
            else:
                pass #skip newspapers that do not have a posted date

        i+=1

driver.quit()

no_duplicate_url_set = list(set(url_set))