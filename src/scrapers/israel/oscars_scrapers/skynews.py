from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
import re


driver = webdriver.Firefox()
i=1
try:

    rec = []
    for i in range(11):
        url='https://www.google.com/search?q=palestine+israel+gaza+conflict+site:news.sky.com&ie=utf-8&oe=utf-8&num=10'
        driver.get(url)
        
        comparison_date = datetime(2023, 10, 7)

        # method : get relevant URLs, then click on "SHOW MORE"
        
        while True:
            
            html = driver.page_source
            
            g=0
            Data = [ ]
            l={}

            soup = BeautifulSoup(html, "html.parser")

            allData = soup.find_all("div",{"class":"g"})

            with open("resultsSKY.txt","a") as f:
                for i in range(0,len(allData)):
                                link = allData[i].find('a').get('href')

                                if(link is not None):
                                    if(link.find('https') != -1 and link.find('http') == 0 and link.find('aclk') == -1):
                                        g=g+1
                                        l["link"]=link
                                        f.write(link)
                                        try:
                                            l["title"]=allData[i].find('h3',{"class":"DKV0Md"}).text
                                        except:
                                            l["title"]=None

                                        try:
                                            l["description"]=allData[i].find("div",{"class":"VwiC3b"}).text
                                        except:
                                            l["description"]=None

                                        l["position"]=g

                                        Data.append(l)

                                        l={}

                                    else:
                                        continue

                                else:
                                    continue

            curr = 0
            """
            with open("resultsSKY.txt","a") as f:
                curr = len(results)
                for article in results:
                        if("href" not in article.attrs.keys()):
                            continue
                        date_pattern = r"(\d{4}/\d{2}/\d{2})"
                        match = re.search(date_pattern, article.attrs["href"])
                        #if match:
                            #date_str = match.group(0)
                        try:
                                url = article.attrs["href"]
                                print(url)
                                # Parse the date as YYYY/MM/DD
                                #is_date = datetime.strptime(date_str, "%Y/%m/%d") > comparison_date
                                #if(is_date and r"\b(" + "|".join(re.escape(keyword) for keyword in keywords) + r")\b"):
                                f.write(f"https://news.sky.com{url}\n")
                        except ValueError:
                                # In case of any parsing issues, return None
                                break
        
         
         """
        #buttons = driver.find_elements(By.TAG_NAME,"button")
        #for button in buttons[:-1]:
            #if(button.get_attribute("data-testid")==f"pagination-next-button"):
            # take the last one 
                #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                #button.click()
        #i += 1    
            # search eleemnts by id 
            next_button = driver.find_element(By.ID, "pnnext")
            next_button.click()
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")    
            #sclt-loadmore{i} loadMor
            sleep(2)
            
        #r"(\d{4}-\d{2}-\d{2})"
    
    


except KeyboardInterrupt:
    driver.close()



#elem = driver.find_element(By.CLASS_NAME, "u-clickable-card__link")
#print(elem)

