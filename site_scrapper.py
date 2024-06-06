import prod_url_getter
import time
import configparser
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as sel_ex

# Import config file
config = configparser.ConfigParser()
config.read("config.ini")

# Get list of product URLs
prod_url_map = prod_url_getter.parse_sitemap()

# Start webdriver session
srv = Service(executable_path=config["PATHS"]["webdriver"])
driver = webdriver.Chrome(service=srv)
wait = WebDriverWait(driver, 1)

prod_data = {}

# Get base page url and enter zip_code
driver.get(config["SOURCES"]["base_site"])
driver.maximize_window()
try:
        # Identify the zipcode entry box and input the value      
        zipcode_box = wait.until(lambda x: x.find_element(By.NAME, "postalCode"))
        zipcode_box.send_keys(config["PARAMETERS"]["zipcode"])
        zipcode_box.send_keys(Keys.ENTER)
        wait.until(EC.invisibility_of_element(zipcode_box)) # Wait until zipcode entry box dissapears.
except sel_ex.TimeoutException: 
    print("Some change has occured to the base website.")
    sys.exit("")

# Walk through items to get product data
for prod_key in [13568]:
        item_data = {}
        item_data['URL'] = prod_url_map[prod_key]
        driver.get(prod_url_map[prod_key])
        # Check if the item is missing, if so, continue to next item.
        try:
            missing_item_check = wait.until(lambda x: x.find_element(By.CLASS_NAME, "error-404__header"))
            if missing_item_check is not None:
                print("Missing Item")
                item_data['status'] = 'missing'
                prod_data[prod_key] = item_data
                continue
        # If item is not missing, get all relevant elements from webpage.
        except sel_ex.TimeoutException: 
            # Product Detail Section
            css_selectors = {'product_title':"div[class='private-product-detail__right'] > h1[class = 'title2-b private-product-detail__description']",
                             'product_format':"div[class='private-product-detail__right'] > div[class = 'product-format product-format__size']",
                             'category_1':"div[class='private-product-detail__header'] > a > span[class = 'subhead1-r']",
                             'category_2':"div[class='private-product-detail__header'] > a > span[class = 'subhead1-sb']",
                             'img_url':"div[class='image-zoomer__source'] > img"}
                              
            product_title = wait.until(lambda x: x.find_element(By.CSS_SELECTOR, css_selectors['product_title'])).text
            product_format = driver.find_element(By.CSS_SELECTOR, css_selectors["product_format"]).find_elements(By.TAG_NAME, 'span')
            category_1 = driver.find_element(By.CSS_SELECTOR, css_selectors["category_1"]).text
            category_2 = driver.find_element(By.CSS_SELECTOR, css_selectors["category_2"]).text
            img_url = driver.find_element(By.CSS_SELECTOR, css_selectors["img_url"]).get_attribute('src')
            
            print(product_title)
            print(category_1)
            print(category_2)
            print(img_url)
            
            for e in product_format:
                 print(e.text)
            
            print("/n")
            
time.sleep(5)
driver.quit()


