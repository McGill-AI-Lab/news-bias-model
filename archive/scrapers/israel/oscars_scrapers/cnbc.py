from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
import re


keywords = [
    "Israel", 
    "Gaza", 
    "Jerusalem", 
    "IDF", 
    "Hamas", 
    "Palestine", 
]

driver = webdriver.Firefox()
try:

    driver.get("https://www.cnbc.com/search/?query=palestine%20israel%20gaza%20war%20conflict&qsearchterm=palestine%20israel%20gaza%20war%20conflict")
    
    comparison_date = datetime(2023, 10, 7)
    

    # method : get relevant URLs, then click on "SHOW MORE"
    
    i = 1
    
    sleep(5)
    while True:
        
        html = driver.page_source
        
        soup = BeautifulSoup(html,"html.parser")

        results = list(soup.find_all("a",{'class': 'resultlink'}))
        
        
        with open("resultsCNBC.txt","a") as f:
            print("articles : ",len(results))
            for article in results:
                if(r"\b(" + "|".join(re.escape(keyword) for keyword in keywords) + r")\b"):
                    if(article.attrs['href']!="/" and article.attrs['href']!="/sport" and article.attrs['href']!="/innovation" and article.attrs['href']!="/culture" and article.attrs['href']!="/arts" and article.attrs['href']!="/travel" and article.attrs['href']!="/future-planet" and article.attrs['href']!="/video" and article.attrs['href']!="/live" and article.attrs['href']!="/sport" and article.attrs['href']!="/video" and article.attrs['href']!="/news" and article.attrs['href']!="/business"):
                        f.write(article.attrs["href"]+"\n")
         
         
        #buttons = driver.find_elements(By.TAG_NAME,"button")
        #for button in buttons[:-1]:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #if(button.get_attribute("data-testid")==f"pagination-next-button"):
            # take the last one 
                #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                #button.click()
        #i += 1        
        #sclt-loadmore{i} loadMor
        sleep(0.5)
        
        #r"(\d{4}-\d{2}-\d{2})"

    
    


except KeyboardInterrupt:
    driver.close()



#elem = driver.find_element(By.CLASS_NAME, "u-clickable-card__link")
#print(elem)