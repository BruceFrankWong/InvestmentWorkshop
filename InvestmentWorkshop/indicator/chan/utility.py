# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List, Tuple, Optional

from .definition import (
    LogLevel,
    FirstOrLast,
    FractalPattern,
    Trend,

    OrdinaryCandle,
    MergedCandle,
    Fractal,
    Stroke,
    Segment,
)
from .log_message import (
    log_not_enough_merged_candles,
    log_show_fixed_side_candles_in_generating_stroke,
    log_show_fixed_side_pattern_in_generating_stroke,
    log_show_mobile_side_candles_in_generating_stroke,

    log_test_result_distance,
    log_test_result_fractal,
    log_test_result_fractal_pattern,
    log_test_result_price_range,
    log_test_result_price_break,
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


def is_fractal_pattern(left_candle: Optional[MergedCandle],
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


def is_overlap(left_stroke: Stroke,
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
                     candles: List[MergedCandle],
                     last_fractal: Optional[Fractal],
                     strict_mode: bool = True,
                     log_level: LogLevel = LogLevel.Normal
                     ) -> Optional[Fractal]:
    """
    Generate a single fractal.

    The two fractals should be:
    1. the distance between the two candles in the middle of each fractal,
       should be equal to the <minimum_distance>, or larger than it.
    2. the pattern of each fractal, should be different.
    3. the low price of the bottom fractal, should be the last lowest one,
       or the last second-lowest one.
    4. the high price of the bottom fractal, should be the last highest one,
       or the last second-highest one.

    :param left_candle:
    :param middle_candle:
    :param right_candle:
    :param candles:
    :param last_fractal:
    :param strict_mode:
    :param log_level:
    :return:
    """
    minimum_distance: int = 4 if strict_mode else 3

    count: int = len(candles)
    if count < minimum_distance:
        log_not_enough_merged_candles(
            log_level=log_level,
            count=count,
            required=minimum_distance
        )
        return None

    # Generate the first pair of fractals.
    if last_fractal is None:
        pass

    # The next fractal.
    else:
        # Test: distance.
        # <distance> should be equal to or larger than <minimum_distance>.
        distance = candles[-1].id - last_fractal.merged_id
        if distance < minimum_distance:
            return None

        # Test: fractal.
        new_fractal_pattern: Optional[FractalPattern]
        if middle_candle.high > left_candle.high and \
                middle_candle.high > right_candle.high:
            new_fractal_pattern = FractalPattern.Top

        elif middle_candle.low < left_candle.low and \
                middle_candle.low < right_candle.low:
            new_fractal_pattern = FractalPattern.Bottom

        elif left_candle.high < middle_candle.high < right_candle.high:
            new_fractal_pattern = None

        elif left_candle.high > middle_candle.high > right_candle.high:
            new_fractal_pattern = None

        else:
            raise RuntimeError('【ERROR】')

        if new_fractal_pattern is None:
            return None

        # Test: fractal pattern.
        if last_fractal is not None:
            if new_fractal_pattern == last_fractal.pattern:
                return None

    # Test: price in range.
    # Price of candles between the two fractals, should not reach or beyond the price of fractals.

    return Fractal(
        id=0 if last_fractal is None else last_fractal.id + 1,
        pattern=new_fractal_pattern,
        left_candle=left_candle,
        middle_candle=middle_candle,
        right_candle=right_candle,
        is_confirmed=False
    )


"""
    关于笔。
    
    笔是几何学中的线段（不是缠论中的线段），其性质：
    1. 至少包含5个合并K线。
       两个分型之间的距离（以构成分型的三根合并K线中居中的那根计算）应大于等于 <最小距离>。
    2. 两个端点都是缠论中的分型，且两个分型的类型不同。
    3. 两个端点之间的合并K线，其价格不应超过分型的价格。
"""


def try_to_generate_first_stroke(candles: List[MergedCandle],
                                 strict_mode: bool = True,
                                 log_level: LogLevel = LogLevel.Normal
                                 ) -> Optional[Stroke]:
    """
    生成首根笔。
    对于首根笔，右侧为固定端，左侧为移动端。
    从左到右（从最大距离到最小距离）进行循环，尝试组合出符合条件的两个分型构成笔。
    如失败，下一次运行本函数时会有新的合并K线加入（即固定端右移），再次从远端尝试构成笔。

    :param candles:
    :param strict_mode:
    :param log_level:
    :return:
    """
    # Handle parameters.
    minimum_distance: int = 4 if strict_mode else 3

    count: int = len(candles)
    if count < minimum_distance + 1:
        log_not_enough_merged_candles(
            log_level=log_level,
            count=count,
            required=minimum_distance + 1
        )
        return None

    # Declare fixed side variables.
    fixed_side_left_candle: MergedCandle = candles[-2]
    fixed_side_middle_candle: MergedCandle = candles[-1]
    fixed_side_right_candle: Optional[MergedCandle] = None
    fixed_side_fractal_pattern: FractalPattern = is_fractal_pattern(
        left_candle=fixed_side_left_candle,
        middle_candle=fixed_side_middle_candle,
        right_candle=fixed_side_right_candle
    )

    # Log right side candles.
    log_show_fixed_side_candles_in_generating_stroke(
        log_level=log_level,
        left_candle=fixed_side_left_candle,
        middle_candle=fixed_side_middle_candle,
        fractal_pattern=fixed_side_right_candle
    )

    # Declare mobile side variables.
    mobile_side_left_candle: Optional[MergedCandle]
    mobile_side_middle_candle: MergedCandle
    mobile_side_right_candle: MergedCandle
    mobile_side_fractal_patter: Optional[FractalPattern]

    # Loop.
    # Keep the distance between the two fractal is equal to or larger than the <minimum_distance>.
    for i in range(1, count - minimum_distance):
        # Get left side candles.
        if i == 1:
            mobile_side_left_candle = None
            mobile_side_middle_candle = candles[i - 1]
            mobile_side_right_candle = candles[i]
        else:
            mobile_side_left_candle = candles[i - 2]
            mobile_side_middle_candle = candles[i - 1]
            mobile_side_right_candle = candles[i]

        # Log left side candles.
        log_show_mobile_side_candles_in_generating_stroke(
            log_level=log_level,
            left_candle=mobile_side_left_candle,
            middle_candle=mobile_side_middle_candle,
            right_candle=mobile_side_right_candle
        )

        # Test: fractal generation.
        # the left side candles should generate a fractal.
        mobile_side_fractal_patter = is_fractal_pattern(
            left_candle=mobile_side_left_candle,
            middle_candle=mobile_side_middle_candle,
            right_candle=mobile_side_right_candle
        )

        # Log fractal generation test result.
        log_test_result_fractal(
            log_level=log_level,
            fractal_pattern=mobile_side_fractal_patter
        )

        # If failed in fractal generation test, go to the next loop.
        if mobile_side_fractal_patter is None:
            continue

        # Test: fractal pattern different.
        # the pattern of left side fractal should be different with the right side.

        # Log fractal pattern test result.
        log_test_result_fractal_pattern(
            log_level=log_level,
            left_fractal_pattern=fixed_side_fractal_pattern,
            right_fractal_pattern=mobile_side_fractal_patter
        )

        # If failed in fractal pattern test, go to the next loop.
        if mobile_side_fractal_patter == fixed_side_fractal_pattern:
            continue

        # Test: price.
        # price of candles in the two fractals, should not reach or beyond the price of fractals.
        price_low: float
        price_high: float
        if fixed_side_fractal_pattern == FractalPattern.Top:
            price_low = mobile_side_middle_candle.low
            price_high = fixed_side_middle_candle.high
        else:
            price_low = fixed_side_middle_candle.low
            price_high = mobile_side_middle_candle.high

        is_price_break_high: bool = False
        is_price_break_low: bool = False
        cursor_candle: MergedCandle
        price_break_candle: Optional[MergedCandle] = None
        for j in range(mobile_side_middle_candle.id + 1, fixed_side_middle_candle.id):
            cursor_candle = candles[j]
            if cursor_candle.low < price_low:
                is_price_break_low = True
                price_break_candle = cursor_candle
                break
            if cursor_candle.high > price_high:
                is_price_break_high = True
                price_break_candle = cursor_candle
                break

        # Log price in range test result.
        log_test_result_price_range(
            log_level=log_level,
            break_high=is_price_break_high,
            break_low=is_price_break_low,
            candle=price_break_candle
        )

        # If failed in price in range test, go to the next loop.
        if is_price_break_high or is_price_break_low:
            continue

        # Generate the stroke.
        trend: Trend
        if fixed_side_fractal_pattern == FractalPattern.Bottom:
            trend = Trend.Bullish
        else:
            trend = Trend.Bearish

        # Return the new stroke.
        return Stroke(
            id=0,
            trend=trend,
            left_candle=mobile_side_middle_candle,
            right_candle=fixed_side_middle_candle
        )


def generate_following_stroke(candles: List[MergedCandle],
                              last_stroke: Stroke,
                              strict_mode: bool = True,
                              log_level: LogLevel = LogLevel.Normal
                              ) -> Optional[Stroke]:
    """
    生成后续笔。
    对于后续笔，左侧为固定端（既有笔的右侧），右侧为移动端。且无需循环，用最新的合并K线尝试是否可以构成笔。

    :param candles:
    :param last_stroke:
    :param strict_mode:
    :param log_level:
    :return:
    """
    # Handle parameters.
    minimum_distance: int = 4 if strict_mode else 3

    count: int = len(candles)
    if count < minimum_distance + 1:
        log_not_enough_merged_candles(
            log_level=log_level,
            count=count,
            required=minimum_distance + 1
        )
        return None

    # Declare fixed side variables.
    fixed_side_middle_candle: MergedCandle = last_stroke.right_candle
    fixed_side_fractal_pattern: FractalPattern
    if last_stroke.trend == Trend.Bullish:
        fixed_side_fractal_pattern = FractalPattern.Top
    else:
        fixed_side_fractal_pattern = FractalPattern.Bottom

    # Log right side candles.
    log_show_fixed_side_pattern_in_generating_stroke(
        log_level=log_level,
        middle_candle=fixed_side_middle_candle,
        fractal_pattern=fixed_side_fractal_pattern
    )

    # Declare mobile side variables.
    mobile_side_left_candle: Optional[MergedCandle]
    mobile_side_middle_candle: MergedCandle
    mobile_side_right_candle: MergedCandle
    mobile_side_fractal_patter: Optional[FractalPattern]

    # Start loop.
    # Keep the distance between the two fractal is equal to or larger than the <minimum_distance>.
    for i in range(count, minimum_distance, -1):
        # Get left side candles.
        if i == 1:
            mobile_side_left_candle = None
            mobile_side_middle_candle = candles[i - 1]
            mobile_side_right_candle = candles[i]
        else:
            mobile_side_left_candle = candles[i - 2]
            mobile_side_middle_candle = candles[i - 1]
            mobile_side_right_candle = candles[i]

        # Log left side candles.
        log_show_mobile_side_candles_in_generating_stroke(
            log_level=log_level,
            left_candle=mobile_side_left_candle,
            middle_candle=mobile_side_middle_candle,
            right_candle=mobile_side_right_candle
        )

        # Test: fractal generation.
        # the mobile side candles should generate a fractal.
        mobile_side_fractal_patter = is_fractal_pattern(
            left_candle=mobile_side_left_candle,
            middle_candle=mobile_side_middle_candle,
            right_candle=mobile_side_right_candle
        )

        # Log fractal generation test result.
        log_test_result_fractal(
            log_level=log_level,
            fractal_pattern=mobile_side_fractal_patter
        )

        # If failed in fractal generation test, go to the next loop.
        if mobile_side_fractal_patter is None:
            continue

        # Test: fractal pattern different.
        # the pattern of left side fractal should be different with the right side.

        # Log fractal pattern test result.
        log_test_result_fractal_pattern(
            log_level=log_level,
            left_fractal_pattern=fixed_side_fractal_pattern,
            right_fractal_pattern=mobile_side_fractal_patter
        )

        # If failed in fractal pattern test, go to the next loop.
        if mobile_side_fractal_patter == fixed_side_fractal_pattern:
            continue

        # Test: price.
        # price of candles in the two fractals, should not reach or beyond the price of fractals.
        price_low: float
        price_high: float
        if fixed_side_fractal_pattern == FractalPattern.Top:
            price_low = mobile_side_middle_candle.low
            price_high = fixed_side_middle_candle.high
        else:
            price_low = fixed_side_middle_candle.low
            price_high = mobile_side_middle_candle.high

        is_price_break_high: bool = False
        is_price_break_low: bool = False
        cursor_candle: MergedCandle
        price_break_candle: Optional[MergedCandle] = None
        for j in range(mobile_side_middle_candle.id + 1, fixed_side_middle_candle.id):
            cursor_candle = candles[j]
            if cursor_candle.low < price_low:
                is_price_break_low = True
                price_break_candle = cursor_candle
                break
            if cursor_candle.high > price_high:
                is_price_break_high = True
                price_break_candle = cursor_candle
                break

        # Log price in range test result.
        log_test_result_price_range(
            log_level=log_level,
            break_high=is_price_break_high,
            break_low=is_price_break_low,
            candle=price_break_candle
        )

        # If failed in price in range test, go to the next loop.
        if is_price_break_high or is_price_break_low:
            continue

        # Generate the stroke.
        trend: Trend
        if fixed_side_fractal_pattern == FractalPattern.Bottom:
            trend = Trend.Bullish
        else:
            trend = Trend.Bearish

        # Return the new stroke.
        return Stroke(
            id=last_stroke.id + 1,
            trend=trend,
            left_candle=fixed_side_middle_candle,
            right_candle=mobile_side_middle_candle
        )


def generate_stroke(candles: List[MergedCandle],
                    last_stroke: Optional[Stroke] = None,
                    strict_mode: bool = True,
                    log_level: LogLevel = LogLevel.Normal
                    ) -> Optional[Stroke]:
    """
    Generate a single stroke.

    A stroke is a segment (on Geometry, not Chan Theory), and each endpoint is a fractal.
    The two fractals should be:
    1. the distance between the two candles in the middle of each fractal,
       should be equal to the <minimum_distance>, or larger than it.
    2. the pattern of each fractal, should be different.
    3. the low price of the bottom fractal, should be the last lowest one,
       or the last second-lowest one.
    4. the high price of the bottom fractal, should be the last highest one,
       or the last second-highest one.

    :param candles:
    :param last_stroke:
    :param strict_mode:
    :param log_level:
    :return:
    """
    minimum_distance: int = 4 if strict_mode else 3

    count: int = len(candles)
    if count < minimum_distance + 1:
        log_not_enough_merged_candles(
            log_level=log_level,
            count=count,
            required=minimum_distance + 1
        )
        return None

    # Declare fixed side variables.
    fixed_side_left_candle: Optional[MergedCandle]
    fixed_side_middle_candle: MergedCandle
    fixed_side_right_candle: Optional[MergedCandle]
    fixed_side_fractal_pattern: Optional[FractalPattern]

    # Assign value for fixed side variables.
    if last_stroke is None:
        fixed_side_left_candle = candles[-2]
        fixed_side_middle_candle = candles[-1]
        fixed_side_right_candle = None
        fixed_side_fractal_pattern = is_fractal_pattern(
            left_candle=fixed_side_left_candle,
            middle_candle=fixed_side_middle_candle,
            right_candle=fixed_side_right_candle
        )
    else:
        fixed_side_left_candle = None
        fixed_side_middle_candle = last_stroke.right_candle
        fixed_side_right_candle = None
        if last_stroke.trend == Trend.Bullish:
            fixed_side_fractal_pattern = FractalPattern.Top
        else:
            fixed_side_fractal_pattern = FractalPattern.Bottom

    # Log fixed side candles and fractal pattern.
    if last_stroke is None:
        log_show_fixed_side_candles_in_generating_stroke(
            log_level=log_level,
            left_candle=fixed_side_left_candle,
            middle_candle=fixed_side_middle_candle,
            fractal_pattern=fixed_side_fractal_pattern
        )
    else:
        log_show_fixed_side_pattern_in_generating_stroke(
            log_level=log_level,
            middle_candle=fixed_side_middle_candle,
            fractal_pattern=fixed_side_fractal_pattern
        )

    # Declare fixed side variables.
    mobile_side_left_candle: Optional[MergedCandle]
    mobile_side_middle_candle: MergedCandle
    mobile_side_right_candle: Optional[MergedCandle]
    mobile_side_fractal_patter: Optional[FractalPattern]

    # Declare variables for loop control.
    loop_start: int
    loop_end: int
    loop_step: int

    if last_stroke is None:
        loop_start = 1
        loop_end = count - minimum_distance
        loop_step = 1
    else:
        loop_start = count
        loop_end = minimum_distance
        loop_step = -1

    # Loop.
    for i in range(loop_start, loop_end, loop_step):
        # Get left side candles.
        if i == 1:
            mobile_side_left_candle = None
            mobile_side_middle_candle = candles[i - 1]
            mobile_side_right_candle = candles[i]
        else:
            mobile_side_left_candle = candles[i - 2]
            mobile_side_middle_candle = candles[i - 1]
            mobile_side_right_candle = candles[i]

        # Log mobile side candles.
        log_show_mobile_side_candles_in_generating_stroke(
            log_level=log_level,
            left_candle=mobile_side_left_candle,
            middle_candle=mobile_side_middle_candle,
            right_candle=mobile_side_right_candle
        )

        # Test: fractal generation.
        # the left side candles should generate a fractal.
        mobile_side_fractal_patter = is_fractal_pattern(
            left_candle=mobile_side_left_candle,
            middle_candle=mobile_side_middle_candle,
            right_candle=mobile_side_right_candle
        )

        # Log fractal generation test result.
        log_test_result_fractal(
            log_level=log_level,
            fractal_pattern=mobile_side_fractal_patter
        )

        # If failed in fractal generation test, go to the next loop.
        if mobile_side_fractal_patter is None:
            continue

        # Test:
        # the pattern of left side fractal should be different with the right side.

        # Log fractal pattern test result.
        log_test_result_fractal_pattern(
            log_level=log_level,
            left_fractal_pattern=fixed_side_fractal_pattern,
            right_fractal_pattern=mobile_side_fractal_patter
        )

        # If failed in fractal pattern test, go to the next loop.
        if fixed_side_fractal_pattern == mobile_side_fractal_patter:
            continue

        # Test:
        # price of candles in the two fractals, should not reach or beyond the price of fractals.
        price_low: float = min(fixed_side_middle_candle.low, mobile_side_middle_candle.low)
        price_high: float = max(fixed_side_middle_candle.high, mobile_side_middle_candle.high)

        is_price_break_high: bool = False
        is_price_break_low: bool = False
        candle: MergedCandle
        price_break_candle: Optional[MergedCandle] = None
        for j in range(fixed_side_middle_candle.id + 1, mobile_side_middle_candle.id, loop_step):
            candle = candles[j]
            if candle.low < price_low:
                is_price_break_low = True
                price_break_candle = candle
                break
            if candle.high > price_high:
                is_price_break_high = True
                price_break_candle = candle
                break

        # Log price in range test result.
        log_test_result_price_range(
            log_level=log_level,
            break_high=is_price_break_high,
            break_low=is_price_break_low,
            candle=price_break_candle
        )

        # If failed in price in range test, go to the next loop.
        if is_price_break_high or is_price_break_low:
            continue

        # Generate the stroke.
        return Stroke(
            id=0 if last_stroke is None else last_stroke.id + 1,
            trend=Trend.Bullish if fixed_side_fractal_pattern == FractalPattern.Bottom
            else Trend.Bearish,
            left_candle=fixed_side_middle_candle,
            right_candle=mobile_side_middle_candle
        )
