# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Tuple
import datetime as dt

import pandas as pd

from .definition import (
    OrdinaryCandle,
    MergedCandle,
    MergedCandleList,
    FractalList,
    SegmentList,
)
from .merge_candle import merge_candle
from .generate_fractal import generate_fractal
from .segment import generate_segment
from .debug import (
    print_debug_before,
    print_debug_after,
)


def theory_of_chan_2(df_origin: pd.DataFrame,
                     count: int = None,
                     debug: bool = False) -> Tuple[MergedCandleList,
                                                   FractalList,
                                                   SegmentList]:
    """
    缠论。

    :param df_origin:
    :param count:
    :param debug:

    ----
    :return:
    """

    # 计时
    time_start: dt.datetime = dt.datetime.now()

    # 声明变量类型。
    candle_current: OrdinaryCandle
    candle_previous: MergedCandle  # 最新缠论K线
    merged_candle_count: int  # 缠论K线数量

    # 初始化
    merged_candle_list: MergedCandleList = []
    fractal_list: FractalList = []
    segment_list: SegmentList = []

    # 转化化 df_origin。
    df_data: pd.DataFrame = df_origin.reset_index()

    # 初始化 candlestick_chan。
    candle_current = OrdinaryCandle(
        high=df_data.loc[0, 'high'].copy(),
        low=df_data.loc[0, 'low'].copy(),
    )
    candle_previous = MergedCandle(
        idx=0,
        high=candle_current.high,
        low=candle_current.low,
        period=1,
        first_ordinary_idx=0
    )
    merged_candle_list.append(
        candle_previous
    )

    # ----------------------------------------
    # 打印 debug 信息。
    # ----------------------------------------
    if debug:
        print_debug_before(
            idx=0,
            count=count,
            candle_previous=candle_previous,
            candle_current=candle_current
        )

    # 循环 df_data。
    for idx in range(1, count):

        # 当前普通K线。
        candle_current = OrdinaryCandle(
            high=df_data.loc[idx, 'high'].copy(),
            low=df_data.loc[idx, 'low'].copy()
        )

        candle_previous = merged_candle_list[-1]

        # ----------------------------------------
        # 打印 debug 信息。
        # ----------------------------------------
        if debug:
            print_debug_before(
                idx=idx,
                count=count,
                candle_previous=candle_previous,
                candle_current=candle_current
            )

        # 合并K线。
        merged_candle_list = merge_candle(
            merged_candle_list=merged_candle_list,
            ordinary_candle=candle_current,
            debug=debug
        )

        # 生成分型。
        fractal_list = generate_fractal(
            merged_candle_list=merged_candle_list,
            fractal_list=fractal_list,
            debug=debug
        )

        segment_list = generate_segment(
            segment_list=segment_list,
            fractal_list=fractal_list,
            debug=debug
        )

        # ----------------------------------------
        # 打印 debug 信息。
        # ----------------------------------------
        if debug:
            print_debug_after(
                candle_list=merged_candle_list,
                fractal_list=fractal_list,
                segment_list=segment_list,
                base_time=time_start
            )

    time_end: dt.datetime = dt.datetime.now()

    if debug:
        print(f'\n计算完成！\n总计花费： {time_end - time_start}')

    return merged_candle_list, fractal_list, segment_list
