#stantard imports
import time
import os
import time
from datetime import date
import re

#third party imports
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class Scrapper():

    def __init__(self, supermarket='not-defined', index=0):
        self.supermarket = supermarket
        self.index = index
        self.response = 200


    def _get_item_information(self):
        today = date.today()
        base_url = ['https://www.clubeextra.com.br/secoes/','?qt=12&p=0&gt=list']
        driver = webdriver.Firefox()
        df_mapping = pd.read_csv('extra_mapping.csv')

        for section in df_mapping['section']:
            df = pd.DataFrame(columns=[ 'insert_date',
                'market_name',
                'section',
                'brand',
                'product_description',
                'product_price',
                'product_price_reals',
                'product_price_cents'
            ])
            section_name = section.split('/')[1]

            driver.get("{}{}{}".format(
                base_url[0],
                section,
                base_url[1]
            ))
            timeout = 6
            try:
                WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, 'filter ng-binding ng-scope')))
            except TimeoutException:
                print("Timed out waiting for page to load")
            finally:
                print("Page loaded")

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            total_items = int(re.findall(r"\d+", str(soup.find_all("p", {'class': "filter ng-binding ng-scope"})))[2])
            print('Total items in this page is: {}'.format(total_items))
            for i in range(0,(int(total_items/12)+2)):
            #for i in range(0,5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                soup = BeautifulSoup(driver.page_source, "html.parser")
                item_name = soup.find_all("p", {'class': "product-description ng-binding"})
                item_price = soup.find_all("p", {'class': "normal-price ng-binding ng-scope"})
                for name, price in zip(item_name, item_price):
                    name_txt = name.get_text().strip()
                    brand = ' '.join(re.findall(r"[A-Z]{2,}", name_txt))
                    price_txt = price.get_text().strip()
                    price_cents = int(price_txt.split(',')[1])
                    price_reals = int(price_txt.replace('.','').split(',')[0].split(' ')[1])
                    new_row = {
                        'insert_date': today.strftime('%m-%d-%Y'),
                        'market_name': self.supermarket,
                        'section': section_name,
                        'brand': brand,
                        'product_description': name_txt,
                        'product_price': price_txt,
                        'product_price_reals': price_reals,
                        'product_price_cents': price_cents
                    }
                    df = df.append(new_row, ignore_index=True)
            df = df.drop_duplicates(['product_description'])
            df.to_csv('{}_data.csv'.format(self.supermarket), mode='a')
            print('Extraction of section {} for {} finished without errors!'.format(section_name, self.supermarket))
        print('Extraction for {} finished without errors!'.format(self.supermarket))

if __name__ == '__main__':
    scrapper_item = Scrapper('extra', 0)
    scrapper_item._get_item_information()
