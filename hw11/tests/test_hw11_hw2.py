import pytest

from hw11.hw2 import Order


def test_positive_case_1():
    def morning_discount():
        return 0.25

    def elder_discount():
        return 0.9

    order_1 = Order(100, morning_discount)
    assert order_1.final_price() == 75

    order_2 = Order(100, elder_discount)
    assert order_2.final_price() == 10


def test_positive_case_2():
    def discount():
        return 1

    def new_discount():
        return 0.99

    order_1 = Order(100, discount)
    assert order_1.final_price() == 0

    order_2 = Order(100, new_discount)
    assert order_2.final_price() == 1


def test_wrong_discount_strategy():
    def discount():
        return 1.25

    with pytest.raises(ValueError):
        Order(100, discount)
