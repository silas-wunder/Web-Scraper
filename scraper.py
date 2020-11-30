from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

# runs the selenium headless
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")

# the search page to look at
url = "https://www.microcenter.com/search/search_results.aspx?N=4294966937+4294808776+4294808774+4294808740&NTK=all&sortby=match&rpp=96"

# actually grabs the page html
driver = webdriver.Firefox(options=options)
driver.get(url)

# grabs all the products from search, each product is part of 'product-wrapper'
soup = BeautifulSoup(driver.page_source, 'html.parser')
cards = soup.find_all('li', class_='product_wrapper')

# holds all cards in stock, if any
cards_in_stock = []

for card_listing in cards:
    stock_amount = card_listing.find('div', class_='stock').find('strong').text
    if stock_amount == '\nSold Out' or stock_amount == '\nNot Carried In This Store':
        cards_in_stock.append(card_listing)

if len(cards_in_stock) != 0:
    cards_formatted = {}
    for card in cards_in_stock:
        card_price = card.find('div', class_='price').text
        card_url = "microcenter.com" + card.find('div', class_='normal').find('a', href=True).get('href')
        card_name = card.find('div', class_='normal').text
        card_price = card_price.strip()
        card_url = card_url.strip()
        card_name = card_name.strip().title()
        cards_formatted[card_name] = (card_price, card_url)
    

driver.quit()