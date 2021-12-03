# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List, Tuple, Optional

from .definition import (
    FirstOrLast,
    FractalPattern,
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


def is_regular_fractal(left_candle: MergedCandle,
                       middle_candle: MergedCandle,
                       right_candle: MergedCandle
                       ) -> Optional[FractalPattern]:
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
        return FractalPattern.Top

    # 如果：
    #     中间K线的最低价比左右K线的最低价都低：
    # 底分型。
    elif middle_candle.low < left_candle.low and middle_candle.low < right_candle.low:
        return FractalPattern.Bottom

    # 其它：不是分型。
    else:
        return None


def is_fractal(left_candle: Optional[MergedCandle],
               middle_candle: MergedCandle,
               right_candle: Optional[MergedCandle]
               ) -> Optional[FractalPattern]:
    """

    :param left_candle:
    :param middle_candle:
    :param right_candle:
    :return:
    """

    if left_candle is None and right_candle is None:
        raise ValueError('<left_candle> and <right_candle> could not both be None.')

    # Left potential fractal.
    elif left_candle is None:
        if middle_candle.high > right_candle.high and middle_candle.low > right_candle.low:
            return FractalPattern.Top
        elif middle_candle.high < right_candle.high and middle_candle.low < right_candle.low:
            return FractalPattern.Bottom
        else:
            raise RuntimeError('Unexpected relationship in two merged candles.')

    # Right potential fractal.
    elif right_candle is None:
        if middle_candle.high > left_candle.high and middle_candle.low > left_candle.low:
            return FractalPattern.Top
        elif middle_candle.high < left_candle.high and middle_candle.low < left_candle.low:
            return FractalPattern.Bottom
        else:
            raise RuntimeError('Unexpected relationship in two merged candles.')

    # Regular fractal.
    else:
        # 如果：中间K线的最高价比左右K线的最高价都高，顶分型。
        if middle_candle.high > left_candle.high and middle_candle.high > right_candle.high:
            return FractalPattern.Top

        # 如果：中间K线的最低价比左右K线的最低价都低，底分型。
        elif middle_candle.low < left_candle.low and middle_candle.low < right_candle.low:
            return FractalPattern.Bottom

        # 其它：不是分型。
        else:
            return None


def is_left_potential_fractal(left_candle: MergedCandle,
                              right_candle: MergedCandle
                              ) -> FractalPattern:
    if left_candle.high > right_candle.high and left_candle.low > right_candle.low:
        return FractalPattern.Top
    elif left_candle.high < right_candle.high and left_candle.low < right_candle.low:
        return FractalPattern.Bottom
    else:
        raise RuntimeError('Unexpected relationship in two merged candles.')


def is_right_potential_fractal(left_candle: MergedCandle,
                               right_candle: MergedCandle
                               ) -> FractalPattern:
    if right_candle.high > left_candle.high and right_candle.low > left_candle.low:
        return FractalPattern.Top
    elif right_candle.high < left_candle.high and right_candle.low < left_candle.low:
        return FractalPattern.Bottom
    else:
        raise RuntimeError('Unexpected relationship in two merged candles.')


def is_potential_fractal(
        candles: List[MergedCandle],
        at: FirstOrLast
) -> Tuple[bool, Optional[FractalPattern]]:
    """
    Determine the potential fractal.

    :param candles:
    :param at:
    :return:
    """
    length: int = len(candles)

    # 如果列表长度 < 2，返回 (False, None)。
    if length < 2:
        return False, None

    # 如果列表中合并K线的id不是紧挨着的，返回 (False, None)。
    for i in range(length - 1):
        if candles[i + 1].id - candles[i].id != 1:
            return False, None

    # 如果列表长度 < 2，返回 (False, None)。
    if length == 2:
        if candles[1].high > candles[0].high:
            if at == FirstOrLast.Last:
                return True, FractalPattern.Top
            else:
                return True, FractalPattern.Bottom
        else:
            if at == FirstOrLast.Last:
                return True, FractalPattern.Bottom
            else:
                return True, FractalPattern.Top

    # 由开头两个合并K线获得序列方向。
    is_increasing: bool = True if candles[1].high > candles[0].high else False

    for i in range(2, length):
        if is_increasing:
            if candles[i].high < candles[i - 1].high:
                return False, None
        else:
            if candles[i].high > candles[i - 1].high:
                return False, None

    if is_increasing:
        if at == FirstOrLast.Last:
            return True, FractalPattern.Top
        else:
            return True, FractalPattern.Bottom
    else:
        if at == FirstOrLast.Last:
            return True, FractalPattern.Bottom
        else:
            return True, FractalPattern.Top


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


def generate_merged_candle(ordinary_candle: OrdinaryCandle,
                           last_candle: Tuple[Optional[MergedCandle], Optional[MergedCandle]]
                           ) -> MergedCandle:
    """
    Generate a new merged candle or crop with existed merged candle.

    :param ordinary_candle:  
    :param last_candle: 
    :return: 
    """
    left_candle: Optional[MergedCandle]
    right_candle: Optional[MergedCandle]
    
    left_candle, right_candle = last_candle
    
    # 如果 left_candle 和 right_candle 都是 None，直接将 ordinary_candle 作为新的合并K线。
    if left_candle is None and right_candle is None:
        new_merged_candle: MergedCandle = MergedCandle(
            id=0,
            high=ordinary_candle.high,
            low=ordinary_candle.low,
            period=1,
            left_ordinary_id=0
        )

        return new_merged_candle

    # 如果 left_candle 和 right_candle 中有一个是 None：
    if right_candle is None and left_candle is not None:
        right_candle, left_candle = left_candle, right_candle
    
    # 如果没有包含关系，直接将 ordinary_candle 作为新的合并K线。
    if not is_inclusive_candle(right_candle, ordinary_candle):
        new_merged_candle: MergedCandle = MergedCandle(
            id=right_candle.id + 1,
            high=ordinary_candle.high,
            low=ordinary_candle.low,
            period=1,
            left_ordinary_id=right_candle.right_ordinary_id + 1
        )

        return new_merged_candle
    
    # 有包含关系：
    else:
        # last_candle 长度为 1，取前合并K线和新普通K线的最大范围。
        if left_candle is None:
            right_candle.high = max(
                right_candle.high,
                ordinary_candle.high
            )
            right_candle.low = min(
                right_candle.low,
                ordinary_candle.low
            )
            right_candle.period += 1

            return right_candle
        
        else:
            if left_candle.id > right_candle.id:
                left_candle, right_candle = right_candle, left_candle
            
            if left_candle.id == right_candle.id:
                raise ValueError('变量 <last_candle> 中的两个合并K线的 id 相同。')
            if right_candle.id - left_candle.id != 1:
                raise ValueError('变量 <last_candle> 中的两个合并K线的 id 序号相差超过 1。')
            
            if right_candle.high > left_candle.high and \
                    right_candle.low > left_candle.low:
                right_candle.high = max(
                    right_candle.high,
                    ordinary_candle.high
                )
                right_candle.low = max(
                    right_candle.low,
                    ordinary_candle.low
                )
                right_candle.period += 1

                return right_candle

            elif right_candle.high < left_candle.high and \
                    right_candle.low < left_candle.low:
                right_candle.high = min(
                    right_candle.high,
                    ordinary_candle.high
                )
                right_candle.low = min(
                    right_candle.low,
                    ordinary_candle.low
                )
                right_candle.period += 1

                return right_candle

            else:
                raise ValueError(
                    f'两个合并K线（id: {left_candle.id}, {right_candle.id}）的高低关系出错。'
                )


def generate_fractal(left_candle: MergedCandle,
                     middle_candle: MergedCandle,
                     right_candle: MergedCandle,
                     last_fractal: Optional[Fractal],
                     strict_mode: bool = True
                     ) -> Optional[Fractal]:
    """
    Generate fractal.

    :param left_candle:
    :param middle_candle:
    :param right_candle:
    :param last_fractal:
    :param strict_mode:
    :return:
    """
    minimum_distance: int = 4 if strict_mode else 3

    # 判定分型。
    pattern: FractalPattern
    if middle_candle.high > left_candle.high and \
            middle_candle.high > right_candle.high:
        pattern = FractalPattern.Top

    elif middle_candle.low < left_candle.low and \
            middle_candle.low < right_candle.low:
        pattern = FractalPattern.Bottom

    elif left_candle.high < middle_candle.high < right_candle.high:
        return None

    elif left_candle.high > middle_candle.high > right_candle.high:
        return None

    else:
        raise RuntimeError('【ERROR】')

    if last_fractal is not None:
        # 判定模式。
        if pattern == last_fractal.pattern:
            return None

        # 判定距离。
        distance = middle_candle.id - last_fractal.merged_id
        if distance < minimum_distance:
            return None

    return Fractal(
        id=0 if last_fractal is None else last_fractal.id + 1,
        pattern=pattern,
        left_candle=left_candle,
        middle_candle=middle_candle,
        right_candle=right_candle,
        is_confirmed=False
    )
