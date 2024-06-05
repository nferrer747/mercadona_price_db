import prod_url_getter
import time
import configparser
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
    print("Element Not Found")

for prod_key in list(prod_url_map.keys())[0:10]:
        driver.get(prod_url_map[prod_key])
        # Check if the item is missing, if so, pass to next item.
        try:
            missing_item_check = wait.until(lambda x: x.find_element(By.CLASS_NAME, "error-404__header"))
            if missing_item_check is not None:
                print("Missing Item")
                continue
        except sel_ex.TimeoutException: 
            print("Found item!")

time.sleep(10)
driver.quit()

