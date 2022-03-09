import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
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
        if len(location) == 2:
            full_street = location[0]
            street = re.sub(r'\d+', '', full_street).strip()
            district = location[1]
            house_number = re.findall('\d+', full_street)[0]
        else:
            district = location[0]
            street = ''
            house_number = ""

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
        "Straße": street,
        "Hausnummer": house_number,
        "Stadtteil": district,
        "Beschreibung": description
    }

def get_flat_data(page_result):
    flat_list = []
    for flat in page_result.select('div[class*="EstateItem"]'):
        try:
            flat_data = extract_flat_details(flat)
        except Exception as err:
            print('Oh no, there is an error...:', err)
            continue
        print(flat_data)
        flat_list.append(flat_data)
    return flat_list

if __name__ == '__main__':
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    url = 'https://www.immowelt.de/liste/duisburg/wohnungen/mieten?sort=relevanz'
    page = requests.get(url=url, headers=headers)
    session = HTMLSession()
    r = session.get(url)
    r.html.render()

    page_result = BeautifulSoup(r.html.raw_html, 'html.parser')
    sub_pages_count = page_result.select('button[class*="navNumberButton"]')
    for count in range(6, int(sub_pages_count[-1].text)):
        sub_page_URL = flatListURL + str(count)
        print(sub_page_URL)
        sub_page = session.get(sub_page_URL)
        sub_page.html.render()
        sub_page_result = BeautifulSoup(sub_page.html.raw_html, 'html.parser')
        get_flat_data(sub_page_result)


    #immoPyDB.insert_many(flats)
