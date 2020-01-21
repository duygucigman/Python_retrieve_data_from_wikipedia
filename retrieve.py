#importing required libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd


#retrieving data from wikipedia
URL='https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M'
response =requests.get(URL)
soup=BeautifulSoup(response.text, 'html.parser')
table = soup.find('table',{'class':'wikitable sortable'}).tbody

#converting the data to dataframe
rows =table.find_all('tr')
columns =[v.text.replace('\n','') for v in rows[0].find_all('th')]

df = pd.DataFrame(columns=columns)

for i in range(1,len(rows)):
    tds = rows[i].find_all('td')
    
    if len(tds)==4:
       values=[tds[0].text , tds[1].text,'' , tds[2].text,'' ,tds[3].text.replace('\n','').replace('\xa0','')]
    else:
        values= [td.text.replace('\n', '').replace('\xa0','') for td in tds]
    
    df=df.append(pd.Series(values, index=columns), ignore_index=True)

#convert dataframe to json
df.to_json(r'C:\Users\fuat\ExtractionWikifediaToJSON.json2', orient='split' ,index=False)
