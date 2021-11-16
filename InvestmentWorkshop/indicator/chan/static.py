# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Dict, List, Optional

import pandas as pd

from .definition import (
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
    is_inclusive_candle,
    is_overlap
)
from .log_message import (
    LOG_CANDLE_GENERATED,
    LOG_CANDLE_UPDATED,
    LOG_FRACTAL_GENERATED,
    LOG_FRACTAL_DROPPED,
    LOG_STROKE_GENERATED,
    LOG_STROKE_EXTENDED,
    LOG_SEGMENT_GENERATED,
    LOG_SEGMENT_EXTENDED,
    LOG_SEGMENT_EXPANDED,
    LOG_ISOLATION_LINE_GENERATED,
    LOG_STROKE_PIVOT_GENERATED,
    LOG_STROKE_PIVOT_EXTENDED,
)


def update_merged_candles(
        df: pd.DataFrame,
        chan: ChanTheory,
        log: bool = False
) -> ChanTheory:
    """
    Update (generate or merge) merged candles for Chan Theory.

    :param df: pandas DatFrame. The ordinary bar data.
    :param chan: Chan. The Chan Theory data.
    :param log: bool. Print log if True.
    :return:
    """

    count: int = len(df)
    width: int = len(str(count - 1)) + 1

    merged_candles: List[MergedCandle] = []

    ordinary_candle: OrdinaryCandle

    new_merged_candle = MergedCandle(
        id=0,
        high=df.iloc[0].at['high'].copy(),
        low=df.iloc[0].at['low'].copy(),
        period=1,
        left_ordinary_id=0
    )

    if log:
        print(f'\n【第 {0:>{width}} / {count - 1:>{width}} 轮】（按普通K线编号）')
        print(
            LOG_CANDLE_GENERATED.format(
                id=new_merged_candle.id + 1,
                ordinary_id=new_merged_candle.left_ordinary_id,
                period=new_merged_candle.period,
                high=new_merged_candle.high,
                low=new_merged_candle.low
            )
        )

    merged_candles.append(new_merged_candle)

    for idx in range(1, count):
        if log:
            print(f'\n【第 {idx:>{width}} / {count - 1:>{width}} 轮】（按普通K线编号）')
        ordinary_candle = OrdinaryCandle(
            high=df.iloc[idx].at['high'].copy(),
            low=df.iloc[idx].at['low'].copy()
        )

        merged_candle_p1: MergedCandle = merged_candles[-1]

        # 如果没有包含关系：
        #     加入。
        if not is_inclusive_candle(merged_candle_p1, ordinary_candle):

            # 新的合并K线，高点 = 普通K线高点，低点 = 普通K线低点，周期 = 1，。
            new_merged_candle = MergedCandle(
                id=len(merged_candles),
                high=ordinary_candle.high,
                low=ordinary_candle.low,
                period=1,
                left_ordinary_id=merged_candles[-1].right_ordinary_id + 1,
            )

            if log:
                print(
                    LOG_CANDLE_GENERATED.format(
                        id=new_merged_candle.id + 1,
                        ordinary_id=new_merged_candle.right_ordinary_id,
                        period=new_merged_candle.period,
                        high=new_merged_candle.high,
                        low=new_merged_candle.low
                    )
                )

            merged_candles.append(new_merged_candle)

            continue

        # 如果存在包含：
        else:
            # 合并K线列表长度 == 1。
            if len(merged_candles) == 1:
                merged_candle_p1.high = max(
                    merged_candle_p1.high,
                    ordinary_candle.high
                )
                merged_candle_p1.low = min(
                    merged_candle_p1.low,
                    ordinary_candle.low
                )
                merged_candle_p1.period += 1

                if log:
                    print(
                        LOG_CANDLE_UPDATED.format(
                            id=new_merged_candle.id + 1,
                            ordinary_id=new_merged_candle.right_ordinary_id,
                            period=new_merged_candle.period,
                            high=new_merged_candle.high,
                            low=new_merged_candle.low
                        )
                    )

                continue

            # 前1合并K线不是第一根合并K线，判断前1合并K线和前2合并K线的方向。
            else:

                merged_candle_p2: MergedCandle = merged_candles[-2]

                # 如果：
                #     前1合并K线 与 前2合并K线： 高点 > 高点 且 低点 > 低点，
                # 合并取 高-高。
                if (
                        merged_candle_p1.high > merged_candle_p2.high and
                        merged_candle_p1.low > merged_candle_p2.low
                ):
                    merged_candle_p1.high = max(
                        merged_candle_p1.high,
                        ordinary_candle.high
                    )
                    merged_candle_p1.low = max(
                        merged_candle_p1.low,
                        ordinary_candle.low
                    )
                    merged_candle_p1.period += 1

                    if log:
                        print(
                            LOG_CANDLE_UPDATED.format(
                                id=new_merged_candle.id + 1,
                                ordinary_id=new_merged_candle.right_ordinary_id,
                                period=new_merged_candle.period,
                                high=new_merged_candle.high,
                                low=new_merged_candle.low
                            )
                        )

                    continue

                # 如果：
                #     前1合并K线 与 前2合并K线： 高点 > 高点 且 低点 > 低点，
                # 合并取 低-低。
                elif (
                        merged_candle_p1.high < merged_candle_p2.high and
                        merged_candle_p1.low < merged_candle_p2.low
                ):
                    new_merged_candle = MergedCandle(
                        id=merged_candle_p1.id,
                        high=min(
                            merged_candle_p1.high,
                            ordinary_candle.high
                        ),
                        low=min(
                            merged_candle_p1.low,
                            ordinary_candle.low
                        ),
                        period=merged_candle_p1.period + 1,
                        left_ordinary_id=merged_candle_p1.left_ordinary_id
                    )

                    merged_candle_p1.high = min(
                        merged_candle_p1.high,
                        ordinary_candle.high
                    )
                    merged_candle_p1.low = min(
                        merged_candle_p1.low,
                        ordinary_candle.low
                    )
                    merged_candle_p1.period += 1

                    if log:
                        print(
                            LOG_CANDLE_UPDATED.format(
                                id=new_merged_candle.id + 1,
                                ordinary_id=new_merged_candle.right_ordinary_id,
                                period=new_merged_candle.period,
                                high=new_merged_candle.high,
                                low=new_merged_candle.low
                            )
                        )

                    continue

                # 其它情况判定为出错。
                else:
                    raise RuntimeError(
                        f'Unexpected candles relationship. '
                        f'Length of merged_candles = {len(merged_candles)}'
                        f'左合并K线：id={merged_candles[-2].id}，'
                        f'high={merged_candles[-2].high}，low={merged_candles[-2].low}；'
                        f'右合并K线：id={merged_candles[-1].id}，'
                        f'high={merged_candles[-1].high}，low={merged_candles[-1].low}。'
                    )

    result: ChanTheory = chan
    result._merged_candles = merged_candles
    return chan


def update_fractals(
        chan: ChanTheory,
        log: bool = False,
        verbose: bool = False
) -> ChanTheory:
    """
    Update (generate, confirm or drop) fractals for Chan Theory.

    :param chan:
    :param log:
    :param verbose:
    :return:
    """
    if len(chan.merged_candles) == 0:
        raise RuntimeError('No merged candle data, run <generate_merged_candles> before.')

    if len(chan.merged_candles) < 3:
        if log:
            print('Length of merged candles less 3.')

    count: int = len(chan.merged_candles)
    width: int = len(str(count - 1)) + 1

    fractals: List[Fractal] = []
    merged_candle: MergedCandle

    if log:
        for idx in range(3):
            print(f'\n【第 {idx:>{width}} / {count - 1:>{width}} 轮】（按合并K线编号）')

    for idx in range(2, count):
        if log:
            print(f'\n【第 {idx:>{width}} / {count - 1:>{width}} 轮】（按合并K线编号）')

        fractal_count: int = 0 if fractals is None else len(fractals)
        last_fractal: Fractal = fractals[-1] if fractal_count >= 1 else None

        # ----------------------------------------
        # 丢弃 前分型。
        # ----------------------------------------

        # 如果分型数量 > 0 且 最新分型未确认：
        if fractal_count > 0 and last_fractal.is_confirmed is False:
            if verbose:
                print(
                    f'\n  ○ 尝试丢弃分型：'
                    f'\n    分型数量 > 0，最新分型 未被确认。'
                )

            is_dropped: bool = False
            last_merged_candle: MergedCandle = chan.merged_candles[idx]

            # 如果当前合并K线顺向突破（即最高价大于顶分型中间K线的最高价，对底分型反之）。
            if last_fractal.pattern == FractalPattern.Top and \
                    last_merged_candle.high >= last_fractal.middle_candle.high:
                is_dropped = True

            elif last_fractal.pattern == FractalPattern.Bottom and \
                    last_merged_candle.low <= last_fractal.middle_candle.low:
                is_dropped = True

            if is_dropped:
                if log:
                    print(
                        LOG_FRACTAL_DROPPED.format(
                            id=last_fractal.id,
                            pattern=last_fractal.pattern,
                            extreme_price=last_fractal.extreme_price
                        )
                    )
                # 丢弃前分型。
                fractals.remove(last_fractal)
                # 重新统计分型数量。
                fractal_count = len(fractals)
                # 重新索引前分型。
                last_fractal = fractals[-1] if fractal_count >= 1 else None

        # --------------------
        # 生成 分型。
        # --------------------
        new_fractal: Optional[Fractal] = None

        left_candle = chan.merged_candles[idx-2]
        middle_candle = chan.merged_candles[idx-1]
        right_candle = chan.merged_candles[idx]

        if middle_candle.high > left_candle.high and \
                middle_candle.high > right_candle.high:
            new_fractal = Fractal(
                id=fractal_count,
                pattern=FractalPattern.Top,
                left_candle=left_candle,
                middle_candle=middle_candle,
                right_candle=right_candle,
                is_confirmed=False
            )
        elif middle_candle.low < left_candle.low and \
                middle_candle.low < right_candle.low:
            new_fractal = Fractal(
                id=fractal_count,
                pattern=FractalPattern.Bottom,
                left_candle=left_candle,
                middle_candle=middle_candle,
                right_candle=right_candle,
                is_confirmed=False
            )

        if new_fractal is not None:

            # 如果这是第1个分型，加入列表。
            if fractal_count == 0:
                fractals.append(new_fractal)
                if log:
                    print(
                        LOG_FRACTAL_GENERATED.format(
                            id=fractal_count + 1,
                            pattern=new_fractal.pattern.value,
                            merged_id=middle_candle.id,
                            ordinary_id=middle_candle.ordinary_id
                        )
                    )

            # 这不是第1个分型：
            else:
                # 新生成的分型：
                #     1. 不能和前分型重复（中间K线一样） -> 和前分型有足够距离
                #     2. 不接受同向分型（除非极值跟大，但这样在前面就被丢弃了）
                #     3. 前分型未被确认的时候不接受反向分型 -> 取消确认一说。
                distance = new_fractal.middle_candle.id - last_fractal.middle_candle.id
                if distance >= 4:  # and new_fractal.type_ != last_fractal.type_:
                    last_fractal.is_confirmed = True
                    fractals.append(new_fractal)

                    if log:
                        print(
                            LOG_FRACTAL_GENERATED.format(
                                id=fractal_count + 1,
                                pattern=new_fractal.pattern.value,
                                merged_id=middle_candle.id,
                                ordinary_id=middle_candle.ordinary_id
                            )
                        )

    result: ChanTheory = chan
    result._fractals = fractals
    return result


def generate_strokes(
        chan: ChanTheory,
        log: bool = False,
        verbose: bool = False
) -> ChanTheory:
    """
    Generate stroke for Chan Theory.

    :param chan:
    :param log:
    :param verbose:
    :return: Chan.
    """
    if len(chan.fractals) == 0:
        raise RuntimeError('No fractal data, run <generate_fractals> before.')

    count: int = len(chan.fractals)
    width: int = len(str(count - 1)) + 1

    strokes: List[Stroke] = []

    for idx in range(1, count):
        if log:
            print(f'\n【第 {idx:>{width}} / {count - 1:>{width}} 轮】（按分型编号）')

        strokes_count: int = 0 if strokes is None else len(strokes)
        left_fractal: Fractal = chan.fractals[idx - 1]
        right_fractal: Fractal = chan.fractals[idx]
        trend: Trend
        if chan.fractals[idx - 1].pattern == FractalPattern.Bottom:
            trend = Trend.Bullish
        else:
            trend = Trend.Bearish

        new_stroke: Stroke = Stroke(
            id=strokes_count,
            trend=trend,
            left_candle=left_fractal.middle_candle,
            right_candle=right_fractal.middle_candle
        )

        strokes.append(new_stroke)

    result: ChanTheory = chan
    result._strokes = strokes
    return result


def generate_segments(
        chan: ChanTheory,
        log: bool = False,
        verbose: bool = False
) -> ChanTheory:
    """
    Generate segments for Chan Theory.

    :param chan:
    :param log:
    :param verbose:
    :return:
    """
    if len(chan.strokes) == 0:
        raise RuntimeError('No stroke data, run <generate_strokes> before.')

    if len(chan.strokes) < 3:
        if verbose:
            print('Length of strokes less 3.')

    segments: List[Segment] = []

    for idx in range(2, len(chan.strokes)):
        segments_count: int = 0 if segments is None else len(segments)

        # 如果 线段的数量 == 0，自前向后（自左向右）穷举 stroke，直到创建首根线段。
        if segments_count == 0:

            # 申明变量类型并赋值。
            left_stroke: Stroke = chan.strokes[idx - 2]
            middle_stroke: Stroke = chan.strokes[idx - 1]
            right_strokes: Stroke = chan.strokes[idx]

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

                if log:
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
            last_stroke_in_segment: Stroke = chan.strokes[last_segment.stroke_id_list[-1]]
            last_stroke: Stroke = chan.strokes[idx]

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

                if log:
                    print(
                        LOG_SEGMENT_EXPANDED.format(
                            id=last_segment.id + 1,
                            trend=last_segment.trend,
                            old_mc_id=last_stroke_in_segment.right_merged_id,
                            new_mc_id=last_stroke.right_merged_id,
                            old_oc_id=last_stroke_in_segment.right_ordinary_id,
                            new_oc_id=last_stroke.right_ordinary_id,
                            new_strokes=[
                                i for i in range(
                                    last_stroke_in_segment.id + 1,
                                    last_stroke.id + 1
                                )
                            ]
                        )
                    )

                # 增加线段的笔。
                for i in range(last_segment.stroke_id_list[-1] + 1, last_stroke.id + 1):
                    last_segment.stroke_id_list.append(i)

                # 移动线段的右侧笔。
                last_segment.right_stroke = last_stroke

                continue

            # 反向突破，生成反向线段。
            if last_stroke.id - last_segment.stroke_id_list[-1] == 3:
                left_stroke: Stroke = chan.strokes[-3]
                middle_stroke: Stroke = chan.strokes[-2]
                right_stroke: Stroke = chan.strokes[-1]

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

                    if log:
                        print(
                            LOG_SEGMENT_GENERATED.format(
                                id=new_segment.id + 1,
                                trend=new_segment.trend,
                                left=new_segment.left_ordinary_id,
                                right=new_segment.right_ordinary_id,
                                strokes=new_segment.stroke_id_list
                            )
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

    result: ChanTheory = chan
    result._segments = segments
    return result


def generate_isolation_lines(
        chan: ChanTheory,
        log: bool = False,
        verbose: bool = False
) -> ChanTheory:

    isolation_lines: List[IsolationLine] = []

    pass

    result: ChanTheory = chan
    result._isolation_lines = isolation_lines
    return result


def generate_stroke_pivots(
        chan: ChanTheory,
        log: bool = False,
        verbose: bool = False
) -> ChanTheory:

    stroke_pivots: List[Pivot] = []

    pass

    result: ChanTheory = chan
    result._stroke_pivots = stroke_pivots
    return result


def generate_segment_pivots(
        chan: ChanTheory,
        log: bool = False,
        verbose: bool = False
) -> ChanTheory:

    segment_pivots: List[Pivot] = []

    pass

    result: ChanTheory = chan
    result._segment_pivots = segment_pivots
    return result


log_settings: Dict[str, bool] = {
    'generate_merged_candles': False,
    'generate_fractals': False,
    'generate_strokes': False,
    'generate_segments': False,
    'generate_isolation_lines': False,
}


def run_with_dataframe(
        df: pd.DataFrame,
        strict_mode: bool = True,
        log: bool = False,
        verbose: bool = False
) -> ChanTheory:
    """
    Run with pandas DataFrame statically.

    :param df:
    :param strict_mode: bool. True means the distance between two fractals should be large than 5.
                        False means 4 at least.
    :param log:
    :param verbose:
    :return:
    """
    chan_static: ChanTheory = ChanTheory(strict_mode=strict_mode)

    ordinary_candle: OrdinaryCandle
    action: Action

    if log:
        print('\n====================\n生成合并K线\n====================')
    chan_static = update_merged_candles(df, chan_static, log)

    if log:
        print('\n====================\n生成分型\n====================')
    chan_static = update_fractals(chan_static, log, verbose)

    if log:
        print('\n====================\n生成笔\n====================')
    chan_static = generate_strokes(chan_static, log, verbose)

    if log:
        print('\n====================\n生成线段\n====================')
    chan_static = generate_segments(chan_static, log, verbose)

    if log:
        print('\n====================\n生成同级别分解线\n====================')
    chan_static = generate_isolation_lines(chan_static, log, verbose)

    if log:
        print('\n====================\n生成笔中枢\n====================')
    chan_static = generate_stroke_pivots(chan_static, log, verbose)

    if log:
        print('\n====================\n生成段中枢\n====================')
    chan_static = generate_segment_pivots(chan_static, log, verbose)

    return chan_static
