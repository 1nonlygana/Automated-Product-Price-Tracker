import requests
from bs4 import BeautifulSoup
import smtplib# Email library for sending alerts
import time
import csv
from datetime import datetime

# Configuration
PRODUCTS = [
    {
        "name": "PlayStation 5",
        "url": "https://amzn.in/d/cd8MIBi",
        "threshold": 58000.00,
        "website": "amazon.in"
    },
    {
        "name": "tshirt",
        "url": "https://www.amazon.in/dp/B06Y2CH63N?psc=1&ref_=cm_sw_r_cp_ud_ct_FC6GJ7GZDMCDV3MA9QXP",#current price 629.1
        "threshold": 800.00,
        "website": "amazon.in"
    }
]
CHECK_EVERY = 10  # Check every 10 seconds
EMAIL = "brodyop03@gmail.com"
PASSWORD = "nxjjrcmqlrlqhaag" 
HISTORY_FILE = "price_history.csv"# File to log price history

def get_price(product):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        page = requests.get(product['url'], headers=headers)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, 'html.parser')

        if product['website'] == "amazon.in":
            price_whole_elem = soup.find("span", class_="a-price-whole")
            price_fraction_elem = soup.find("span", class_="a-price-fraction")
            if price_whole_elem and price_fraction_elem:
                price_whole = price_whole_elem.get_text().replace(',', '')
                price_fraction = price_fraction_elem.get_text()
                return float(price_whole + price_fraction)
            else:
                print(f"Could not find price elements for {product['name']}")
                return None
        elif product['website'] == "amazon.in":
            price_elem = soup.find("div", class_="priceView-hero-price")
            if price_elem:
                price = price_elem.find("span").get_text()
                return float(price.replace('Rs.', '').replace(',', ''))
            else:
                print(f"Could not find price element for {product['name']}")
                return None

    except Exception as e:
        print(f"Error getting price for {product['name']}: {e}")
        return None
    

## Function to log price history
def log_price(product, price):
    try:
        with open(HISTORY_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                product['name'],
                price,
                product['url']
            ])
    except Exception as e:
        print(f"Error logging price: {e}")
## Function to send email alert
def send_alert(product, price):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()# Connect to the server
        server.starttls()#upgrades the connection
        server.login(EMAIL, PASSWORD)

        subject = f"Price Alert: {product['name']} dropped to Rs.{price}!"
        body = (
            f"Product: {product['name']}\n"
            f"Current Price: Rs.{price}\n"
            f"Your Threshold: Rs.{product['threshold']}\n"
            f"Link: {product['url']}"
        )
        
        server.sendmail(EMAIL, EMAIL, f"Subject: {subject}\n\n{body}")
        print(f"Alert sent for {product['name']}!")
        server.quit()
    except Exception as e:
        print(f"Error sending alert: {e}")
## Main function to track prices
def track_prices():
    print("Starting price tracker... Press Ctrl+C to stop")
    print("current time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Checking products every", CHECK_EVERY, "seconds")
    print("Products to track:")
    for product in PRODUCTS:
        print(f"- {product['name']} (Threshold: Rs.{product['threshold']})")
        print(f"  Current price: Rs.{get_price(product)}")

    
    # Create history file header if it doesn't exist
    try:
        with open(HISTORY_FILE, 'x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Product", "Price", "URL"])
    except FileExistsError:
        pass
    
    while True:
        for product in PRODUCTS:
            print(f"Checking {product['name']}...")
            current_price = get_price(product)
            
            if current_price is None:
                continue
                
            print(f"Current price: Rs.{current_price}")
            log_price(product, current_price)
            
            if current_price <= product['threshold']:
                send_alert(product, current_price)
        
        print(f"Waiting {CHECK_EVERY//3600} hour(s) before next check...")
        time.sleep(CHECK_EVERY)
# Continuous monitoring
if __name__ == "__main__":
    track_prices()
