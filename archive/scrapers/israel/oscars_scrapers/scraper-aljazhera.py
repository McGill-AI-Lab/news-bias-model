from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
import re


BUTTON_CLASSNAME = "show-more-button big-margin"

keywords = [
    "Israel", 
    "Gaza", 
    "Jerusalem", 
    "IDF", 
    "Hamas", 
    "Palestine", 
]

driver = webdriver.Firefox()
i = 0
try:

    driver.get("https://www.aljazeera.com/tag/israel-palestine-conflict/")
    
    comparison_date = datetime(2023, 10, 7)
    
    

    # method : get relevant URLs, then click on "SHOW MORE"
    
    while True:
        
        html = driver.page_source
        
        soup = BeautifulSoup(html,"html.parser")

        results = list(soup.find_all("a",{'class': 'u-clickable-card__link'}))
        
        
        with open("resultsAL.txt","a+") as f:
            print("articles : ",len(list(soup.find_all("a",{'class': 'u-clickable-card__link'}))))
            for article in results:
                    date_pattern = r"(\d{4}/\d{2}/\d{2})"
                    match = re.search(date_pattern, article.attrs["href"])
                    if match:
                        date_str = match.group(0)
                        try:
                            # Parse the date as YYYY/MM/DD
                            is_date = datetime.strptime(date_str, "%Y/%m/%d") > comparison_date
                            if(is_date and r"\b(" + "|".join(re.escape(keyword) for keyword in keywords) + r")\b"):
                                f.write(f"https://www.aljazeera.com{article.attrs["href"]}\n")
                        except ValueError:
                            # In case of any parsing issues, return None
                            break
                
        

        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            element = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "show-more-button")))
            button = driver.find_element(By.CLASS_NAME, "show-more-button")
            driver.execute_script("arguments[0].scrollIntoView();", button)
            #element = WebDriverWait(driver, 20).until(EC.visibility_of_element_located(button))
            element = WebDriverWait(driver, 2).until(EC.element_to_be_clickable(button))
            
            sleep(0.4)
            try:
                button.click()
            except:
                driver.execute_script("arguments[0].click();", button)
        except: 
            continue
            
        sleep(0.5)
        
        #r"(\d{4}-\d{2}-\d{2})"

    
    


except KeyboardInterrupt:
    driver.close()



#elem = driver.find_element(By.CLASS_NAME, "u-clickable-card__link")
#print(elem)