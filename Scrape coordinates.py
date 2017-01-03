import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import re
import time
import csv

zips = pd.read_csv('Wisc Zips.csv')['Zip Code']
writefile = 'test-Wisconsin_lat_long.csv'

session = requests.session()
pattern = re.compile(r'YPU = (.*?);')

def get_yp_url(zipcode, page):
    url = 'http://www.yellowpages.com/search?search_terms=taverns&geo_location_terms={}&page={}'
    return url.format(int(zipcode), page)

def get_coords_from_javascript(scripts):
    '''
    :param scripts: list of javascript blocks from webpage
    :return: dictionary of geographic coordinates
    '''
    locs=[]
    for script in scripts:
        if len(pattern.findall(str(script.string))) == 1:
            data = pattern.findall(str(script.string))
            down = json.loads(data[0])
            try:
                locs = down['expandedMapListings']
                if len(locs) ==0: break
            except:
                break
    return locs

with open(writefile, 'w') as f1:
    writer = csv.writer(f1, delimiter=',', lineterminator='\n')
    for zipcode in zips:
        for page in range(1,30):
            url = get_yp_url(zipcode, page)
            print(url)

            s = session.get(url)
            soup = BeautifulSoup(s.text, 'lxml')

            # Get all javascript blocks from page
            scripts = soup.findAll('script')

            locs = get_coords_from_javascript(scripts)

            if len(locs) == 0: break

            for loc in locs:
                writer.writerow([loc['name'],loc['zip'],loc['latitude'], loc['longitude']])
                print(loc['name'],loc['zip'],loc['latitude'], loc['longitude'])

            print('{}------------------{}'.format(zipcode, page))
            time.sleep(2)