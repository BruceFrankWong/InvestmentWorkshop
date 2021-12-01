# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Dict, List, Optional

import pandas as pd

from .definition import (
    LogLevel,
    Action,

    FractalPattern,
    Trend,

    OrdinaryCandle,
    MergedCandle,
    Fractal,
    Stroke,
    Segment,
    IsolationLine,
    Pivot,

    ChanTheory,
)
from .utility import (
    is_right_potential_fractal,
    is_overlap,
    generate_merged_candle,
    generate_fractal,
)
from .log_message import (
    log_event_new_turn,
    log_event_candle_generated,
    log_event_candle_updated,
    log_event_fractal_generated,
    log_event_fractal_updated,
    log_event_fractal_dropped,
    log_event_stroke_generated,
    log_event_stroke_updated,
    log_event_segment_generated,
    log_event_segment_extended,
    log_event_segment_expanded,
    log_event_isolation_line_generated,
    log_event_stroke_pivot_generated,
    log_event_stroke_pivot_extended,

    log_try_to_generate_fractal,
    log_try_to_update_fractal,
    log_try_to_generate_stroke,
    log_try_to_update_stroke,

    log_show_candles,

    log_failed_in_not_enough_merged_candles,
)


def generate_merged_candles_with_dataframe(df: pd.DataFrame,
                                           count: Optional[int] = None,
                                           log_level: LogLevel = LogLevel.Normal
                                           ) -> List[MergedCandle]:
    """
    Generate the merged candle list with pandas DataFrame.

    :param df: pandas DatFrame. The ordinary bar data.
    :param count: int. How many rows to calculate.
    :param log_level: bool. Print log if True.
    :return:
    """

    # Handle parameters.
    if count is None or count <= 0 or count > len(df):
        count = len(df)
    
    # Declare variables type.
    merged_candles: List[MergedCandle] = []
    ordinary_candle: OrdinaryCandle
    new_candle: MergedCandle

    old_candle_left: Optional[MergedCandle]
    old_candle_right: Optional[MergedCandle]

    for idx in range(count):
        log_event_new_turn(log_level, idx, count)
        
        ordinary_candle = OrdinaryCandle(
            high=df.iloc[idx].at['high'].copy(),
            low=df.iloc[idx].at['low'].copy()
        )

        if len(merged_candles) >= 2:
            old_candle_right = merged_candles[-1]
            old_candle_left = merged_candles[-2]
        elif len(merged_candles) == 1:
            old_candle_right = merged_candles[-1]
            old_candle_left = None
        else:
            old_candle_right = None
            old_candle_left = None

        new_candle = generate_merged_candle(
            ordinary_candle=ordinary_candle,
            last_candle=(old_candle_left, old_candle_right)
        )

        if old_candle_right is None or new_candle.id != old_candle_right.id:
            log_event_candle_generated(
                log_level=log_level,
                new_merged_candle=new_candle
            )

            merged_candles.append(new_candle)
        else:
            log_event_candle_updated(
                log_level=log_level,
                merged_candle=new_candle
            )

    return merged_candles


def _generate_fractal(left_candle: MergedCandle,
                      middle_candle: MergedCandle,
                      right_candle: MergedCandle,
                      new_fractal_id: int,
                      last_fractal: Optional[Fractal] = None,
                      determine_distance: bool = True,
                      minimum_distance: int = 4,
                      determine_pattern: bool = True,
                      verbose: bool = False
                      ) -> Optional[Fractal]:

    if verbose:
        print(
            f'\n  ○ 尝试生成分型：'
            f'\n    左侧合并K线 id（合并K线）= {left_candle.id}，'
            f'id（普通K线）= {left_candle.ordinary_id}，'
            f'最高价 = {left_candle.high}，最低价 = {left_candle.low}'
            f'\n    中间合并K线 id（合并K线）= {middle_candle.id}，'
            f'id（普通K线）= {middle_candle.ordinary_id}，'
            f'最高价 = {middle_candle.high}，最低价 = {middle_candle.low}'
            f'\n    右侧合并K线 id（合并K线）= {right_candle.id}，'
            f'id（普通K线）= {right_candle.ordinary_id}，'
            f'最高价 = {right_candle.high}，最低价 = {right_candle.low}'
        )

    # 判定距离。
    if determine_distance:
        distance = middle_candle.id - last_fractal.merged_id
        if distance < minimum_distance:
            if verbose:
                print(f'        新老分型的距离 = {distance}，< {minimum_distance}，不满足。')
            return
        else:
            if verbose:
                print(f'        新老分型的距离 = {distance}，>= {minimum_distance}，满足。')

    # 判定分型。
    pattern: FractalPattern
    if middle_candle.high > left_candle.high and \
            middle_candle.high > right_candle.high:
        if verbose:
            print('        中间合并K线的最高价 > 左右两侧合并K线的最高价，满足。')
        pattern = FractalPattern.Top

    elif middle_candle.low < left_candle.low and \
            middle_candle.low < right_candle.low:
        if verbose:
            print('        中间合并K线的最高价 < 左右两侧合并K线的最高价，满足。')
        pattern = FractalPattern.Bottom

    elif left_candle.high < middle_candle.high < right_candle.high:
        if verbose:
            print('        左侧合并K线的最高价 < 中间合并K线的最高价 < 右侧合并K线的最高价，不满足。')
        return

    elif left_candle.high > middle_candle.high > right_candle.high:
        if verbose:
            print('        左侧合并K线的最高价 > 中间合并K线的最高价 > 右侧合并K线的最高价，不满足。')
        return

    else:
        print('【ERROR】')
        return

    # 判定模式。
    if determine_pattern:
        if pattern == last_fractal.pattern:
            if verbose:
                print(f'        新分型的模式 = {pattern}，与前分型相同，不满足。')
            return
        else:
            if verbose:
                print(f'        新分型的模式 = {pattern}，与前分型不同，满足。')

    new_fractal: Fractal = Fractal(
        id=new_fractal_id,
        pattern=pattern,
        left_candle=left_candle,
        middle_candle=middle_candle,
        right_candle=right_candle,
        is_confirmed=False
    )

    return new_fractal


def generate_fractals(merged_candles: List[MergedCandle],
                      count: Optional[int] = None,
                      log_level: LogLevel = LogLevel.Normal
                      ) -> List[Fractal]:
    """
    Generate the fractal list.

    :param merged_candles:
    :param count:
    :param log_level:
    :return:
    """
    # Handle parameters.
    if count is None or count <= 0 or count > len(merged_candles):
        count = len(merged_candles)

    if len(merged_candles) == 0:
        raise RuntimeError(
            'No merged candle data, run <generate_merged_candles_with_dataframe> before.'
        )

    # Declare variables.
    fractals: List[Fractal] = []
    merged_candle: MergedCandle

    last_fractal: Fractal
    left_candle: MergedCandle
    middle_candle: MergedCandle
    right_candle: MergedCandle

    # 开始循环
    for idx in range(count):
        log_event_new_turn(log_level, idx, count)

        # 如果 fractal 列表的长度 >= 2，尝试修正分型
        if len(fractals) >= 2:
            # 最新的分型
            last_fractal = fractals[-1]
            # 最新的合并K线
            last_candle = merged_candles[idx]

            # log
            log_try_to_update_fractal(
                log_level=log_level,
                last_fractal=last_fractal,
                last_candle=last_candle
            )

            is_updated: bool = False

            # 如果当前合并K线顺向突破（即最高价大于顶分型中间K线的最高价，对底分型反之）。
            if last_fractal.pattern == FractalPattern.Top:
                if last_candle.high < last_fractal.middle_candle.high:
                    if log_level.value >= LogLevel.Detailed.value:
                        print(
                            ' ' * 8, f'最新合并K线的最高价 <= 最新笔的右侧价，不满足。'
                        )
                else:
                    is_updated = True
                    if log_level.value >= LogLevel.Detailed.value:
                        print(
                            ' ' * 8, f'最新合并K线的最高价 > 最新笔的右侧价，满足。'
                        )

            else:   # last_fractal.pattern == FractalPattern.Bottom
                if last_candle.low > last_fractal.middle_candle.low:
                    if log_level.value >= LogLevel.Detailed.value:
                        print(
                            ' ' * 8, f'最新合并K线的最高价 >= 最新笔的右侧价，不满足。'
                        )
                else:
                    is_updated = True
                    if log_level.value >= LogLevel.Detailed.value:
                        print(
                            ' ' * 8, f'最新合并K线的最高价 < 最新笔的右侧价，满足。'
                        )

            if is_updated:
                log_event_fractal_updated(
                    log_level=log_level,
                    old_fractal=last_fractal,
                    new_candle=last_candle
                )

                # 修正前分型。
                last_fractal.left_candle = merged_candles[last_candle.id - 1]
                last_fractal.middle_candle = last_candle
                last_fractal.right_candle = None
                last_fractal.is_confirmed = False

                continue

        # 生成新的分型。
        # 首个分型的标记是 last_fractal == None.
        # 第2个分型需要保证：
        #     1. 距离
        #     2. 分型模式与前分型不同

        # log
        log_try_to_generate_fractal(log_level=log_level)

        if idx < 3:
            log_failed_in_not_enough_merged_candles(log_level=log_level, count=idx)
            continue

        left_candle = merged_candles[idx - 2]
        middle_candle = merged_candles[idx - 1]
        right_candle = merged_candles[idx]
        last_fractal = fractals[-1] if len(fractals) > 0 else None

        log_show_candles(
            log_level=log_level,
            left_candle=left_candle,
            middle_candle=middle_candle,
            right_candle=right_candle
        )

        new_fractal = generate_fractal(
            left_candle=left_candle,
            middle_candle=middle_candle,
            right_candle=right_candle,
            last_fractal=last_fractal
        )

        if new_fractal is not None:
            if last_fractal is not None:
                last_fractal.is_confirmed = True
            fractals.append(new_fractal)
            log_event_fractal_generated(
                log_level=log_level,
                new_fractal=new_fractal
            )

    return fractals


def generate_strokes(merged_candles: List[MergedCandle],
                     count: Optional[int] = None,
                     log_level: LogLevel = LogLevel.Normal
                     ) -> List[Stroke]:
    """
    Generate stroke for Chan Theory.

    :param merged_candles:
    :param count:
    :param log_level:
    :return: List[Stroke].
    """

    # Handle parameters.
    if count is None or count <= 0 or count > len(merged_candles):
        count = len(merged_candles)

    if len(merged_candles) == 0:
        raise RuntimeError(
            'No merged candle data, run <generate_merged_candles_with_dataframe> before.'
        )

    # Declare variables.
    strokes: List[Stroke] = []
    merged_candle: MergedCandle

    last_stroke: Stroke
    left_candle: MergedCandle
    middle_candle: MergedCandle
    right_candle: MergedCandle

    previous_fractal: MergedCandle = merged_candles[0]
    current_fractal: MergedCandle

    # Loop.
    for idx in range(count):
        # Log new turn.
        log_event_new_turn(log_level, idx, count)

        # 如果 strokes 列表的长度 == 0，尝试生成首个笔。
        if len(strokes) == 0:
            # log
            log_try_to_generate_stroke(log_level=log_level)

            if idx == 1:
                log_failed_in_not_enough_merged_candles(log_level=log_level, count=idx)
                continue

            # Get the potential fractal (the last candle) pattern.
            is_potential_fractal: bool
            left_potential_fractal_pattern: FractalPattern
            right_potential_fractal_pattern: FractalPattern
            is_potential_fractal, right_potential_fractal_pattern = is_right_potential_fractal(
                merged_candles[-2],
                merged_candles[-1]
            )
            for i in range(1, idx):
                pass

        # 如果 strokes 列表的长度 >= 1，尝试修正笔。
        if len(strokes) >= 1:
            # 最新的笔
            last_stroke = strokes[-1]
            # 最新的合并K线
            last_candle = merged_candles[idx]

            # log
            log_try_to_update_stroke(log_level=log_level)

            is_updated: bool = False

            # 如果当前合并K线顺向突破（即最高价大于顶分型中间K线的最高价，对底分型反之）。
            if last_stroke.trend == Trend.Bullish:
                if last_candle.high < last_stroke.right_price:
                    if log_level.value >= LogLevel.Detailed.value:
                        print(
                            ' ' * 8, f'最新合并K线的最高价 <= 最新笔的右侧价，不满足。'
                        )
                else:
                    is_updated = True
                    if log_level.value >= LogLevel.Detailed.value:
                        print(
                            ' ' * 8, f'最新合并K线的最高价 > 最新笔的右侧价，满足。'
                        )

            else:  # last_stroke.trend == Trend.Bearish
                if last_candle.low > last_stroke.right_price:
                    if log_level.value >= LogLevel.Detailed.value:
                        print(
                            ' ' * 8, f'最新合并K线的最高价 >= 最新笔的右侧价，不满足。'
                        )
                else:
                    is_updated = True
                    if log_level.value >= LogLevel.Detailed.value:
                        print(
                            ' ' * 8, f'最新合并K线的最高价 < 最新笔的右侧价，满足。'
                        )

            if is_updated:
                log_event_stroke_updated(
                    log_level=log_level,
                    old_stroke=last_stroke,
                    new_candle=last_candle
                )

                # 修正最新的笔。
                last_stroke.right_candle = last_candle

                continue

        current_fractal = merged_candles[idx]
        if current_fractal.pattern == previous_fractal.pattern:
            continue
        trend: Trend
        if previous_fractal.pattern == FractalPattern.Bottom:
            trend = Trend.Bullish
        else:
            trend = Trend.Bearish

        new_stroke: Stroke = Stroke(
            id=len(strokes),
            trend=trend,
            left_candle=previous_fractal.middle_candle,
            right_candle=current_fractal.middle_candle
        )

        strokes.append(new_stroke)

        previous_fractal = current_fractal

    return strokes


def generate_segments(strokes: List[Stroke],
                      log_level: LogLevel = LogLevel.Normal
                      ) -> List[Segment]:
    """
    Generate segments for Chan Theory.

    :param strokes:
    :param log_level:
    :return:
    """
    if len(strokes) == 0:
        raise RuntimeError('No stroke data, run <generate_strokes> before.')

    if len(strokes) < 3:
        if verbose:
            print('Length of strokes less 3.')

    segments: List[Segment] = []

    for idx in range(2, len(strokes)):
        segments_count: int = 0 if segments is None else len(segments)

        # 如果 线段的数量 == 0，自前向后（自左向右）穷举 stroke，直到创建首根线段。
        if segments_count == 0:

            # 申明变量类型并赋值。
            left_stroke: Stroke = strokes[idx - 2]
            middle_stroke: Stroke = strokes[idx - 1]
            right_strokes: Stroke = strokes[idx]

            overlap_high: float
            overlap_low: float
            is_overlapping: bool

            # 重叠区域检测
            is_overlapping, overlap_high, overlap_low = is_overlap(left_stroke, right_strokes)

            # 如果：有重叠，创建首根线段。
            if is_overlapping:
                new_segment: Segment = Segment(
                    id=segments_count,
                    trend=left_stroke.trend,
                    left_candle=left_stroke.left_candle,
                    right_candle=right_strokes.right_candle,
                    stroke_id_list=[left_stroke.id, middle_stroke.id, right_strokes.id]
                )

                segments.append(new_segment)

                if log_level.value >= LogLevel.Normal.value:
                    print(
                        LOG_STROKE_GENERATED.format(
                            id=new_segment.id + 1,
                            trend=new_segment.trend,
                            left_mc_id=new_segment.left_merged_id,
                            right_mc_id=new_segment.right_merged_id,
                            left_oc_id=new_segment.left_ordinary_id,
                            right_oc_id=new_segment.right_ordinary_id
                        )
                    )

        # 如果 线段的数量 > 0：
        #     1. 延伸线段
        #     2. 反向线段
        #     3. 跳空线段
        else:
            # 申明变量类型并赋值。
            last_segment: Segment = segments[-1]
            last_stroke_in_segment: Stroke = strokes[last_segment.stroke_id_list[-1]]
            last_stroke: Stroke = strokes[idx]

            # 顺向突破，延伸线段。
            # 如果：
            #     A1. last_segment 的 trend 是 上升，且
            #     A3. last_stroke 的最高价 >= last_stroke_in_segment 的右侧价 （顺向超越或达到）：
            #   或
            #     B1. last_segment 的 trend 是 下降，且
            #     B3. last_stroke 的最低价 <= last_stroke_in_segment 的右侧价 （顺向超越或达到）：
            # 延伸（调整）笔。
            if last_stroke.trend == last_stroke_in_segment.trend and \
                    (
                            (
                                    last_stroke.trend == Trend.Bullish and
                                    last_stroke.right_price >= last_stroke_in_segment.right_price
                            ) or (
                                    last_stroke.trend == Trend.Bearish and
                                    last_stroke.right_price <= last_stroke_in_segment.right_price
                            )
                    ):

                log_event_segment_expanded(
                    log_level=log_level,
                    element_id=last_segment.id + 1,
                    trend=last_segment.trend,
                    old_mc_id=last_stroke_in_segment.right_merged_id,
                    new_mc_id=last_stroke.right_merged_id,
                    old_oc_id=last_stroke_in_segment.right_ordinary_id,
                    new_oc_id=last_stroke.right_ordinary_id,
                    strokes_changed=[
                        i for i in range(
                            last_stroke_in_segment.id + 1,
                            last_stroke.id + 1
                        )
                    ]
                )

                # 增加线段的笔。
                for i in range(last_segment.stroke_id_list[-1] + 1, last_stroke.id + 1):
                    last_segment.stroke_id_list.append(i)

                # 移动线段的右侧笔。
                last_segment.right_stroke = last_stroke

                continue

            # 反向突破，生成反向线段。
            if last_stroke.id - last_segment.stroke_id_list[-1] == 3:
                left_stroke: Stroke = strokes[-3]
                middle_stroke: Stroke = strokes[-2]
                right_stroke: Stroke = strokes[-1]

                # 如果：
                #     A1. 上升线段，且
                #     A2. 右侧笔的左侧价 < 左侧笔的左侧价，且
                #         （不新高）
                #     A3.
                #         A. 右侧笔的右侧价 <= 左侧笔的右侧价   （= 可以吗？）
                #           （创左侧笔的新低）
                #       或
                #         B. 左侧笔的右侧价 < 线段内右侧笔的左侧价
                #           （创线段内右侧笔的新低）
                #   或
                #     B1. 下降线段，且
                #     B2. 右侧笔的左侧价 > 左侧笔的左侧价，且
                #         （不新低）
                #     B3.
                #         A. 右侧笔的右侧价 >= 左侧笔的右侧价
                #           （创左侧笔的新高）
                #       或
                #         B. 左侧笔的右侧价 > 线段内右侧笔的左侧价
                #            （创线段内右侧笔的新高）
                # 生成反向线段。
                if (
                        last_segment.trend == Trend.Bullish and
                        right_stroke.trend == Trend.Bearish and
                        right_stroke.left_price < left_stroke.left_price and
                        (
                                right_stroke.right_price <= left_stroke.right_price
                                or
                                left_stroke.right_price < last_stroke_in_segment.left_price
                        )
                ) or (
                        last_segment.trend == Trend.Bearish and
                        right_stroke.trend == Trend.Bullish and
                        right_stroke.left_price > left_stroke.left_price and
                        (
                                right_stroke.right_price >= left_stroke.right_price
                                or
                                left_stroke.right_price > last_stroke_in_segment.left_price
                        )
                ):
                    new_segment = Segment(
                        id=segments_count,
                        trend=right_stroke.trend,
                        left_candle=left_stroke.left_candle,
                        right_candle=right_stroke.right_candle,
                        stroke_id_list=[left_stroke.id, middle_stroke.id, right_stroke.id]
                    )
                    segments.append(new_segment)

                    log_event_segment_generated(
                        log_level=log_level,
                        element_id=new_segment.id + 1,
                        trend=new_segment.trend,
                        left_mc_id=new_segment.left_merged_id,
                        right_mc_id=new_segment.left_merged_id,
                        left_oc_id=new_segment.left_ordinary_id,
                        right_oc_id=new_segment.right_ordinary_id,
                        strokes=new_segment.stroke_id_list
                    )

                    continue

            # 跳空生成线段。
            # 如果：
            #     A1. 上升线段，且
            #     A2. 右侧笔的左侧价 < 左侧笔的左侧价，且
            #         （不新高）
            #     A3.
            #         A. 右侧笔的右侧价 <= 左侧笔的右侧价   （= 可以吗？）
            #           （创左侧笔的新低）
            #       或
            #         B. 左侧笔的右侧价 < 线段内右侧笔的左侧价
            #           （创线段内右侧笔的新低）
            #   或
            #     B1. 下降线段，且
            #     B2. 右侧笔的左侧价 > 左侧笔的左侧价，且
            #         （不新低）
            #     B3.
            #         A. 右侧笔的右侧价 >= 左侧笔的右侧价
            #           （创左侧笔的新高）
            #       或
            #         B. 左侧笔的右侧价 > 线段内右侧笔的左侧价
            #            （创线段内右侧笔的新高）
            # 生成反向线段。
            if True:
                pass

    return segments


def generate_isolation_lines(chan: ChanTheory,
                             log_level: LogLevel = LogLevel.Normal
                             ) -> List[IsolationLine]:

    isolation_lines: List[IsolationLine] = []

    pass

    return isolation_lines


def generate_stroke_pivots(chan: ChanTheory,
                           log_level: LogLevel = LogLevel.Normal
                           ) -> List[Pivot]:

    stroke_pivots: List[Pivot] = []

    pass

    return stroke_pivots


def generate_segment_pivots(chan: ChanTheory,
                            log_level: LogLevel = LogLevel.Normal
                            ) -> List[Pivot]:

    segment_pivots: List[Pivot] = []

    pass

    return segment_pivots


def run_with_dataframe(df: pd.DataFrame,
                       count: int = 0,
                       strict_mode: bool = True,
                       log_level: LogLevel = LogLevel.Normal
                       ) -> ChanTheory:
    """
    Run with pandas DataFrame statically.

    :param df:
    :param count:
    :param strict_mode: bool. True means the distance between two fractals should be large than 5.
                        False means 4 at least.
    :param log_level:
    :return:
    """
    data_chan: ChanTheory = ChanTheory(strict_mode=strict_mode)

    ordinary_candle: OrdinaryCandle
    action: Action

    if log_level.value >= LogLevel.Normal.value:
        print('\n====================\n生成合并K线\n====================')
    data_chan._merged_candles = generate_merged_candles_with_dataframe(
        df=df,
        count=count,
        log_level=log_level
    )

    if log_level.value >= LogLevel.Normal.value:
        print('\n====================\n生成分型\n====================')
    data_chan._fractals = generate_fractals(data_chan.merged_candles, log_level=log_level)

    if log_level.value >= LogLevel.Normal.value:
        print('\n====================\n生成笔\n====================')
    data_chan._strokes = generate_strokes(data_chan.merged_candles, log_level=log_level)

    if log_level.value >= LogLevel.Normal.value:
        print('\n====================\n生成线段\n====================')
    data_chan._segments = generate_segments(data_chan.strokes, log_level=log_level)

    if log_level.value >= LogLevel.Normal.value:
        print('\n====================\n生成同级别分解线\n====================')
    data_chan._isolation_lines = generate_isolation_lines(data_chan.segments, log_level=log_level)

    if log_level.value >= LogLevel.Normal.value:
        print('\n====================\n生成笔中枢\n====================')
    data_chan = generate_stroke_pivots(data_chan, log_level=log_level)

    if log_level.value >= LogLevel.Normal.value:
        print('\n====================\n生成段中枢\n====================')
    data_chan = generate_segment_pivots(data_chan, log_level=log_level)

    return data_chan
