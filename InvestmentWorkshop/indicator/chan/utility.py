# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Tuple, Optional

from .definition import (
    TrendType,
    OrdinaryCandle,
    MergedCandle,
    FractalType,
    Fractal,

    OrdinaryCandleList,
    MergedCandleList,
    FractalList,
)


def is_inclusive_number(h1: float,
                        l1: float,
                        h2: float,
                        l2: float) -> bool:
    """
    判断两根K线是否存在包含关系。两根K线的关系有以下九种：
        1. H1 > H2 & L1 > L2, 非包含，下降。
        2. H1 > H2 & L1 = L2, 包含, K1包含K2, 下降。
        3. H1 > H2 & L1 < L2, 包含。
        4. H1 = H2 & L1 > L2, 包含。
        5. H1 = H2 & L1 = L2, 包含。
        6. H1 = H2 & L1 < L2, 包含。
        7. H1 < H2 & L1 > L2, 包含。
        8. H1 < H2 & L1 = L2, 包含。
        9. H1 < H2 & L1 < L2, 非包含, 。

    :param h1: float, HIGH price of current candlestick.
    :param l1: float, LOW price of current candlestick.
    :param h2: float, HIGH price of previous candlestick.
    :param l2: float, LOW price of previous candlestick.

    ----
    :return: bool, if
    """
    if (h1 > h2 and l1 > l2) or (h1 < h2 and l1 < l2):
        return False
    else:
        return True


def is_inclusive_candle(candle_1: OrdinaryCandle,
                        candle_2: OrdinaryCandle
                        ) -> bool:
    """
    判断两根K线是否存在包含关系。两根K线的关系有以下九种：

    :param candle_1: OrdinaryCandle, candlestick 1.
    :param candle_2: OrdinaryCandle, candlestick 2.

    ----
    :return: bool, if
    """

    return is_inclusive_number(
        candle_1.high,
        candle_1.low,
        candle_2.high,
        candle_2.low
    )


def get_trend(left_candle: MergedCandle,
              right_candle: OrdinaryCandle
              ) -> TrendType:
    if right_candle.high > left_candle.high and right_candle.low > left_candle.low:
        return TrendType.Bullish
    elif right_candle.high < left_candle.high and right_candle.low < left_candle.low:
        return TrendType.Bearish
    else:
        raise RuntimeError('缠论K线不应存在包含关系。')


def get_merged_candle_idx(merged_candle: MergedCandle,
                          merged_candle_list: MergedCandleList
                          ) -> int:
    return merged_candle_list.index(merged_candle)


def get_fractal_distance(left_fractal: Fractal,
                         right_fractal: Fractal,
                         merged_candle_list: MergedCandleList) -> int:
    """
    两个分型之间的距离（取分型中间那根K线）。

    :param left_fractal:
    :param right_fractal:
    :param merged_candle_list:

    :return:
    """
    return get_merged_candle_idx(right_fractal.middle_candle, merged_candle_list) - \
        get_merged_candle_idx(left_fractal.middle_candle, merged_candle_list)
