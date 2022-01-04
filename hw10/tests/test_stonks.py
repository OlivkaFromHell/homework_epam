from pathlib import Path

import pytest
import requests

import hw10.stonks


class FakeResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


def test_get_usd_value(monkeypatch):
    xml = '<ValCurs Date="31.12.2021" name="Foreign Currency Market">' \
          '<Valute ID="R01235">' \
          '<NumCode>036</NumCode>' \
          '<CharCode>AUD</CharCode>' \
          '<Nominal>1</Nominal>' \
          '<Name>Австралийский доллар</Name>' \
          '<Value>53,9141</Value>' \
          '</Valute></ValCurs>'

    def mock_get_page(*args, **kwargs):
        return FakeResponse(200, xml)

    monkeypatch.setattr(requests.Session, "get", mock_get_page)

    assert hw10.stonks.get_usd_value() == 53.9141


def test_wrapper_retry(monkeypatch):
    def mock_get_page(*args, **kwargs):
        return FakeResponse(400, '<html></html>')

    monkeypatch.setattr(requests.Session, "get", mock_get_page)

    with pytest.raises(requests.ConnectionError):
        hw10.stonks.get_page('unvalid_link.com')


def test_get_company_cost(monkeypatch):
    def fake_get_usd_value():
        return 1

    monkeypatch.setattr(hw10.stonks, 'get_usd_value', fake_get_usd_value)
    assert hw10.stonks.get_company_cost('50') == 50.0


def test_get_sorted_dict():
    info = {'Google': {'cost': 500, 'age': 20}, 'Apple': {'cost': 1000, 'age': 30}}
    sorted_info = {'Apple': {'cost': 1000, 'age': 30}, 'Google': {'cost': 500, 'age': 20}}
    assert hw10.stonks.get_sorted_dict(info, 'cost') == sorted_info


def test_get_amount_of_pages(monkeypatch):
    html = '<html>' \
           '<div class="finando_paging margin-top--small">' \
           '<a href="?p=1">1</a>' \
           '<a href="?p=2">2</a>' \
           '<a href="?p=3">3</a>' \
           '<a href="?p=4">' \
           '<img src="data:image/gif;base64</a>' \
           '</div></html>'

    def mock_get_page(*args, **kwargs):
        return FakeResponse(200, html)

    monkeypatch.setattr(requests.Session, "get", mock_get_page)

    assert hw10.stonks.get_amount_of_pages() == 3


def test_get_links_and_growths_from_page(monkeypatch):
    with open(Path(__file__).parent.joinpath('home_page.html')) as f:
        html = f.read()

    def mock_get_page(*args, **kwargs):
        return FakeResponse(200, html)

    monkeypatch.setattr(requests.Session, "get", mock_get_page)

    result = [('/stocks/yum-stock', 25.85), ('/stocks/zbra-stock', 54.53),
              ('/stocks/zbh-stock', -14.89)]
    assert hw10.stonks.get_links_and_growths_from_page(1) == result


def test_get_company_info(monkeypatch):
    with open(Path(__file__).parent.joinpath('company_page.html')) as f:
        html = f.read()

    def mock_get_page(*args, **kwargs):
        return FakeResponse(200, html)

    def fake_get_company_cost(*args, **kwargs):
        return 10080.02

    monkeypatch.setattr(requests.Session, "get", mock_get_page)
    monkeypatch.setattr(hw10.stonks, 'get_company_cost', fake_get_company_cost)

    result = 'YUM! Brands Inc.', 10080.02, "YUM", float('inf'), 25.85, 0
    assert hw10.stonks.get_company_info(('/mmm/stock/', 25.85)) == result
