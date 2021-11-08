# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import pytest

from InvestmentWorkshop.indicator.chan2 import (
    OrdinaryCandle,
    is_inclusive_number,
    is_inclusive_candle
)


@pytest.mark.parametrize(
    'candle_1, candle_2, result',
    [
        (
                OrdinaryCandle(high=23900.0, low=23840.0),
                OrdinaryCandle(high=23895.0, low=23845.0),
                True
        ),
        (
                OrdinaryCandle(high=23900.0, low=23840.0),
                OrdinaryCandle(high=23895.0, low=23845.0),
                True
        ),
        (2019, 8),
        (2008, 12),
        (2030, 3),
        (2020, 15),
        (2020, -3),
    ]
)
def test_is_inclusive_candle(candle_1, candle_2, result):
    assert is_inclusive_candle(candle_1, candle_2) is result
