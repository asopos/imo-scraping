import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re

client = MongoClient(host="localhost", port=2717)

detailURL = 'https://www.immowelt.de/expose/'
flatListURL = 'https://www.immowelt.de/liste/duisburg/wohnungen/mieten?d=true&sd=DESC&sf=RELEVANCE&sp='

immoPyDB = client.immoPy

def extract_flat_details(flat_soup):
    price = flat_soup.select_one('div[data-test="price"]').string
    qm = flat_soup.select_one('div[data-test="area"]').string
    rooms = flat_soup.select_one('div[data-test="rooms"]').string
    landlord = flat_soup.select_one('div[class*="ProviderName"]').string
    if flat_soup.find("i", text="location"):
        location = flat_soup.find("i", text="location").nextSibling.text.split(', ')
        street = location[0]
        district = location[1]

    else:
        location = ''
    if flat_soup.find("i", text="check"):
        description = flat_soup.find("i", text="check").nextSibling.text
    else:
        description = ''
    return {
        "Vermieter": landlord,
        "Preis": price.split(" ")[0],
        "Quadratmeter": qm.split(" ")[0],
        "Zimmer": rooms.split(" ")[0],
        "Straße": re.sub(r'\d+', '', street).strip(),
        "Hausnummer": re.findall('\d+', street)[0],
        "Stadtteil": district,
        "Beschreibung": description
    }

def get_flat_data(page_result):
    flat_list = []
    for flat in page_result.select('div[class*="EstateItem"]'):
        flat_data = extract_flat_details(flat)
        flat_list.append(flat_data)
    return flat_list


if __name__ == '__main__':
    url = 'https://www.immowelt.de/liste/duisburg/wohnungen/mieten?sort=relevanz'

    page = requests.get(url=url)
    page_result = BeautifulSoup(page.content, 'html.parser')
    #subPages = page_result.select_one('div[class*="Pagination-"]')

    flats = get_flat_data(page_result)
    print(flats)
    #immoPyDB.insert_many(flats)
