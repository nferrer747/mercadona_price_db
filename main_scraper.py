import pandas as pd
import api_scraper
from datetime import date

# Scrape data and store in df
prod_data_df = api_scraper.scrape_data()
prod_data_df.reset_index()

# Insert scraping date
prod_data_df['date'] = date.today()

# Code for inserting table into BQ Dataset
pass
