from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# email stuff
port = 465
passfile = open("passfile.txt")
password = passfile.read()
passfile.close()
senderfile = open("sender.txt")
sender = senderfile.read()
senderfile.close()
recieverfile = open("reciever.txt")
reciever = recieverfile.read()
recieverfile.close()

# runs the selenium headless
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
options.add_argument("--log-level=3")

# the search page to look at
url = "https://www.microcenter.com/search/search_results.aspx?Ntk=all&sortby=match&N=4294966937+4294808776+4294808740+4294808774&myStore=true&storeid=181"

# actually grabs the page html
driver = webdriver.Chrome(options=options)
driver.get(url)

# grabs all the products from search, each product is part of 'product-wrapper'
soup = BeautifulSoup(driver.page_source, 'html.parser')
cards = soup.find_all('li', class_='product_wrapper')

# holds all cards in stock, if any
cards_in_stock = []

# add every In Stock card to list
for card_listing in cards:
    stock_amount = card_listing.find('div', class_='stock').text
    if stock_amount != '\nSOLD OUT at Denver Store\n':
        cards_in_stock.append(card_listing)

# if there are in stock cards, pull relevant info and send an email
if len(cards_in_stock) != 0:
    # email prep
    message = MIMEMultipart('alternative')
    message['Subject'] = "GPU(s) are in stock"
    message['From'] = sender
    message['To'] = reciever
    messageHTML = "<html>"

    # loop through each card and pull relevant information about the card
    for card in cards_in_stock:
        card_price = card.find('div', class_='price').text
        card_url = "microcenter.com" + \
            card.find('div', class_='normal').find('a', href=True).get('href')
        card_name = card.find('div', class_='normal').text
        card_price = card_price.strip()
        card_url = card_url.strip()
        card_name = card_name.strip().title()
        html = f"""
    <body>
        <p>
            <a href={card_url}>{card_name}</a>
            is avaiable for {card_price}
        </p>
    </body>"""
        messageHTML += html
    messageHTML += "\n</html>"
    message.attach(MIMEText(messageHTML, "html"))

    # send the email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, reciever, message.as_string())
    print(f"Cards found in stock, email sent at {datetime.now()}.")

else:
    print(f"No cards found, exiting at {datetime.now()}")

os.system(f'taskkill /f /im chrome.exe >nul')
os.system(f'taskkill /f /im chromedriver.exe >nul')
driver.quit()
print()
