import concurrent.futures
import json
import random
import re
import time
import xml.etree.ElementTree as ElementTree
from typing import Dict, List, Tuple, Union

import requests
from bs4 import BeautifulSoup, element

session = requests.Session()


def retry(attempts=5):
    def _retry_atemmpt(func):
        def wrapper(*args, **kwargs):
            nonlocal attempts
            result = func(*args, **kwargs)
            while attempts != 0:
                if result.status_code != 200:
                    time.sleep(0.5 + random.uniform(0.5, 1))
                    attempts -= 1
                    result = func(*args, **kwargs)
                else:
                    break

            if result.status_code != 200:
                raise requests.ConnectionError(f'No connection with: {args[0]}')

            return result

        return wrapper

    return _retry_atemmpt


@retry(attempts=5)
def get_page(url: str) -> requests.Response:
    page = session.get(url)
    return page


def get_usd_value() -> float:
    """gets current usd value from cbr.ru"""
    url = 'https://www.cbr.ru/scripts/XML_daily.asp'
    xml_data = get_page(url).text
    xml = ElementTree.fromstring(xml_data)
    value = xml.find('./Valute[@ID="R01235"]/Value').text
    value = float(value.replace(',', '.'))
    return value


def get_amount_of_pages() -> int:
    """parse home pafe of markets.businessinsider.com/index/components/s&p_500 and returns number of pages"""
    home_page = get_page('https://markets.businessinsider.com/index/components/s&p_500')
    soup = BeautifulSoup(home_page.text, "html.parser")
    page_numbers = soup.find('div', class_='finando_paging margin-top--small').find_all('a')
    max_page_number = int(page_numbers[-2].text)

    return max_page_number


def get_link_and_annual_growth(row: element.ResultSet) -> Tuple[str, float]:
    """convert link and growth from html to str and float"""
    link = row.find('td', class_='table__td table__td--big').a['href']
    annual_growth = float(row.find_all('td')[7].text.strip().split('\n')[1].strip('%'))
    return link, annual_growth


def get_links_and_growths_from_page(page_number: int) -> List[Tuple[str, float]]:
    """takes page number and returns list of tuple(link to company page, annual growth)"""
    page = get_page(f'https://markets.businessinsider.com/index/components/s&p_500?p={page_number}')
    soup = BeautifulSoup(page.text, "html.parser")

    table_rows = soup.find('table', class_='table table__layout--fixed').find('tbody').find_all('tr')

    company_link_growth = []
    for row in table_rows:
        link, annual_growth = get_link_and_annual_growth(row)
        company_link_growth.append((link, annual_growth))
    return company_link_growth


def get_company_cost(cost: str) -> float:
    """calculate cost of company from usd to rubbles"""
    cost = float(cost.replace(',', ''))
    return round(get_usd_value() * cost, 2)


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


def get_potential_profit(row: element.ResultSet) -> float:
    """calculate potential profit from row data"""
    try:
        week_low_high = re \
            .match(r'\n\r\n\t\t\t\t\t\t([\d,]+\.\d+)\r\n\t\t\t\t\t\t52 Week Low\n\n\r\n\t\t\t\t\t\t([\d,]+\.\d+).*',
                   row[1].text)

        # in case when you have cost repr like: 2,894.12 we should get rid of comma
        week_low, week_high = float(week_low_high.group(1).replace(',', '')), float(
            week_low_high.group(2).replace(',', ''))
        potential_profit = round(abs(week_high - week_low) * 100 / week_low, 2)
    except IndexError:
        potential_profit = 0
    return potential_profit


def get_company_info(link_growth: Tuple[str, float]) -> Tuple[str, float, str, float, float, float]:
    page = get_page(f'https://markets.businessinsider.com/{link_growth[0]}')
    soup = BeautifulSoup(page.text, 'html.parser')

    name = soup.find('span', class_='price-section__label').text.strip()
    price = get_company_cost(soup.find('span', class_='price-section__current-value').text)
    code = soup.find('span', class_='price-section__category').find('span').text[2:]
    p_e = get_p_e(soup.find_all('div', class_='snapshot__data-item'))
    annual_growth = link_growth[1]
    potential_profit = get_potential_profit(soup.find_all('div', class_='snapshot__highlow'))

    return name, price, code, p_e, annual_growth, potential_profit


def get_list_of_pages_with_link_and_growth() -> Dict[int, List[Tuple[str, float]]]:
    """Iterates through all pages and returns dict
        key: page number
        value: list of tuple(link to company, annual growth)
    """
    amount_of_pages = get_amount_of_pages()

    company_names = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        page_link_and_growth = executor.map(get_links_and_growths_from_page, range(1, amount_of_pages + 1))

    for page_number, list_with_link_and_growth in enumerate(page_link_and_growth):
        company_names[page_number + 1] = list_with_link_and_growth
    return company_names


def parse_pages() -> Dict[str, Dict[str, Union[str, float]]]:
    company_links = get_list_of_pages_with_link_and_growth()

    companies = {}
    for page in company_links:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            list_with_data = executor.map(get_company_info, [(link, growth) for link, growth in company_links[page]])
        for info in list_with_data:
            name, price, code, p_e, annual_growth, potential_profit = info
            companies[name] = {'price': price, 'code': code,
                               'P/E': p_e, 'annual growth': annual_growth,
                               'potential profit': potential_profit}

    return companies


class Companies:
    def __init__(self, companies_info):
        self.companies_info = companies_info

    def get_sorted_dict(self, key: str, reverse: bool) -> dict:
        return dict(sorted(self.companies_info.items(), key=lambda item: item[1][key], reverse=reverse)[:10])


class MostExpensiveCompanies(Companies):
    def __init__(self, companies_info):
        super().__init__(companies_info)
        with open('10_most_expensive_companies.json', 'w') as f:
            sorted_companies = self.get_sorted_dict('price', True)
            json.dump(sorted_companies, f)


class LessPEvalueCompanies(Companies):
    def __init__(self, companies_info):
        super().__init__(companies_info)
        with open('10_lowest_p_e.json', 'w') as f:
            sorted_companies = self.get_sorted_dict('P/E', False)
            json.dump(sorted_companies, f)


class HighestGrowthCompanies(Companies):
    def __init__(self, companies_info):
        super().__init__(companies_info)
        with open('10_highest_growth_rate.json', 'w') as f:
            sorted_companies = self.get_sorted_dict('annual growth', True)
            json.dump(sorted_companies, f)


class MostRentableCompanies(Companies):
    def __init__(self, companies_info):
        super().__init__(companies_info)
        with open('10_most_rentable.json', 'w') as f:
            sorted_companies = self.get_sorted_dict('potential profit', True)
            json.dump(sorted_companies, f)


if __name__ == '__main__':
    start = time.time()

    companies_data = parse_pages()
    MostExpensiveCompanies(companies_data)
    LessPEvalueCompanies(companies_data)
    HighestGrowthCompanies(companies_data)
    MostRentableCompanies(companies_data)

    finish = time.time()

    print(round(finish - start, 2), 'secs')
