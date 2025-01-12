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
i=1
try:

    rec = []
    for i in range(11):
        driver.get(f"https://www.nytimes.com/news-event/israel-hamas-gaza?page={i}")
        
        comparison_date = datetime(2023, 10, 7)
        
        

        # method : get relevant URLs, then click on "SHOW MORE"
        
        while True:
            
            html = driver.page_source
            
            soup = BeautifulSoup(html,"html.parser")

            results = list(soup.find_all("a",{'class': 'css-8hzhxf'}))
            
            curr = 0
            with open("resultsNYT.txt","a") as f:
                curr = len(results)
                for article in results:
                        date_pattern = r"(\d{4}/\d{2}/\d{2})"
                        match = re.search(date_pattern, article.attrs["href"])
                        if match:
                            date_str = match.group(0)
                            try:
                                # Parse the date as YYYY/MM/DD
                                is_date = datetime.strptime(date_str, "%Y/%m/%d") > comparison_date
                                if(is_date and r"\b(" + "|".join(re.escape(keyword) for keyword in keywords) + r")\b"):
                                    f.write(f"https://www.nytimes.com{article.attrs["href"]}\n")
                            except ValueError:
                                # In case of any parsing issues, return None
                                break
        
         
         
        #buttons = driver.find_elements(By.TAG_NAME,"button")
        #for button in buttons[:-1]:
            #if(button.get_attribute("data-testid")==f"pagination-next-button"):
            # take the last one 
                #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                #button.click()
        #i += 1    
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")    
            #sclt-loadmore{i} loadMor
            sleep(0.5)
            

            
            if(len(rec)<10):
                rec.append(curr)
            
            else:
                rec = rec[1:]
                rec.append(curr)
            
            sortie = True
            for i in range(len(rec)-1):
                if(rec[i] != rec[i+1]):
                    sortie = False

            print(rec)
            if(sortie):
                break
        #r"(\d{4}-\d{2}-\d{2})"
    
    


except KeyboardInterrupt:
    driver.close()



#elem = driver.find_element(By.CLASS_NAME, "u-clickable-card__link")
#print(elem)