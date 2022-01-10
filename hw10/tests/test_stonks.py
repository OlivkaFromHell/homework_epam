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

    assert hw10.stonks.Parser().get_usd_value() == 53.9141


def test_wrapper_retry(monkeypatch):
    def mock_get_page(*args, **kwargs):
        return FakeResponse(400, '<html></html>')

    monkeypatch.setattr(requests.Session, "get", mock_get_page)

    with pytest.raises(requests.ConnectionError):
        hw10.stonks.get_page('unvalid_link.com')


def test_get_company_cost(monkeypatch):
    xml = '<ValCurs Date="31.12.2021" name="Foreign Currency Market">' \
          '<Valute ID="R01235">' \
          '<NumCode>036</NumCode>' \
          '<CharCode>AUD</CharCode>' \
          '<Nominal>1</Nominal>' \
          '<Name>Австралийский доллар</Name>' \
          '<Value>1,0</Value>' \
          '</Valute></ValCurs>'

    def mock_get_page(*args, **kwargs):
        return FakeResponse(200, xml)

    monkeypatch.setattr(requests.Session, "get", mock_get_page)

    assert hw10.stonks.Parser().get_company_cost('50') == 50.0


def test_get_sorted_dict():
    info = [hw10.stonks.Company(name='3M Co.', price=13411.72, code='MMM', p_e=19.91,
                                annual_growth=3.06, potential_profit=27.85),
            hw10.stonks.Company(name='A.O. Smith Corp.', price=6181.07, code='AOS', p_e=25.06,
                                annual_growth=48.8, potential_profit=66.55)]
    sorted_info = [hw10.stonks.Company(name='A.O. Smith Corp.', price=6181.07, code='AOS', p_e=25.06,
                                       annual_growth=48.8, potential_profit=66.55).dict(include={'name', 'code',
                                                                                                 'potential_profit'}),
                   hw10.stonks.Company(name='3M Co.', price=13411.72, code='MMM', p_e=19.91,
                                       annual_growth=3.06, potential_profit=27.85).dict(include={'name', 'code',
                                                                                                 'potential_profit'})]

    assert hw10.stonks.Data(info, 'a.json', 'potential_profit', True).get_sorted_companies() == sorted_info


def test_get_amount_of_pages(monkeypatch):
    data = hw10.stonks.Parser()
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

    assert data.get_amount_of_pages() == 3


def test_get_links_and_growths_from_page(monkeypatch):
    data = hw10.stonks.Parser()
    with open(Path(__file__).parent.joinpath('home_page.html')) as f:
        html = f.read()

    def mock_get_page(*args, **kwargs):
        return FakeResponse(200, html)

    monkeypatch.setattr(requests.Session, "get", mock_get_page)

    result = [('/stocks/yum-stock', 25.85), ('/stocks/zbra-stock', 54.53),
              ('/stocks/zbh-stock', -14.89)]
    assert data.get_links_and_growths_from_page(1) == result


def test_get_company_info(monkeypatch):
    data = hw10.stonks.Parser()
    with open(Path(__file__).parent.joinpath('company_page.html')) as f:
        html = f.read()

    def mock_get_page(*args, **kwargs):
        return FakeResponse(200, html)

    def fake_get_company_cost(*args, **kwargs):
        return 10080.02

    monkeypatch.setattr(requests.Session, "get", mock_get_page)
    monkeypatch.setattr(hw10.stonks.Parser, 'get_company_cost', fake_get_company_cost)

    result = hw10.stonks.Company(name='YUM! Brands Inc.', price=10080.02, code="YUM", p_e=float('inf'),
                                 annual_growth=25.85, potential_profit=0)
    assert data.get_company_info(('/mmm/stock/', 25.85)) == result
