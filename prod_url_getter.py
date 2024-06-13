import requests
import xml.etree.ElementTree as ET
import re
import json
import os

# Import config file
with open("config.json") as f:
    config = json.load(f)

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

    prod_id_list = [] # list to store product_ids
    p = re.compile('/product/[0-9]+') # regex to match product urls

    # Loop through all product URLs
    i = 0
    while True:
        try:
            prod_url = sitemap[i][0].text
            m = p.search(prod_url)
            if m is not None:
                prod_id_list.append(int(m.group()[9:]))
        except IndexError:
            break

        i += 1
    
    os.remove('file.xml')
    
    # Remove any duplicate keys.
    prod_id_list = list(set(prod_id_list))
    return prod_id_list
