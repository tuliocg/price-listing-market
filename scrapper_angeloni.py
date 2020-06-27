#stantard imports
import os
import time
from datetime import date

#third party imports
import requests
from bs4 import BeautifulSoup
import pandas as pd


class Scrapper():
    #angeloni URL sorted low to high price, 48 items/page
    today = date.today()
    base_url = [
        "https://www.angeloni.com.br/super/c?No=",
        "&Nrpp=48&Ns=dim.product.inStock|1||sku.activePrice|0"
    ]

    def __init__(self, supermarket='angeloni', index=0):
        self.supermarket = supermarket
        self.index = index
        self.response = 200


    def _get_item_information(self):
        df = pd.DataFrame(columns=[
            'insert_date',
            'market_name',
            'product_description',
            'product_price',
            'product_availability'
        ])
        #for i in range(200):
        while self.response == 200:
            page = requests.get(
                "{}{}{}".format(
                    self.base_url[0],
                    str(self.index),
                    self.base_url[1]
                )
            )
            soup = BeautifulSoup(page.content, 'html.parser')
            elements = soup.find_all(class_='box-produto')
            if not elements:
                self.response = 404
            for element in elements:
                item_desc = element.find('h2', class_='box-produto__desc-prod')
                item_preco_int = element.find('span', class_='box-produto__preco__valor')
                item_preco_dec = element.find('span', class_='box-produto__preco__centavos')
                if not item_preco_int:
                    disponibilidade = 0
                    item_preco = 0
                else:
                    disponibilidade = 1
                    item_preco = '{}{}'.format(
                        item_preco_int.text,
                        item_preco_dec.text
                    )
                new_row = {
                    'insert_date': self.today.strftime('%m-%d-%Y'),
                    'market_name': self.supermarket,
                    'product_description': item_desc.text,
                    'product_price': item_preco,
                    'product_availability': disponibilidade
                }
                df = df.append(new_row, ignore_index=True)
            df.to_csv('{}_data.csv'.format(self.supermarket))
            self.index = self.index + 48
        print('Extraction {} data finished without errors!'.format(self.supermarket))

if __name__ == '__main__':
    scrapper_item = Scrapper()
    scrapper_item._get_item_information()
