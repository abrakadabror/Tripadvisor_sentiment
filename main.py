import pandas as pd
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from textblob import TextBlob

import time
from bs4 import BeautifulSoup

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://www.tripadvisor.com/Attraction_Review-g14134359-d14951238-Reviews-TeamLab_Planets_TOKYO-Toyosu_Koto_Tokyo_Tokyo_Prefecture_Kanto.html')
time.sleep(7)



# driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]').click() # inny zapis tego co wyzej

PAGE_AMOUT = 5 # jęsli jest stała i chcemy zazaczyć, ze ona sie zmieni to piszemy i Snake Case
reviews = []# tu bedziemy trzmac wszystkie opinie                   # Linter to program , ktory dba o jakosc kodu
page = [] # tu trzymamy numer strony na ktorej została odnaleziona opinia
przycisk_zaakceptuj = driver.find_element(By.ID,'onetrust-accept-btn-handler') 
przycisk_zaakceptuj.click()
for i in range(PAGE_AMOUT):
    reviews_on_single_page = []
    more_buttons = driver.find_elements(By.CLASS_NAME, 'CECjK')
    #print(more_buttons)

    print(len(more_buttons))#ile znalazło przycisków do rozwiniecia
    for j in range(len(more_buttons)): #przejdziemy przez wszystkie przyciki do rozwiniecia
        if more_buttons[j].is_displayed():# sprwdzamy czy przycisk more_buttons jest pokazany
            driver.execute_script('arguments[0].click();', more_buttons[j]) #metoda ktora wykorzystuje to, ze juz mamy odnaleziony element i JavaScript w niego kliknie, uzywajac execute script mozemy wykonac

    page_source = driver.page_source # to co tu robimy to bierzemy to jak strona po przekliaknaniu przez selenium jako page_source
    soup = BeautifulSoup(page_source, 'html.parser') # do bs4 podajemy nasza rozwinieta strone jako obiekt do scrapowania
    reviews_selector = soup.find_all('div', class_= 'biGQs _P pZUbB KxBGd')
    for review_selector in reviews_selector:
        review_span = review_selector.find('span', class_= 'yCeTE')
        #print(review_span)
        if review_span is None:
            continue# jesli nie znaleźlismy spana z komenatrzem to przejdziemy do nastepnego elementu
        review = review_span.get_text(strip = True)
        reviews_on_single_page.append(review)
    # print(len(reviews_on_single_page))
    reviews_amout = len(reviews_on_single_page)
    page_ids = [i +1]* reviews_amout # tworztmy liste cyfr, lista ma taka dlugosc jak reviews_amount
    reviews.extend(reviews_on_single_page) 
    page.extend(page_ids)
    time.sleep(2)
    przycisk_strona = driver.find_element(By.XPATH, '//*[@id="tab-data-qa-reviews-0"]/div/div[5]/div/div[11]/div[1]/div/div[1]/div[2]/div/a')
    actions = ActionChains(driver) #definiujemy, ze wydarzy sie jais ciag zdarzen/ tworzymi liste zadan
    actions.move_to_element(przycisk_strona) #w naszym zadaniu jest to tlko jedno zdarzene czyli move_to_element, zjedziemy do elementu / dopisujemy zadania do listy
    actions.perform()
    przycisk_strona.click()
    time.sleep(3)
driver.quit()
#print(len(page))

data = {'ID': page, 'Comment': reviews } # id 1 kolumna i w komentarzu recenzja
df = pd.DataFrame(data)
print(df.head(50))

#

def analyze_text(text):
    blob = TextBlob(text) # rozdziela text na pasujace skrawki
    sentiment = blob.sentiment.polarity # ktoś zrobił funkcje jak sentiment.polarity i aplikujey je na nasz tekst
    if sentiment > 0: 
        return 'Positive'
    elif sentiment < 0:
        return 'Netagive'
    else:
        return 'Neutral'
df['Sentiment'] = df['Comment'].apply(analyze_text)

print(df.head(50))
df.to_excel('baza_danych.xlsx', index = False)

conn = sqlite3.connect('comments.sqlite')

df.to_sql('CommentsTable', conn, if_exists='append', index = False)

conn.close()

print('end')