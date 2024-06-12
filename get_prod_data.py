import prod_url_getter
import json
import requests
import time
import pprint as pp
from dataclasses import dataclass, field
from copy import deepcopy

# Import config file
with open("config.json") as f:
    config = json.load(f)

t_start = time.perf_counter()

@dataclass(order = True) 
class Product:
    id: int 
    ean: str 
    url: str 
    title: str 
    #wh_available: list[str] # what warehouses have the product available
    brand: str 
    packaging: str # product pack type. ie: bottle
    unit_size: float # total product unit weight
    pack_size: float # weight per pack
    pack_size_ref: str # what unit is pack/unit size in
    pack_units: float # number of packs in unit
    category_0: str 
    category_1: str
    category_2: str
    current_price: float # current price
    base_price: float # base price if discounted. if not = current_price
    bulk_price: float 
    bulk_ref: str
    thumbnail: str
    discount_percentage: float = field(init=False)

    def __post_init__(self):
        if self.base_price is None:
            self.base_price = self.current_price # Set base price = to current if there is no discount price.
        
        self.discount_percentage = round(1 - self.current_price/self.base_price, 3) # Calculate discount percentage
      
# Get list of product URLs
prod_id_list = prod_url_getter.parse_sitemap()
n_products = len(prod_id_list)
print(f'Total products to get: {n_products}')

output_storage = []

wait = 0
i = 0
while i < (n_products - 1):
    prod_key = prod_id_list[i]
    api_base_url = f'https://tienda.mercadona.es/api/products/{prod_key}/'
    
    if 0 > 1: # Test if ommiting stock calls is faster.
        av_warehouses = []

        # Check for stock availability
        for warehouse in config["PARAMETERS"]["warehouses"]:
            wh_req = requests.get(f'{api_base_url}?wh={warehouse}')
            if wh_req.status_code != 200:
                continue
            
            av_warehouses.append(warehouse)
        
    # Get product data and load into product instance
    try:
        prod_data_req = requests.get(api_base_url)
        prod_data = prod_data_req.json()
    except json.JSONDecodeError: # Catch empty or faulty jsons.
        print(f'Error in decoding JSON for product {prod_key}. Status code = {prod_data_req.status_code}')
        if prod_data_req.status_code == 410: # Remove product if empty page response.
            print(f'Removing product {prod_key}.')
            prod_id_list.remove(prod_key)
            n_products -= 1
        else:
            # We have another type of error and we move the product down the list.
            prod_id_list.append(prod_id_list.pop(prod_id_list.index(prod_key))) 
        
        continue

    def content_get(obj_call):
        try:
            return obj_call
        except KeyError:
            return None
    
    try:
        print(f'Current counter {i}: Product {prod_key}')

        current_product = Product(
            id = prod_data['id'],
            ean = content_get(prod_data['ean']),
            url = content_get(prod_data['share_url']),
            title = content_get(prod_data['display_name']),
            # wh_available = content_get(av_warehouses),
            brand = content_get(prod_data['details']['brand']),
            packaging = content_get(prod_data['packaging']),
            unit_size = content_get(prod_data['price_instructions']['unit_size']),
            pack_size = content_get(prod_data['price_instructions']['pack_size']),
            pack_size_ref = content_get(prod_data['price_instructions']['size_format']),
            pack_units = content_get(prod_data['price_instructions']['total_units']),
            category_0 = content_get(prod_data['categories'][0]['name']),
            category_1 = content_get(prod_data['categories'][0]['categories'][0]['name']),
            category_2 = content_get(prod_data['categories'][0]['categories'][0]['categories'][0]['name']),
            current_price = content_get(float(prod_data['price_instructions']['unit_price'])),
            base_price = content_get(prod_data['price_instructions']['previous_unit_price'] and float(prod_data['price_instructions']['previous_unit_price'])),
            bulk_price = content_get(prod_data['price_instructions']['reference_price']),
            bulk_ref = content_get(prod_data['price_instructions']['reference_format']),
            thumbnail = content_get(prod_data['photos'][0]['regular']))

    except KeyError: # The API returns a 200 instead of a 429 if too many requests are performed. Therefore we need to set a wait and retry.
        wait += 10
        print(f'Too many requests: wait {wait} seconds and move on to other product.')
        time.sleep(wait)
        prod_id_list.append(prod_id_list.pop(prod_id_list.index(prod_key)))
        continue
        
    wait = 0
    i += 1
    output_storage.append(deepcopy(current_product.__dict__))

t_end = time.perf_counter()#

with open('prod_data.json', 'wb') as f:
    f.write(output_storage)

print(f'Time elapsed: {t_end - t_start}')