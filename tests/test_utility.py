# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from pathlib import Path


from InvestmentWorkshop.utiltiy import (
    PACKAGE_NAME,
    PACKAGE_PATH,
)


def test_package_name():
    assert isinstance(PACKAGE_NAME, str)
    assert PACKAGE_NAME == 'InvestmentWorkshop'


def test_package_path():
    from InvestmentWorkshop import utiltiy
    assert PACKAGE_PATH == Path(utiltiy.__file__).parent
