import pytest

from hw11.hw1 import SimplifiedEnum


def test_positive_case_1():
    class ColorsEnum(metaclass=SimplifiedEnum):
        __keys = ("RED", "BLUE", "ORANGE", "BLACK")

    assert ColorsEnum.RED == "RED"


def test_negative_case_1():
    class ColorsEnum(metaclass=SimplifiedEnum):
        __keys = ("RED", "BLUE", "ORANGE", "BLACK")

    assert ColorsEnum.BLUE != "RED"


def test_positive_case_2():
    class SizesEnum(metaclass=SimplifiedEnum):
        __keys = ("XL", "L", "M", "S", "XS")

    assert SizesEnum.XL == "XL"


def test_non_existing_called_attr():
    class ColorsEnum(metaclass=SimplifiedEnum):
        __keys = ("RED", "BLUE", "ORANGE", "BLACK")

    with pytest.raises(AttributeError):
        ColorsEnum.XL


def test_wrong_attr_name():
    class ColorsEnum(metaclass=SimplifiedEnum):
        __keys = ("1RED", "BLUE")

    assert getattr(ColorsEnum, '1RED') == "1RED"


def test_access_through_method():
    class ColorsEnum(metaclass=SimplifiedEnum):
        __keys = ("RED", "BLUE", "ORANGE", "BLACK")

        def do_smth(self):
            return self.RED

    num = ColorsEnum()
    assert num.do_smth() == "RED"


def test_access_through_cls_method():
    class ColorsEnum(metaclass=SimplifiedEnum):
        __keys = ("RED", "BLUE", "ORANGE", "BLACK")

        @classmethod
        def do_smth(cls):
            return cls.RED

    num = ColorsEnum()
    assert num.do_smth() == "RED"
