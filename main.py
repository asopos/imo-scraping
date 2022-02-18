import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient(host="localhost", port=2717)

immoPyDB = client.immoPy

def extract_flat_details(flat_soup):
    price = flat_soup.select_one('div[data-test="price"]').string
    qm = flat_soup.select_one('div[data-test="area"]').string
    rooms = flat_soup.select_one('div[data-test="rooms"]').string
    landlord = flat_soup.select_one('div[class*="ProviderName"]').string
    features = flat_soup.select('div[class*="IconFact"]')
    location = features[0].findChildren('span')[0].get_text()
    description = features[1].findChildren('span')[0].get_text()
    return {
        "Vermieter": landlord,
        "Preis": price.split(" ")[0],
        "Quadratmeter": qm.split(" ")[0],
        "Zimmer": rooms.split(" ")[0],
        "Ort": location,
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
    flats = get_flat_data(page_result)
    immoPyDB.insert_many(flats)
