# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List, Tuple, Optional

from .definition import (
    FirstOrLast,
    FractalPattern,
    FractalPotential,
    Trend,

    OrdinaryCandle,
    MergedCandle,
    Fractal,
    Stroke,
    Segment,
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


def is_regular_fractal(
        left_candle: MergedCandle,
        middle_candle: MergedCandle,
        right_candle: MergedCandle
) -> Tuple[bool, Optional[FractalPattern]]:
    """

    :param left_candle:
    :param middle_candle:
    :param right_candle:
    :return:
    """
    # 如果：
    #     中间K线的最高价比左右K线的最高价都高：
    # 顶分型。
    if middle_candle.high > left_candle.high and middle_candle.high > right_candle.high:
        return True, FractalPattern.Top

    # 如果：
    #     中间K线的最低价比左右K线的最低价都低：
    # 底分型。
    elif middle_candle.low < left_candle.low and middle_candle.low < right_candle.low:
        return True, FractalPattern.Bottom

    # 其它：不是分型。
    else:
        return False, None


def is_potential_fractal(
        at: FirstOrLast,
        merged_candles: List[MergedCandle]
) -> Tuple[bool, Optional[FractalPattern], Optional[FractalPotential]]:
    """

    :param at:
    :param merged_candles:
    :return:
    """
    # 如果 First:
    # 需要3根K线才判断是否可以生成潜在分型。
    if at == FirstOrLast.First:
        if len(merged_candles) >= 3:
            left_candle: MergedCandle = merged_candles[-3]
            middle_candle: MergedCandle = merged_candles[-2]
            right_candle: MergedCandle = merged_candles[-1]

            # 如果：
            #     左侧K线的最高价 > 中间K线的最高价 > 右侧K线的最高价：
            # 顶分型，潜在的。
            if left_candle.high > middle_candle.high > right_candle.high:
                return True, FractalPattern.Top, FractalPotential.Left

            # 如果：
            #     左侧K线的最低价 < 中间K线的最低价 < 右侧K线的最低价：
            # 顶分型，潜在的。
            elif left_candle.low < middle_candle.low < right_candle.low:
                return True, FractalPattern.Bottom, FractalPotential.Left

        else:
            return False, None, None

    # 如果 Last:
    # 需要2根K线才判断是否可以生成潜在分型。
    else:
        left_candle: MergedCandle = merged_candles[-2]
        right_candle: MergedCandle = merged_candles[-1]
        # 如果 ：
        #     右侧K线的最高价比左侧K线的最高价高：
        # 顶分型。
        if right_candle.high > left_candle.high:
            return True, FractalPattern.Top, FractalPotential.Right

        # 如果：
        #     中间K线的最低价比左右K线的最低价都低：
        # 底分型。
        elif right_candle.low < left_candle.low:
            return True, FractalPattern.Bottom, FractalPotential.Right

        # 其它：不是分型。
        else:
            return False, None, None


def is_overlap(
        left_stroke: Stroke,
        right_stroke: Stroke
) -> Tuple[bool, Optional[float], Optional[float]]:
    """
    Determine whether an overlap range exists between 2 strokes, and return high and low of
    the range if existed.

    :param left_stroke:
    :param right_stroke:
    :return: a 3-element tuple.
             The first is bool, True if the overlap range exists.
             The second is float, high of the overlap range. Return None if the range not exists.
             The second is float, low of the overlap range. Return None if the range not exists.
    """
    # 如果：
    #     1. 右侧笔是上升笔，右侧笔的左侧价 < 左侧笔的左侧价，右侧笔的右侧价 < 左侧笔的左侧价
    #   或者
    #     2. 右侧笔是下降笔，右侧笔的左侧价 > 左侧笔的左侧价，右侧笔的右侧价 > 左侧笔的左侧价
    # 无重叠。

    if (
            right_stroke.trend == Trend.Bullish and
            right_stroke.left_price < left_stroke.left_price and
            right_stroke.right_price < left_stroke.left_price
    ) or (
            right_stroke.trend == Trend.Bearish and
            right_stroke.left_price > left_stroke.left_price and
            right_stroke.right_price > left_stroke.left_price
    ):
        return False, None, None

    # 如果：
    #     1. 右侧笔是上升笔，且
    #     2A. 右侧笔的左侧价 < 左侧笔的左侧价，右侧笔的右侧价 >= 左侧笔的左侧价
    #       有重叠：
    #       高点 = min(右侧笔的右侧价, 左侧笔的右侧价)，低点 = 左侧笔的左侧价
    #
    # A3. 右侧笔是上升笔，右侧笔的左侧价 >= 左侧笔的左侧价，右侧笔的右侧价 > 左侧笔的右侧价
    #       有重叠：
    #       高点 = min(右侧笔的右侧价, 左侧笔的左侧价)，低点 = 右侧笔的左侧价

    if right_stroke.trend == Trend.Bullish:
        if right_stroke.left_price < left_stroke.left_price <= right_stroke.right_price:
            overlap_high = min(right_stroke.right_price, left_stroke.right_price)
            overlap_low = left_stroke.left_price
        elif right_stroke.left_price >= left_stroke.left_price:
            overlap_high = min(right_stroke.right_price, left_stroke.right_price)
            overlap_low = right_stroke.left_price
        else:
            raise RuntimeError('Unknown parameters in generating first segment (Bullish).')

    # B2. 右侧笔是下降笔，右侧笔的左侧价 > 左侧笔的左侧价，右侧笔的右侧价 <= 左侧笔的右侧价
    #       有重叠：
    #       高点 = 左侧笔的左侧价，低点 = max(右侧笔的右侧价, 左侧笔的右侧价)
    #
    # B3. 右侧笔是下降笔，右侧笔的左侧价 <= 左侧笔的左侧价，右侧笔的右侧价 < 左侧笔的右侧价
    #       有重叠：
    #       高点 = 右侧笔的左侧价，低点 = max(右侧笔的右侧价, 左侧笔的左侧价)
    else:
        if right_stroke.left_price > right_stroke.left_price and \
                right_stroke.right_price <= left_stroke.right_price:
            overlap_high = left_stroke.left_price
            overlap_low = max(right_stroke.right_price, left_stroke.right_price)
        elif right_stroke.left_price <= right_stroke.left_price:
            overlap_high = right_stroke.left_price
            overlap_low = max(right_stroke.right_price, left_stroke.left_price)
        else:
            raise RuntimeError('Unknown parameters in generating first segment (Bearish).')

    return True, overlap_high, overlap_low


def get_trend(left_candle: MergedCandle,
              right_candle: OrdinaryCandle
              ) -> Trend:
    if right_candle.high > left_candle.high and right_candle.low > left_candle.low:
        return Trend.Bullish
    elif right_candle.high < left_candle.high and right_candle.low < left_candle.low:
        return Trend.Bearish
    else:
        raise RuntimeError('缠论K线不应存在包含关系。')


def get_merged_candle_idx(
        merged_candle: MergedCandle,
        merged_candle_list: List[MergedCandle]
) -> int:
    return merged_candle_list.index(merged_candle)


def get_fractal_distance(
        left_fractal: Fractal,
        right_fractal: Fractal,
        merged_candle_list: List[MergedCandle]
) -> int:
    """
    两个分型之间的距离（取分型中间那根K线）。

    :param left_fractal:
    :param right_fractal:
    :param merged_candle_list:

    :return:
    """
    return get_merged_candle_idx(right_fractal.middle_candle, merged_candle_list) - \
        get_merged_candle_idx(left_fractal.middle_candle, merged_candle_list)
