from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json

#! THIS CODE ONLY GETS URLS

# Set up the Selenium WebDriver (you need to have ChromeDriver installed for Chrome)
driver = webdriver.Chrome()
keywords = [
    # Geopolitical Context
    "Israel", 
    "Gaza", 
    "West-bank Gaza", 
    "IDF", 
    "Hamas", 
    "Palestine", ]
#     "Israel-Palestine conflict", 
#     "Gaza crisis", 
#     "West Bank tensions", 
#     "Middle East peace talks", 
#     "Two-state solution", 
#     "Occupied territories", 
#     "Jerusalem unrest",
    
#     # Events/Actions
#     "Ceasefire Israel Palestine", 
#     "Israeli airstrikes Gaza", 
#     "Hamas attacks Israel", 
#     "Rocket attacks Gaza", 
#     "Israeli military operations", 
#     "IDF offensive", 
#     "Palestinian protests", 
#     "Settler violence West Bank",
    
#     # Humanitarian/International Response
#     "Humanitarian crisis Gaza", 
#     "Civilian casualties Gaza", 
#     "UN response Israel Palestine", 
#     "International sanctions Israel", 
#     "Peace efforts Israel Palestine", 
#     "Refugee crisis Gaza", 
#     "Aid for Palestinians",
    
#     # Key Political Figures/Groups
#     "Benjamin Netanyahu Gaza", 
#     "Hamas Israel", 
#     "Fatah Israel", 
#     "Mahmoud Abbas Palestine", 
#     "Israeli government response", 
#     "Palestinian Authority",
    
#     # International Relations
#     "U.S. Israel policy", 
#     "UN Security Council Israel", 
#     "Iran Israel tensions", 
#     "Arab world Israel relations", 
#     "Egypt Gaza border"
# ]

url_set = []
# Load the CNN search page
for query in keywords:
    print(f'Starting to search for the keyword: "{query}"')
    i = 0
    while True:
        i += 1
        url = f'https://www.cnn.com/search?q={query}&from={i * 90}&size=90&sort=newest&types=all&section='
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "container__field-links"))
            )
        except:
            print("Timeout or no content available. Exiting loop.")
            break
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        link_container = soup.find("div", class_="container__field-links container_list-images-with-description__field-links")
        
        if link_container:
            results = link_container.find_all('a', href=True)
            links = [link.get('href') for link in results if 'index.html' in link.get('href')]
            url_set.extend(links)
        else:
            break

driver.quit()
print(f"Got {len(url_set)} urls BEFORE removing duplicates")
links_list = list(set(url_set))
print(f"Got {len(links_list)} urls AFTER removing duplicates")
# with open('urls.txt', 'w') as f:
#     for url in links_list:
#         f.write(f"{url}\n")
data = {
    "cnn.com": links_list
}
with open('data/news-data.json', 'w') as f:
    json.dump(data, f, indent=4)