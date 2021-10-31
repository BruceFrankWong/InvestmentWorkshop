# -*- coding: utf-8 -*-

__author__ = 'Bruce Frank Wong'

"""

    Chan Theory

        Record data with pandas DataFrame, and align with common candlestick DataFrame.

"""


from typing import Dict, List, Tuple, Any, Sequence, Optional, Union
from dataclasses import dataclass
from enum import Enum
import datetime as dt
from copy import deepcopy

import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import mplfinance as mpf


class FractalType(Enum):
    Top = '顶分型'
    Bottom = '底分型'


class TrendType(Enum):
    Up = '上升'
    Down = '下降'
    Bullish = '上升'
    Bearish = '下降'


@dataclass
class CandlestickOrdinary:
    high: float
    low: float


@dataclass
class CandlestickChan(CandlestickOrdinary):
    period: int
    first: int
    last: int


@dataclass
class Fractal:
    type_: FractalType
    idx: int
    left: Optional[CandlestickChan]
    middle: CandlestickChan
    right: CandlestickChan


CandlestickChanList = List[CandlestickChan]
FractalList = List[Fractal]


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


def is_inclusive_candle(candle_1: CandlestickOrdinary,
                        candle_2: CandlestickOrdinary
                        ) -> bool:
    """
    判断两根K线是否存在包含关系。两根K线的关系有以下九种：

    :param candle_1: CandlestickOrdinary, candlestick 1.
    :param candle_2: CandlestickOrdinary, candlestick 2.

    ----
    :return: bool, if
    """

    return is_inclusive_number(
        candle_1.high,
        candle_1.low,
        candle_2.high,
        candle_2.low
    )


def is_fractal_top(candle_l: CandlestickChan,
                   candle_m: CandlestickChan,
                   candle_r: CandlestickChan
                   ) -> bool:
    if candle_m.high == max(candle_l.high, candle_m.high, candle_r.high):
        return True
    else:
        return False


def is_fractal_bottom(candle_l: CandlestickChan,
                      candle_m: CandlestickChan,
                      candle_r: CandlestickChan
                      ) -> bool:
    if candle_m.low == min(candle_l.low, candle_m.low, candle_r.low):
        return True
    else:
        return False


def is_fractal(candle_l: CandlestickChan,
               candle_m: CandlestickChan,
               candle_r: CandlestickChan
               ) -> Tuple[bool, Optional[FractalType]]:
    if is_fractal_top(candle_l, candle_m, candle_r):
        return True, FractalType.Top
    elif is_fractal_bottom(candle_l, candle_m, candle_r):
        return True, FractalType.Bottom
    else:
        return False, None


def get_trend(candle_l: CandlestickChan,
              candle_r: CandlestickOrdinary
              ) -> TrendType:
    if candle_r.high > candle_l.high and candle_r.low > candle_l.low:
        return TrendType.Bullish
    elif candle_r.high < candle_l.high and candle_r.low < candle_l.low:
        return TrendType.Bearish
    else:
        raise RuntimeError('缠论K线不应存在包含关系。')


def merge_candlestick(candlestick_chan_list: List[CandlestickChan],
                      candlestick_ordinary: CandlestickOrdinary,
                      debug: bool = False
                      ) -> List[CandlestickChan]:
    """
    合并K线。
    """

    result: List[CandlestickChan] = deepcopy(candlestick_chan_list)

    is_inclusive: bool = is_inclusive_candle(
        candlestick_chan_list[-1],
        candlestick_ordinary
    )

    # 本普通K线与前缠论K线之间，不存在包含关系：
    if not is_inclusive:

        # 新的缠论K线，高点 = 普通K线高点，低点 = 普通K线低点，周期 = 1，。
        result.append(
            CandlestickChan(
                high=candlestick_ordinary.high,
                low=candlestick_ordinary.low,
                period=1,
                first=candlestick_chan_list[-1].last + 1,
                last=candlestick_chan_list[-1].last + 1
            )
        )

    # 如果存在包含：
    else:
        # 前1缠论K线的周期 + 1。
        result[-1].period += 1

        # 前1缠论K线所合并的普通K线，其末根的 idx。
        result[-1].last += 1

        # 前1缠论K线所合并的普通K线，其第一根的序号为0（从序号 0 开始的普通K线都被合并了），取前1缠论K线和本普通K线的最大范围。
        if result[-1].first == 0:
            result[-1].high = max(
                result[-1].high,
                candlestick_ordinary.high
            )
            result[-1].low = min(
                result[-1].low,
                candlestick_ordinary.low
            )
        # 前1缠论K线不是第一根缠论K线，判断前1缠论K线和前2缠论K线的方向。
        else:

            # 如果：
            #     前1缠论K线 与 前2缠论K线： 高点 > 高点 且 低点 > 低点，
            # 合并取 高-高。
            if (
                    result[-1].high > result[-2].high and
                    result[-1].low > result[-2].low
            ):
                result[-1].high = max(
                    result[-1].high,
                    candlestick_ordinary.high
                )
                result[-1].low = max(
                    result[-1].low,
                    candlestick_ordinary.low
                )

            # 如果：
            #     前1缠论K线 与 前2缠论K线： 高点 > 高点 且 低点 > 低点，
            # 合并取 低-低。
            elif (
                    result[-1].high < result[-2].high and
                    result[-1].low < result[-2].low
            ):
                result[-1].high = min(
                    result[-1].high,
                    candlestick_ordinary.high
                )
                result[-1].low = min(
                    result[-1].low,
                    candlestick_ordinary.low
                )

            # 其它情况判定为出错。
            else:
                print(
                    f'【ERROR】在合并K线时发生错误——未知的前K与前前K高低关系。\n'
                    f'前1高：{result[-1].high}，前2高：{result[-2].high}；\n'
                    f'前1低：{result[-1].low}，前2低：{result[-2].low}。'
                )

    if debug:
        print(
            f'\n    合并K线：\n'
            f'        K线关系：{"包含" if is_inclusive else "非包含"}\n'
            f'        当前缠论K线：高点 = {result[-1].high}，低点 = {result[-1].low}。'
        )

    # 返回新的缠论K线。
    return result


def update_fractal(candlestick_chan_list: List[CandlestickChan],
                   fractal_list: FractalList,
                   debug: bool = False
                   ) -> Optional[FractalList]:

    result: FractalList = deepcopy(fractal_list)

    # 缠论K线 1 根或更少。
    if len(candlestick_chan_list) <= 1:
        if debug:
            print(
                f'\n    更新分型：\n'
                f'        当前仅有1根缠论K线，忽略。'
            )
        return result

    # 缠论K线 2 根。
    if len(candlestick_chan_list) == 2:
        candle_l = candlestick_chan_list[0]
        candle_r = candlestick_chan_list[1]

        trend = get_trend(candle_l=candle_l, candle_r=candle_r)
        fractal: FractalType = FractalType.Bottom if trend == TrendType.Bullish else FractalType.Top

        result.append(
            Fractal(
                type_=fractal,
                idx=0,
                left=None,
                middle=candle_l,
                right=candle_r
            )
        )

        if debug:
            print(
                f'\n    更新分型：\n'
                f'        当前仅有2根缠论K线，趋势为 {trend.value}，暂定 首根缠论K线为 {fractal.value}。'
            )

        return result

    # 其他情况
    candle_l = candlestick_chan_list[-3]
    candle_m = candlestick_chan_list[-2]
    candle_r = candlestick_chan_list[-1]

    new_fractal: Fractal
    is_new_fractal, new_fractal_type = is_fractal(candle_l, candle_m, candle_r)
    if is_new_fractal:
        # 新分型
        idx_new_fractal = len(candlestick_chan_list) - 2
        new_fractal = Fractal(
            type_=new_fractal_type,
            idx=idx_new_fractal,
            left=candle_l,
            middle=candle_m,
            right=candle_r
        )

        # 如果前分型的特征idx==0，前分型特征idx==1，覆盖。
        idx_previous_fractal = result[-1].idx
        if idx_previous_fractal == 0 and idx_new_fractal == 1:
            result[-1].idx = new_fractal

    if debug:
        print(
            f'\n    更新分型：\n'
            f'        尚未完成。'
        )


def print_debug_before(idx: int,
                       count: int,
                       candlestick_list: CandlestickOrdinary,
                       candle_ordinary: CandlestickOrdinary) -> None:
    """
    Print information before processing each turn.
    :return:
    """

    width: int = len(str(count - 1)) + 1

    print(
        f'\n第 {idx:>{width}} / {count - 1:>{width}} （普通K线）轮：\n'
        f'    前K线（缠论K线）：idx = {idx - 1}, '
        f'高点 = {candlestick_list.high}, '
        f'低点 = {candlestick_list.low}\n'
        f'    本K线（普通K线）：idx = {idx}, '
        f'高点 = {candle_ordinary.high}, '
        f'低点 = {candle_ordinary.low}'
    )


def print_debug_after(candlestick_list: CandlestickChanList,
                      base_time: dt.datetime) -> None:
    """
    Print information after processing each turn.

    :param candlestick_list:
    :param base_time:
    :return:
    """
    time_current: dt.datetime = dt.datetime.now()

    count: int = len(candlestick_list)

    print(
        f'\n    【处理完毕】，用时 {time_current - base_time}，结果如下：\n'
        f'        缠论K线数量： {count}。'
    )
    print(
        f'        前1缠论K线：自 {candlestick_list[-1].first} 至 {candlestick_list[-1].last}，'
        f'周期 = {candlestick_list[-1].period}；'
    )
    if count >= 2:
        print(
            f'        前2缠论K线：自 {candlestick_list[-2].first} 至 {candlestick_list[-2].last}，'
            f'周期 = {candlestick_list[-2].period}；'
        )
    else:
        print('        前2缠论K线：  不存在；')
    if count >= 3:
        print(
            f'        前3缠论K线：自 {candlestick_list[-3].first} 至 {candlestick_list[-3].last}，'
            f'周期 = {candlestick_list[-3].period}。'
        )
    else:
        print('        前3缠论K线：  不存在。')


def theory_of_chan_2(df_origin: pd.DataFrame,
                     count: int = None,
                     debug: bool = False) -> CandlestickChanList:
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
    candlestick_ordinary: CandlestickOrdinary
    candlestick_chan_list: CandlestickChanList = []
    fractal_list: FractalList = []
    chan_candle_count: int                  # 缠论K线数量
    chan_candle_last: CandlestickChan       # 最新缠论K线

    # 转化化 df_origin。
    df_data: pd.DataFrame = df_origin.reset_index()

    # 初始化 candlestick_chan。
    candlestick_chan_list.append(
        CandlestickChan(
            high=df_data.loc[0, 'high'].copy(),
            low=df_data.loc[0, 'low'].copy(),
            period=1,
            first=0,
            last=0
        )
    )

    # ----------------------------------------
    # 打印 debug 信息。
    # ----------------------------------------
    if debug:
        width: int = len(str(count - 1)) + 1
        print(
            f'\n第 {0:>{width}} / {count - 1:>{width}} （普通K线）轮：\n'
            f'    前K线（缠论K线）：idx = 0, '
            f'高点 = {candlestick_chan_list[0].high}, '
            f'低点 = {candlestick_chan_list[0].low}\n'
            f'    本K线（普通K线）：idx = 0, '
            f'高点 = {df_data.loc[0, "high"].copy()}, '
            f'低点 = {df_data.loc[0, "low"].copy()}\n'
            f'\n'
            f'    【初始化】完成。'
        )

    # 循环 df_data。
    for idx in range(1, count):

        # 当前普通K线。
        candlestick_ordinary = CandlestickOrdinary(
            high=df_data.loc[idx, 'high'].copy(),
            low=df_data.loc[idx, 'low'].copy()
        )

        # 当前缠论K线数量。
        chan_candle_count = len(candlestick_chan_list)

        chan_candle_last = candlestick_chan_list[-1]

        # ----------------------------------------
        # 打印 debug 信息。
        # ----------------------------------------
        if debug:
            print_debug_before(
                idx=idx,
                count=count,
                candlestick_list=chan_candle_last,
                candle_ordinary=candlestick_ordinary
            )

        # 合并K线。
        candlestick_chan_list = merge_candlestick(
            candlestick_chan_list=candlestick_chan_list,
            candlestick_ordinary=candlestick_ordinary,
            debug=debug
        )

        # 如果缠论K线有变化（新增或修正），更新分型。
        if len(candlestick_chan_list) != chan_candle_count or candlestick_chan_list[-1] != chan_candle_last:
            fractal_list = update_fractal(
                candlestick_chan_list=candlestick_chan_list,
                fractal_list=fractal_list,
                debug=debug
            )
        else:
            if debug:
                print(
                    f'\n    缠论K线无变化，无需更新分型。\n'
                )

        # ----------------------------------------
        # 打印 debug 信息。
        # ----------------------------------------
        if debug:
            print_debug_after(
                candlestick_list=candlestick_chan_list,
                base_time=time_start
            )

    time_end: dt.datetime = dt.datetime.now()

    if debug:
        print(f'\n计算完成！\n总计花费： {time_end - time_start}')

    return candlestick_chan_list


def plot_theory_of_chan_2(df_origin: pd.DataFrame,
                          candlestick_chan_list: CandlestickChanList,
                          count: int,
                          merged_line_width: int = 3,
                          debug: bool = False):
    """
    绘制合并后的K线。

    :param df_origin:
    :param candlestick_chan_list:
    :param count:
    :param merged_line_width:
    :param debug:

    ----
    :return:
    """
    mpf_color = mpf.make_marketcolors(
        up='red',       # 上涨K线的颜色
        down='green',   # 下跌K线的颜色
        inherit=True
    )

    mpf_style = mpf.make_mpf_style(
        marketcolors=mpf_color,
        rc={
            'font.family': 'SimHei',        # 指定默认字体：解决plot不能显示中文问题
            'axes.unicode_minus': False,    # 解决保存图像是负号'-'显示为方块的问题
        }
    )

    mpf_config = {}

    fig, ax_list = mpf.plot(
        df_origin.iloc[:count],
        title='AL2111',
        type='candle',
        volume=False,
        show_nontrading=False,
        figratio=(40, 20),
        figscale=2,
        style=mpf_style,
        tight_layout=True,
        returnfig=True,
        return_width_config=mpf_config,
        warn_too_much_data=1000
    )

    candle_width = mpf_config['candle_width']
    line_width = mpf_config['line_width']

    if debug:
        for k, v in mpf_config.items():
            print(k, v)

    # 生成缠论K线元素。
    candle_chan = []
    for idx in range(len(candlestick_chan_list)):
        candle = candlestick_chan_list[idx]

        if candle.first > count:
            break

        candle_chan.append(
            Rectangle(
                xy=(
                    candle.first - candle_width / 2,
                    candle.low
                ),
                width=candle.period - 1 + candle_width,
                height=candle.high - candle.low,
                angle=0,
                linewidth=line_width * merged_line_width
            )
        )

    # 生成矩形。
    patch_collection = PatchCollection(
        candle_chan,
        edgecolor='black',
        # facecolor='none',
        facecolor='gray',
        alpha=0.6
    )

    ax1 = ax_list[0]
    ax1.add_collection(patch_collection)
    ax1.autoscale_view()

    print('Plot done.')
