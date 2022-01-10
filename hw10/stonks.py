import concurrent.futures
import json
import random
import re
import time
import xml.etree.ElementTree as ElementTree
from itertools import chain
from math import ceil
from typing import Tuple

import requests
from bs4 import BeautifulSoup, element
from pydantic import BaseModel

session = requests.Session()


def retry(attempts=5):
    def _retry_atemmpt(func):
        def wrapper(*args, **kwargs):
            nonlocal attempts
            result = func(*args, **kwargs)
            while attempts != 0:
                if result.status_code != 200:
                    time.sleep(0.3 + random.uniform(0.5, 1))
                    attempts -= 1
                    result = func(*args, **kwargs)
                else:
                    break

            if result.status_code != 200:
                raise requests.ConnectionError(f'No connection with: {args[0]}')

            return result

        return wrapper

    return _retry_atemmpt


class Company(BaseModel):
    name: str
    price: float
    code: str
    p_e: float
    annual_growth: float
    potential_profit: float


class Parser:
    def __init__(self):
        self.usd_value = self.get_usd_value()

    @retry(attempts=5)
    def get_page(self, url: str) -> requests.Response:
        page = session.get(url)
        return page

    def get_usd_value(self) -> float:
        """gets current usd value from cbr.ru"""
        url = 'https://www.cbr.ru/scripts/XML_daily.asp'
        xml_data = self.get_page(url).text
        xml = ElementTree.fromstring(xml_data)
        value = xml.find('./Valute[@ID="R01235"]/Value').text
        value = float(value.replace(',', '.'))
        return value

    def get_amount_of_pages(self) -> int:
        """parse home pafe of markets.businessinsider.com/index/components/s&p_500 and returns number of pages"""
        home_page = self.get_page('https://markets.businessinsider.com/index/components/s&p_500')
        soup = BeautifulSoup(home_page.text, "html.parser")
        page_numbers = soup.find('div', class_='finando_paging margin-top--small').find_all('a')
        max_page_number = int(page_numbers[-2].text)

        return max_page_number

    @staticmethod
    def get_link_and_annual_growth(row: element.ResultSet) -> Tuple[str, float]:
        """convert link and growth from html to str and float"""
        link = row.find('td', class_='table__td table__td--big').a['href']
        annual_growth = float(row.find_all('td')[7].text.strip().split('\n')[1].strip('%'))
        return link, annual_growth

    def get_links_and_growths_from_page(self, page_number: int) -> list[Tuple[str, float]]:
        """takes page number and returns list of tuple(link to company page, annual growth)"""
        page = self.get_page(f'https://markets.businessinsider.com/index/components/s&p_500?p={page_number}')
        soup = BeautifulSoup(page.text, "html.parser")

        table_rows = soup.find('table', class_='table table__layout--fixed').find('tbody').find_all('tr')

        company_link_growth = []
        for row in table_rows:
            link, annual_growth = self.get_link_and_annual_growth(row)
            company_link_growth.append((link, annual_growth))
        return company_link_growth

    @staticmethod
    def divide_list_4_parts(array, size=4) -> list[list[Company]]:
        chunks = ceil(len(array) / float(size))
        return [array[i * chunks: chunks * (i + 1)] for i in range(size)]

    def get_company_cost(self, cost: str) -> float:
        """calculate cost of company from usd to rubbles"""
        cost = float(cost.replace(',', ''))
        return round(self.usd_value * cost, 2)

    @staticmethod
    def get_p_e(table: element.ResultSet) -> float:
        """returns P/E from company page if it's exists else returns None"""
        p_e = float('inf')
        for value in table:
            if value.find('div', class_='snapshot__header').text == 'P/E Ratio':
                try:
                    p_e_str = re.match(r'\r\n\t\t\t\t(-?\d+,?\d+\.\d+)\r\n\t\t\t\tP/E Ratio\n', value.text).group(1)
                    p_e = float(p_e_str.replace(',', ''))
                except AttributeError:
                    pass

        return p_e

    @staticmethod
    def get_potential_profit(row: element.ResultSet) -> float:
        """calculate potential profit from row data"""
        try:
            week_low_high = \
                re.match(
                    r'\n\r\n\t\t\t\t\t\t([\d,]+\.\d+)\r\n\t\t\t\t\t\t52 Week Low\n\n\r\n\t\t\t\t\t\t([\d,]+\.\d+).*',
                    row[1].text
                )

            # in case when you have cost repr like: 2,894.12 we should get rid of comma
            week_low, week_high = float(week_low_high.group(1).replace(',', '')), float(
                week_low_high.group(2).replace(',', ''))
            potential_profit = round(abs(week_high - week_low) * 100 / week_low, 2)
        except IndexError:
            potential_profit = 0
        return potential_profit

    def get_company_info(self, link_growth: Tuple[str, float]) -> Company:
        page = self.get_page(f'https://markets.businessinsider.com/{link_growth[0]}')
        soup = BeautifulSoup(page.text, 'html.parser')

        name = soup.find('span', class_='price-section__label').text.strip()
        price = self.get_company_cost(soup.find('span', class_='price-section__current-value').text)
        code = soup.find('span', class_='price-section__category').find('span').text[2:]
        p_e = self.get_p_e(soup.find_all('div', class_='snapshot__data-item'))
        annual_growth = link_growth[1]
        potential_profit = self.get_potential_profit(soup.find_all('div', class_='snapshot__highlow'))

        return Company(name=name, price=price, code=code,
                       p_e=p_e, annual_growth=annual_growth,
                       potential_profit=potential_profit)

    def get_list_of_pages_with_link_and_growth(self) -> list[Tuple[str, float]]:
        """
        Iterates through all pages and get company link and annual growth
        :return: list of Tuple[link to company, annual growth]
        """
        amount_of_pages = self.get_amount_of_pages()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            page_link_and_growth = executor.map(self.get_links_and_growths_from_page, range(1, amount_of_pages + 1))

        return list(chain(*page_link_and_growth))

    def proceed_links(self, lst: list[list[Company]]) -> list[Company]:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            list_with_data = list(executor.map(self.get_company_info, lst))
        return list_with_data

    def parse_pages(self) -> list[Company]:
        company_links = self.get_list_of_pages_with_link_and_growth()
        divided_company_links = self.divide_list_4_parts(company_links)

        with concurrent.futures.ProcessPoolExecutor(4) as p:
            result = p.map(self.proceed_links, divided_company_links)

        return list(chain(*result))


class Data:
    def __init__(self, data, file_name: str, key: str, reverse: bool):
        self.data = data
        self.file_name = file_name
        self.key = key
        self.reverse = reverse

    def get_sorted_companies(self) -> list[Company]:
        companies = [cmp.dict(include={'name', 'code', self.key}) for cmp in self.data]
        return sorted(companies, key=lambda item: item.get(self.key), reverse=self.reverse)[:10]

    def create_json(self) -> None:
        with open(self.file_name, 'w') as f:
            sorted_companies = self.get_sorted_companies()
            json.dump(sorted_companies, f)


class MostExpensiveCompanies(Data):
    def __init__(self, info):
        super().__init__(info, '10_most_expensive_companies.json', 'price', True)
        self.create_json()


class LessPEvalueCompanies(Data):
    def __init__(self, info):
        super().__init__(info, '10_lowest_p_e.json', 'p_e', False)
        self.create_json()


class HighestGrowthCompanies(Data):
    def __init__(self, info):
        super().__init__(info, '10_highest_growth_rate.json', 'annual_growth', True)
        self.create_json()


class MostRentableCompanies(Data):
    def __init__(self, info):
        super().__init__(info, '10_most_rentable.json', 'potential_profit', True)
        self.create_json()


if __name__ == '__main__':
    start = time.time()

    companies_data = Parser().parse_pages()
    MostExpensiveCompanies(companies_data)
    LessPEvalueCompanies(companies_data)
    HighestGrowthCompanies(companies_data)
    MostRentableCompanies(companies_data)

    finish = time.time()

    print(round(finish - start, 2), 'secs')
