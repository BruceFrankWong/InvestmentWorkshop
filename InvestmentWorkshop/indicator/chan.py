# -*- coding: utf-8 -*-

__author__ = 'Bruce Frank Wong'

"""

    Chan Theory

        Record data with pandas DataFrame, and align with common candlestick DataFrame.

"""


from typing import Dict, List, Tuple, Any, Sequence
from dataclasses import dataclass
from enum import Enum
import datetime as dt
from copy import deepcopy

import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import mplfinance as mpf


PriceRange = Tuple[float, float]


@dataclass
class CandlestickOrdinary:
    high: float
    low: float


@dataclass
class CandlestickChan(CandlestickOrdinary):
    period: int
    first: int
    last: int


class Fractal(Enum):
    Top = '顶分型'
    Bottom = '底分型'


def is_inclusive_number(c_h: float,
                        c_l: float,
                        p_h: float,
                        p_l: float) -> bool:
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

    :param c_h: float, HIGH price of current candlestick.
    :param c_l: float, LOW price of current candlestick.
    :param p_h: float, HIGH price of previous candlestick.
    :param p_l: float, LOW price of previous candlestick.

    ----
    :return: bool, if
    """
    if (c_h > p_h and c_l > p_l) or (c_h < p_h and c_l < p_l):
        return False
    else:
        return True


def is_inclusive_candle(candle_1: CandlestickOrdinary,
                        candle_2: CandlestickOrdinary
                        ) -> bool:
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

    :param candle_1: CandlestickOrdinary, candlestick 1.
    :param candle_2: CandlestickOrdinary, candlestick 2.

    ----
    :return: bool, if
    """
    if (
            (candle_1.high > candle_2.high and candle_1.low > candle_2.low) or
            (candle_1.high < candle_2.high and candle_1.low < candle_2.low)
    ):
        return False
    else:
        return True


def merge_candlestick(candlestick_chan: List[CandlestickChan],
                      candlestick_ordinary: CandlestickOrdinary
                      ) -> List[CandlestickChan]:
    """
    合并K线。
    """

    result: List[CandlestickChan] = deepcopy(candlestick_chan)

    # 本普通K线与前缠论K线之间，不存在包含关系：
    if not is_inclusive_number(
            candlestick_chan[-1].high,
            candlestick_chan[-1].low,
            candlestick_ordinary.high,
            candlestick_ordinary.low):

        # 新的缠论K线，高点 = 普通K线高点，低点 = 普通K线低点，周期 = 1，。
        new_candlestick: CandlestickChan = CandlestickChan(
            high=candlestick_ordinary.high,
            low=candlestick_ordinary.low,
            period=1,
            first=candlestick_chan[-1].last + 1,
            last=candlestick_chan[-1].last + 1
        )

        result.append(new_candlestick)

    # 如果存在包含：
    else:
        # 前1缠论K线的周期 + 1。
        candlestick_chan[-1].period += 1

        # 前1缠论K线所合并的普通K线，其末根的 idx。
        candlestick_chan[-1].last += 1

        # 前1缠论K线所合并的普通K线，其第一根的序号为0（从序号 0 开始的普通K线都被合并了），取前1缠论K线和本普通K线的最大范围。
        if candlestick_chan[-1].first == 0:
            candlestick_chan[-1].high = max(
                candlestick_chan[-1].high,
                candlestick_ordinary.high
            )
            candlestick_chan[-1].high = min(
                candlestick_chan[-1].low,
                candlestick_ordinary.low
            )
        # 前1缠论K线不是第一根缠论K线，判断前1缠论K线和前2缠论K线的方向。
        else:

            # 如果：
            #     前1缠论K线 与 前2缠论K线： 高点 > 高点 且 低点 > 低点，
            # 合并取 高-高。
            if (
                    candlestick_chan[-1].high > candlestick_chan[-2].high and
                    candlestick_chan[-1].low > candlestick_chan[-2].low
            ):
                candlestick_chan[-1].high = max(
                    candlestick_chan[-1].high,
                    candlestick_ordinary.high
                )
                candlestick_chan[-1].low = max(
                    candlestick_chan[-1].low,
                    candlestick_ordinary.low
                )

            # 如果：
            #     前1缠论K线 与 前2缠论K线： 高点 > 高点 且 低点 > 低点，
            # 合并取 低-低。
            elif (
                    candlestick_chan[-1].high < candlestick_chan[-2].high and
                    candlestick_chan[-1].low < candlestick_chan[-2].low
            ):
                candlestick_chan[-1].high = min(
                    candlestick_chan[-1].high,
                    candlestick_ordinary.high
                )
                candlestick_chan[-1].low = min(
                    candlestick_chan[-1].low,
                    candlestick_ordinary.low
                )

            # 其它情况判定为出错。
            else:
                print(
                    f'【ERROR】在合并K线时发生错误——未知的前K与前前K高低关系。\n'
                    f'前1高：{candlestick_chan[-1].high}，前2高：{candlestick_chan[-2].high}；\n'
                    f'前1低：{candlestick_chan[-1].low}，前2低：{candlestick_chan[-2].low}。'
                )

    # 返回新的缠论K线。
    return result


def print_debug_before(idx: int,
                       count: int,
                       candle_1: CandlestickOrdinary,
                       candle_2: CandlestickOrdinary) -> None:
    """
    Print information before processing each turn.
    :return:
    """

    width: int = len(str(count)) + 1
    msg_1: str = '%:>*'.format(width, idx)
    msg_2: str = '%:>*'.format(width, count)

    print(
        f'第 {msg_1} / {msg_2} （普通K线）轮：\n'
        f'    前K线（缠论K线）：idx = {idx - 1}, '
        f'高点 = {candle_1.high}, '
        f'低点 = {candle_1.low}\n'
        f'    本K线（普通K线）：idx = {idx}, '
        f'高点 = {candle_2.high}, '
        f'低点 = {candle_2.low}\n'
    )


def print_debug_after(candlestick_chan: List[CandlestickChan],
                      base_time: dt.datetime) -> None:
    """
    Print information after processing each turn.

    :param candlestick_chan:
    :param base_time:
    :return:
    """
    time_current: dt.datetime = dt.datetime.now()

    relation = '包含' if is_inclusive_candle(candlestick_chan[-1], candlestick_chan[-2]) else '非'
    count: int = len(candlestick_chan)
    print(f'    【本轮处理完毕】，用时 {time_current - base_time}。')
    print(f'\n')
    print(f'    K线关系：{relation}\n')
    print(f'    K线数量：{count}，')
    print(f'缠论高点：{candlestick_chan[-1].high}，')
    print(f'缠论低点：{candlestick_chan[-1].low}。')
    print(f'\n')
    print(
        f'    前1缠论K线：（首根）{candlestick_chan[-1].first} ～ （末根）{candlestick_chan[-1].last}，'
        f'周期：{candlestick_chan[-1].period}；'
    )
    if count >= 2:
        print(
            f'    前2缠论K线：（首根）{candlestick_chan[-2].first} ～ （末根）{candlestick_chan[-2].last}，'
            f'周期：{candlestick_chan[-2].period}；'
        )
    else:
        print('    前3缠论K线：  不存在；')
    if count >= 3:
        print(
            f'    前3缠论K线：（首根）{candlestick_chan[-3].first} ～ （末根）{candlestick_chan[-3].last}，'
            f'周期：{candlestick_chan[-3].period}。'
        )
    else:
        print('    前3缠论K线：  不存在。')


def theory_of_chan(df_origin: pd.DataFrame,
                   count: int = None,
                   debug: bool = False) -> List[CandlestickChan]:
    """
    处理K线合并。

    :param df_origin:
    :param count:
    :param debug:

    ----
    :return:
    """

    # 计时
    time_start: dt.datetime = dt.datetime.now()

    # ----------------------------------------
    # 声明变量类型。
    # ----------------------------------------
    candlestick_ordinary: CandlestickOrdinary
    candlestick_chan: List[CandlestickChan] = []

    # ----------------------------------------
    # 转化化 df_origin。
    # ----------------------------------------
    df_data: pd.DataFrame = df_origin.reset_index()

    # 添加第1根缠论K线。
    candlestick_chan.append(
        CandlestickChan(
            high=df_data.loc[0, 'high'],
            low=df_data.loc[0, 'low'],
            period=1,
            first=0,
            last=0
        )
    )

    for idx in range(1, count):
        candlestick_ordinary = CandlestickOrdinary(
            high=df_origin.loc[idx, 'high'].copy(),
            low=df_origin.loc[idx, 'low'].copy()
        )
        merge_candlestick(
            candlestick_chan=candlestick_chan,
            candlestick_ordinary=candlestick_ordinary
        )

        # ----------------------------------------
        # 打印 debug 信息。
        # ----------------------------------------
        if debug:
            print_debug_after(candlestick_chan, time_start)

    time_end: dt.datetime = dt.datetime.now()

    if debug:
        print(f'\n计算完成！\n总计花费： {time_end - time_start}')

    return candlestick_chan
