# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import datetime as dt

from .definition import (
    OrdinaryCandle,
    MergedCandle,
    MergedCandleList,
    FractalList,
    SegmentList,
)
from .utility import get_merged_candle_idx


def print_debug_before(idx: int,
                       count: int,
                       candle_previous: OrdinaryCandle,
                       candle_current: OrdinaryCandle) -> None:
    """
    Print information before processing each turn.
    :return:
    """

    width: int = len(str(count - 1)) + 1

    print(
        f'\n'
        f'【第 {idx:>{width}} / {count - 1:>{width}} 轮】（按普通K线编号）：\n'
        f'    前K线（合并K线）：idx = {idx - 1}, '
        f'高点 = {candle_previous.high}, '
        f'低点 = {candle_previous.low}\n'
        f'    本K线（普通K线）：idx = {idx}, '
        f'高点 = {candle_current.high}, '
        f'低点 = {candle_current.low}'
    )
    if idx == 0:
        print(
            f'\n'
            f'  ● 初始化完成。'
        )


def print_debug_after(candle_list: MergedCandleList,
                      fractal_list: FractalList,
                      segment_list: SegmentList,
                      base_time: dt.datetime) -> None:
    """
    Print information after processing each turn.

    :param candle_list:
    :param fractal_list:
    :param segment_list:
    :param base_time:
    :return:
    """
    time_current: dt.datetime = dt.datetime.now()

    print(f'\n  ● 处理完毕，用时 {time_current - base_time}。')

    candle_count: int = len(candle_list)
    print(f'    合并K线数量： {candle_count}。')

    candle: MergedCandle = candle_list[-1]
    print(
        f'      前1合并K线：自 {candle.first_ordinary_idx} 至 {candle.last_ordinary_idx}，'
        f'周期 = {candle_list[-1].period}；'
    )
    if candle_count >= 2:
        candle = candle_list[-2]
        print(
            f'      前2合并K线：自 {candle.first_ordinary_idx} 至 {candle.last_ordinary_idx}，'
            f'周期 = {candle_list[-2].period}；'
        )
    else:
        print('      前2合并K线：不存在；')
    if candle_count >= 3:
        candle = candle_list[-3]
        print(
            f'      前3合并K线：自 {candle.first_ordinary_idx} 至 {candle.last_ordinary_idx}，'
            f'周期 = {candle_list[-3].period}。'
        )
    else:
        print('      前3合并K线：不存在。')

    fractal_count: int = 0 if fractal_list is None else len(fractal_list)
    print(
        f'\n    分型数量： {fractal_count}。'
    )
    if fractal_count >= 1:
        fractal = fractal_list[-1]
        print(
            f'      分型(f-1)： type = {fractal.type_.value}，'
            f'分型 idx = {fractal.idx}，'
            f'普通K线 idx = {fractal.middle_candle.last_ordinary_idx}。'
        )
    else:
        print('      分型(f-1)：不存在。')
    if fractal_count >= 2:
        fractal = fractal_list[-2]
        print(
            f'      分型(f-2)： type = {fractal.type_.value}，'
            f'分型 idx = {fractal.idx}，'
            f'普通K线 idx = {fractal.middle_candle.last_ordinary_idx}。'
        )
    else:
        print('      分型(f-2)：不存在。')

    segment_count: int = 0 if segment_list is None else len(segment_list)
    print(
        f'\n    线段数量： {segment_count}。'
    )
    if segment_count >= 1:
        segment = segment_list[-1]
        print(
            f'      线段(s-1)： type = {segment.trend.value}，'
            f'普通K线 idx = {segment.left_fractal.middle_candle.last_ordinary_idx} ~ '
            f'{segment.right_fractal.middle_candle.last_ordinary_idx}，'
            f'共有分型 {len(segment.fractals)} 个，'
            f'分型 idx {segment.left_fractal.idx} ~ {segment.right_fractal.idx}，'
            f'最后一个分型 idx {segment.fractals[-1].idx}。'
        )
    else:
        print('      线段(s-1)：不存在。')
