# -*- coding: utf-8 -*-
"""
Web scraping a Vietnamese lottery's jackpot numbers

Scrapping done at 5:20pm CST 7/30/2020
"""
# Import libraries
import pandas as pd

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.keys import Keys

#%% Try using requests
# Problem: cannot open other Javascript pages, thus only get the most recent 8 numbers
url = "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-645"
page = requests.get(url)

soup = BeautifulSoup(page.content, 'html.parser')
# print(soup.prettify())

# the lottery numbers are stored in <td> tag, class 'day_so_ket_qua_v2'
all_td = soup.find_all('td')
# Get the <td> tags that contain the winnning numbers
td_win_num = [i for i in all_td if i.find(class_="day_so_ket_qua_v2")]
# Get the <td> tags that contain the draw number for timestamp
td_lot = [all_td[i] for i in range(1,len(all_td),3)]

# Reformat the winning number string into 6 different integers
win_num_formatted = [i.get_text().strip() for i in td_win_num]
win_num_formatted = [[int(s[i:(i+2)]) for i in range(0,len(s),2)] for s in win_num_formatted]

# Make a dictionary (key = lot number; value = winning number)
win_num = {key.get_text():value for (key,value) in zip(td_lot,win_num_formatted)}

#%% Use selenium to get more numbers
# Set up selenium
options = Options()
options.headless = True # turn off GUI
driver = webdriver.Chrome(options=options, executable_path="D:/chromedriver_win32/chromedriver.exe")
driver.get("https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/winning-number-645")

# Store the info about jackpot numbers in dictionary, key is lot, value is the number
win_num = {}
# page number
page_num = 0
while True:
    elem = driver.find_element_by_id("divResultContent")
    elem_text = elem.text.split('\n')
    
    # Only keep the lot number and winning number
    elem_text = [s for s in elem_text if len(s) > 5 and s[0].isnumeric()] # 5: the number of digits of the max page number
    
    # Stop after reaching last page
    if len(elem_text) == 0:
        break
    
    # Update result dictionary
    win_num.update({elem_text[i]:elem_text[i+1] for i in range(0,len(elem_text),2)})
    
    # Click next page
    page_num += 1
    driver.execute_script(f"javascript:NextPage({page_num})")

# Export the result dictionary
pd.Series(win_num).to_csv("winning_number.csv")
