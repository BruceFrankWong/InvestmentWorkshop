# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from InvestmentWorkshop.utiltiy import (
    PACKAGE_NAME,
)


def test_package_name():
    assert isinstance(PACKAGE_NAME, str)
    assert PACKAGE_NAME == 'InvestmentWorkshop'
