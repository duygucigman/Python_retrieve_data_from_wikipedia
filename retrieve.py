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
df.to_json(r'C:\Users\xxx\ExtractionWikifediaToJSON.json', orient='split' ,index=False)



#filtered Borough column for Not Assigned value
df_filtered = df[df.Borough!='Not assigned']

#convert Pstcode and Borough column to index data for using groupby function
df_filtered_index=df_filtered.set_index(['Postcode', 'Borough'])
df_filtered_index

#to do groupby by using Postcode and prepare Neigbourhood column like 'Lawrence Heights,Lawrence Manor'
df_filtered_groupby = df_filtered_index.groupby(level=['Postcode', 'Borough'], sort=False).agg( ','.join)
df_filtered_groupby

#Checking result with some examples
df_filtered_groupby.filter(like='M1R', axis=0)

df_filtered_groupby[df_filtered_groupby.Neighbourhood=='Not assigned']
df_filtered_groupby

#removing index
df_filtered_groupby=df_filtered_groupby.reset_index()
df_filtered_groupby

#Updating neigbourhood column if equals to Not assign with Borough value 
df_filtered_groupby["Neighbourhood"] = np.where(df_filtered_groupby["Neighbourhood"] == 'Not assigned', df_filtered_groupby['Borough'], df_filtered_groupby["Neighbourhood"])
df_filtered_groupby

#We printed that how many row data we have in dataframe by using .shape method
print('{} rows exist in dataframe'.format(df_filtered_groupby.shape[0]))

import geocoder # import geocoder

# initialize your variable to None
lat_lng_coords = None

# loop until you get the coordinates
while(lat_lng_coords is None):
  g = geocoder.google('{}, Toronto, Ontario'.format(postal_code))
  lat_lng_coords = g.latlng

latitude = lat_lng_coords[0]
longitude = lat_lng_coords[1]



#Having Geo data of Toronto from csv to dataframe
Toronto_geo_data = pd.read_csv(r'C:\Users\fuat\Desktop\IBM Coursera-Visualization with Python\assignment4-wikipedia\Geospatial_Coordinates.csv')
Toronto_geo_data.head()

#Merged 2 different tables (df_filtered_groupby , Toronto_geo_data)
df_filtered_groupby_merged=df_filtered_groupby
df_filtered_groupby_merged = df_filtered_groupby_merged.join(Toronto_geo_data.set_index('Postal Code'), on='Postcode')
df_filtered_groupby_merged


# set number of clusters
kclusters = 5

toronto_grouped_clustering2 = df_filtered_groupby_merged.drop(['Neighbourhood','Borough','Postcode'], 1)
toronto_grouped_clustering2

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(toronto_grouped_clustering2)

# check cluster labels generated for each row in the dataframe
kmeans.labels_[0:10]

address = 'Toronto'

geolocator = Nominatim(user_agent="Can_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Canada are {}, {}.'.format(latitude, longitude))


# create map of Toronto using latitude and longitude values
map_toronto = folium.Map(location=[latitude, longitude], zoom_start=8)

# add markers to map
for lat, lng, label in zip(df_filtered_groupby_merged['Latitude'], df_filtered_groupby_merged['Longitude'], df_filtered_groupby_merged['Neighbourhood']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_toronto)  
    
map_toronto

