# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import pytest

from InvestmentWorkshop.collector.czce import (
    fetch_czce_history_index,
)


def test_fetch_czce_history_index():
    result = fetch_czce_history_index()
    assert isinstance(result, dict)

    assert len(result.keys()) == 2
    assert 'futures' in result.keys()
    assert 'option' in result.keys()

    for k, v in result.items():
        assert isinstance(v, list)
        for item in v:
            assert isinstance(item, str)
