# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import datetime as dt

from InvestmentWorkshop.collector.dce import (
    fetch_dce_history_index,
)


def test_fetch_dce_history_index():
    result = fetch_dce_history_index()
    assert isinstance(result, dict)
    assert len(result) == (dt.date.today().year - 2006)

    for year, content in result.items():
        assert isinstance(year, int)
        assert isinstance(content, dict)
        for product, url in content.items():
            assert isinstance(product, str)
            assert isinstance(url, str)
