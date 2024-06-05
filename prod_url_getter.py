import requests
import xml.etree.ElementTree as ET
import re
import configparser
import os

# Import config file
config = configparser.ConfigParser()
config.read("config.ini")

# Read sitemap url
sitemap_url = config["SOURCES"]["sitemap"]

# Define function to parse url
def read_parse_xml(path):
  resp = requests.get(path)

  with open('file.xml', 'wb') as f:
          f.write(resp.content)

  tree = ET.parse('file.xml')
  root = tree.getroot()
  return root

# Parse sitemap
def parse_sitemap():
    sitemap = read_parse_xml(sitemap_url)

    url_map = {} # hashmap to store ids and links
    p = re.compile('/product/[0-9]+') # regex to match product urls

    # Loop through all product URLs
    i = 0
    while True:
        try:
            prod_url = sitemap[i][0].text
            m = p.search(prod_url)
            if m is not None:
                prod_id = int(m.group()[9:])
                url_map[prod_id] = prod_url
        except IndexError:
            break

        i += 1
    
    os.remove('file.xml')
    return url_map
