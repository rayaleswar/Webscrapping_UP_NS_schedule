from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

timewaits = [1,2,3,4,5]
final_df = pd.DataFrame(columns=['Origin_Terminal', 'Destination_Terminal', 'CutOff_Day', 'CutOff_Time', 'Available_Day', 'Available_Time', 'Origin_Capabilities', 'Destination_Capabilities', 'Company', 'Route_Type', 'Transit_Time',  'Equipment_Type'])

s = Service('C:/Users/royal/Downloads/chromedriver-win64/chromedriver.exe')
chromeOptions = Options()
chromeOptions.headless = False
chromeOptions.add_experimental_option ('excludeSwitches', ['enable-logging'])
chromeOptions.add_argument ('--log-level=3')
chromeOptions.add_argument("user-agent=whatever you want")
driver = webdriver.Chrome(service = s, options= chromeOptions)

driver.get("https://www.norfolksouthern.com/en/ship-by-rail/our-rail-network/intermodal-terminals-schedules")

stations = ["ALB", "APK", "ATL", "AUS", "AYE", "FEC", "BAL", "BET", "BRM", "BUF", "CSC", "CNC", "C47", "C63", "CAL", \
            "LAN", "CIN", "MPH", "COL", "CRX", "DEC", "LIV", "DEL", "EZP", "VIP", "GCT", "GBO", "GER", "HBG", "HUN", \
            "JAX", "VOL", "MIA", "MVL", "NIT", "NOL", "NOR", "PMA", "PIT", "ROS", "RUT", "GCY", "SHR", "STL", "TAY", "TOL", "WIT"]

for origin in stations:
    try:
        select_element = Select(driver.find_element(By.ID, "origin")) 
        select_element.select_by_value(origin)   
        for destination in stations:
            try:
                select_element = Select(driver.find_element(By.ID, "destination")) 
                select_element.select_by_value(destination)
                time.sleep(random.choice(timewaits))
                submit_button = driver.find_element(By.XPATH,"/html/body/div/div/div[1]/main/div/div/div/div/div[1]/div[3]/div/div[1]/form/div[3]/button")
                submit_button.click()
                response=driver.page_source.encode('utf-8').strip()
                soup = BeautifulSoup(response,'html5lib')               
                
                div = soup.find('div', class_ = 'intermodal-results')
                title = div.find_all('div', class_='panel')
                origin = title[0].find('h4', class_ = 'panel__title').text
                destination = title[1].find('h4', class_ = 'panel__title').text
                origin_cap = title[0].find('div', class_ = 'panel__capabilities').p.find("br").next_sibling.get_text(separator=" ").replace("\n", " ")
                dest_cap = title[1].find('div', class_ = 'panel__capabilities').p.find("br").next_sibling.get_text(separator=" ").replace("\n", " ")
                
                res = soup.find('div', class_ = 'intermodal-results__table')
                equip = res.find('h5', class_='result-table__title').text.split(" ")[-1]
                
                table = res.find('table')
                rows = table.find_all("tr")
                data = []
                for row in rows:
                    cells = row.find_all("td")
                    data.append([cell.get_text(separator=" ") for cell in cells])

                df = pd.DataFrame(data).T
                df.rename(columns=df.iloc[0], inplace = True)
                df.drop(df.index[0], inplace = True)
                df['CutOff_Day'] = df['Cutoff'].astype('str').str[:-5]
                df['CutOff_Time'] = df['Cutoff'].astype('str').str[-5:]
                df['Available_Day'] = df['Available'].astype('str').str[:-5]
                df['Available_Time'] = df['Available'].astype('str').str[-5:]
                df['Origin_Terminal'] = origin
                df['Destination_Terminal'] = destination
                df['Origin_Capabilities'] = origin_cap
                df['Destination_Capabilities'] = dest_cap
                df['Company'] = 'NS'
                df['Route_Type'] = ' '
                df['Transit_Time'] = ' '
                df['Equipment_Type'] = equip
                df = df[['Origin_Terminal', 'Destination_Terminal', 'CutOff_Day', 'CutOff_Time', 'Available_Day', 'Available_Time', 'Origin_Capabilities', 'Destination_Capabilities', 'Company', 'Route_Type', 'Transit_Time',  'Equipment_Type']]
                final_df = final_df.merge(df, on=['Origin_Terminal', 'Destination_Terminal', 'CutOff_Day', 'CutOff_Time', 'Available_Day', 'Available_Time', 'Origin_Capabilities', 'Destination_Capabilities', 'Company', 'Route_Type', 'Transit_Time',  'Equipment_Type'], how='outer')
                                
            except Exception as exc:
                continue
    except Exception as exc:
            continue
            
print(f'shape of the dataframe {final_df.shape}')
# final_df.head()

final_df.to_csv('C:/Users/royal/Downloads/webscrapping/ns_trains.csv', index=False)
driver.quit()