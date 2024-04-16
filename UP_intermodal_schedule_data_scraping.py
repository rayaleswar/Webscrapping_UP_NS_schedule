from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import time

s = Service('C:/Users/royal/Downloads/chromedriver-win64/chromedriver.exe')
chromeOptions = Options()
chromeOptions.headless = False
chromeOptions.add_experimental_option ('excludeSwitches', ['enable-logging'])
chromeOptions.add_argument ('--log-level=3')
chromeOptions.add_argument("user-agent=whatever you want")
driver = webdriver.Chrome(service = s, options= chromeOptions)

driver.get("https://c02.my.uprr.com/fpa/intermodal-schedules/")    
# print("It works Before the driver call")
submit_button = driver.find_element(By.XPATH,"//html/body/app-root/app-temp-up-wrapper/div/div/div[2]/div/div/share-home/div/div/div/div[1]/share-search-criteria/form/div[2]/div/button[2]")
submit_button.click()
time.sleep(10)
# print("\n\nIt works after the driver call")

response=driver.page_source.encode('utf-8').strip()
soup = BeautifulSoup(response,'html5lib')
strdiv = soup.find('div', class_= 'mat-typography')
strddiv = strdiv.find('div', class_='mdc-layout-grid__inner')
ssr = strddiv.find("share-search-results", attrs={"_ngcontent-mkv-c43": "", "_nghost-mkv-c42": ""})
mat = ssr.find_all('mat-card', attrs={'_ngcontent-mkv-c42': '', 'class':"mat-card mat-focus-indicator ng-star-inserted"})

final_df = pd.DataFrame(columns=['Origin_Terminal', 'Destination_Terminal', 'CutOff_Day', 'CutOff_Time', 'Available_Day', 'Available_Time', 'Origin_Capabilities', 'Destination_Capabilities', 'Company', 'Route_Type', 'Transit_Time',  'Equipment_Type'])

for m in mat: 
    route = m.find_all('div', attrs={'div _ngcontent-mkv-c42':"", 'class':"header-element"})[0].text
    container = m.find_all('div', attrs={'div _ngcontent-mkv-c42':"", 'class':"header-element"})[1].text
    origin = m.find('span', attrs={'_ngcontent-mkv-c42':"", 'class':"no-wrap mat-body-1"}).text
    destination = m.find('span', attrs={'_ngcontent-mkv-c42':"", 'class':"ellipsis mat-body-1"}).text

    table = m.find("div", class_="table-container")

    date = []

    for child in table.find_all(recursive=False):
        col = child.find_all(recursive=False)
        row = []
        for c in col:
            row.append(c.text)
        date.append(row)

    df = pd.DataFrame(date)

    df = df.T
    df.rename(columns=df.iloc[0], inplace = True)
    df.drop(df.index[0], inplace = True)

    df['CutOff_Day'] = df['Drop off by'].astype('str').str[:4]
    df['CutOff_Time'] = df['Drop off by'].astype('str').str[-5:]
    df['Available_Day'] = df['Available'].astype('str').str[:4]
    df['Available_Time'] = df['Available'].astype('str').str[-5:]
    df['Transit_Time'] = df[' Transit time Average90th percentileSubject to change']
    df['Origin_Terminal'] = origin
    df['Destination_Terminal'] = destination
    df['Company'] = 'UP'
    df['Origin_Capabilities'] = ' '
    df['Destination_Capabilities'] = ' '
    df['Route_Type'] = route
    df['Equipment_Type'] = container
    df = df[['Origin_Terminal', 'Destination_Terminal', 'CutOff_Day', 'CutOff_Time', 'Available_Day', 'Available_Time', 'Origin_Capabilities', 'Destination_Capabilities', 'Company', 'Route_Type', 'Transit_Time',  'Equipment_Type']]
    final_df = final_df.merge(df, on=['Origin_Terminal', 'Destination_Terminal', 'CutOff_Day', 'CutOff_Time', 'Available_Day', 'Available_Time', 'Origin_Capabilities', 'Destination_Capabilities', 'Company', 'Route_Type', 'Transit_Time',  'Equipment_Type'], how='outer')

print(f'shape of the dataframe {final_df.shape}')
# final_df.head()

final_df.to_csv('C:/Users/royal/Downloads/webscrapping/up_trains.csv', index=False)
driver.quit()