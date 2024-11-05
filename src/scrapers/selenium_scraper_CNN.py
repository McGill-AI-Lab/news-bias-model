from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

#! THIS CODE ONLY GETS URLS

# Set up the Selenium WebDriver (you need to have ChromeDriver installed for Chrome)
driver = webdriver.Chrome()  # or webdriver.Firefox() for Firefox
query = 'palestine'
url_set = []
i = 0
# Load the CNN search page
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
print(url_set)

links_list = list(set(url_set))
with open('urls.txt', 'w') as f:
    for url in links_list:
        f.write(f"{url}\n")
