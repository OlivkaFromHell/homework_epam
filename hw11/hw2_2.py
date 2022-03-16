"""
You are given the following code:

class Order:
    morning_discount = 0.25

    def __init__(self, price):
        self.price = price

    def final_price(self):
        return self.price - self.price * self.morning_discount

Make it possible to use different discount programs.
Hint: use strategy behavioural OOP pattern.
https://refactoring.guru/design-patterns/strategy

Example of the result call:

def morning_discount(order):
    ...

def elder_discount(order):
    ...

order_1 = Order(100, morning_discount)
assert order_1.final_price() == 75

order_2 = Order(100, elder_discount)
assert order_2.final_price() == 10
"""
from abc import ABC, abstractmethod
from typing import ClassVar, Union


class DiscountStrategy(ABC):
    @abstractmethod
    def calculate_discount(self, price):
        pass


class MorningDiscount(DiscountStrategy):
    def calculate_discount(self, price):
        return price * 0.25


class ElderDiscount(DiscountStrategy):
    def calculate_discount(self, price):
        return price * 0.9


class Order:
    def __init__(self, price: Union[float, int], discount: ClassVar):
        self.price = price
        self.__discount = discount

    def final_price(self):
        return self.price - self.__discount.calculate_discount(self, self.price)


if __name__ == "__main__":

    order_1 = Order(100, MorningDiscount)
    assert order_1.final_price() == 75

    order_2 = Order(100, ElderDiscount)
    assert order_2.final_price() == 10
