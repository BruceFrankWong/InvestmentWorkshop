# -*- coding: utf-8 -*-

__author__ = 'Bruce Frank Wong'

"""

    Chan Theory

        Record data with pandas DataFrame, and align with common candlestick DataFrame.

"""


from typing import Dict, List, Tuple, Any, Sequence, Optional
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

    def __str__(self) -> str:
        return self.value


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
class FractalStandard:
    type_: FractalType
    is_confirmed: bool
    left: CandlestickChan
    middle: CandlestickChan
    right: CandlestickChan

    def __str__(self) -> str:
        return f'FractalStandard (confirmed = {self.is_confirmed}, {self.type_.value}, idx = {self.middle.last}, ' \
               f'range = {self.middle.high} ~ {self.middle.low})'


@dataclass
class FractalFirst:
    type_: FractalType
    middle: CandlestickChan
    right: CandlestickChan


@dataclass
class FractalLast:
    type_: FractalType
    left: CandlestickChan
    middle: CandlestickChan


CandlestickChanList = List[CandlestickChan]
FractalList = List[FractalStandard]


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


def get_fractal_distance(left_fractal: FractalStandard,
                         right_fractal: FractalStandard,
                         candlestick_chan_list: List[CandlestickChan]) -> int:
    """
    两个分型之间的距离（取分型中间那根K线）。
    :param left_fractal:
    :param right_fractal:
    :param candlestick_chan_list:
    :return:
    """
    return candlestick_chan_list.index(right_fractal.middle) - candlestick_chan_list.index(left_fractal.middle)


def update_fractal(candlestick_chan_list: List[CandlestickChan],
                   fractal_list: FractalList,
                   debug: bool = False
                   ) -> Optional[FractalList]:

    # --------------------
    # 声明变量
    # --------------------

    # 结果
    result: FractalList = deepcopy(fractal_list)

    # 最新的缠论K线
    candle: CandlestickChan = candlestick_chan_list[-1]
    # 最新的缠论K线的 idx
    idx_candle: int = len(candlestick_chan_list) - 1

    # 已存在的分型的数量。
    fractal_count: int = 0 if result is None else len(result)

    # 前分型。
    fractal: FractalStandard = result[-1] if fractal_count >= 1 else None
    # 前分型的中间缠论K线 idx
    idx_fractal: int = candlestick_chan_list.index(fractal.middle) if fractal_count >= 1 else 0

    # ----------------------------------------
    # 如果分型数量 > 0，且 前分型未被确认：
    # ----------------------------------------
    if fractal_count > 0:  # and not fractal.is_confirmed:
        # --------------------
        # 确认 前分型。
        # --------------------

        # 如果当前缠论K线与前分型中间K线的距离 >= 4 （即中间有3根缠论K线）。
        distance: int = idx_candle - idx_fractal
        if distance >= 4:
            fractal.is_confirmed = True
            if debug:
                print(
                    f'\n'
                    f'    确认分型：\n'
                    f'        当前K线（缠论idx = {idx_candle}，普通idx = {candle.last}）与'
                    f'前分型（分型idx = {fractal_count - 1}，缠论idx = {idx_fractal}，普通idx = {fractal.middle.last}）'
                    f'之间有 {distance - 1} 根缠论K线，无论行情如何变化，该分型可以被确认。\n'
                )

        # --------------------
        # 丢弃 前分型。
        # --------------------

        # 如果当前缠论K线的极值顺着前分型的方向突破（即最高价大于顶分型中间K线的最高价，对底分型反之）。
        if fractal.type_ == FractalType.Top:
            extreme_type = '最高价'
            value_candle = candle.high
            value_fractal = fractal.middle.high
        else:
            extreme_type = '最低价'
            value_candle = candle.low
            value_fractal = fractal.middle.low
        if (
                (
                        fractal.type_ == FractalType.Top and value_candle > value_fractal
                ) or
                (
                        fractal.type_ == FractalType.Bottom and value_candle < value_fractal
                )
        ):
            if debug:
                print(
                    f'\n'
                    f'    丢弃分型：\n'
                    f'        当前缠论K线的{extreme_type}({value_candle})超越了与前分型的极值（{value_fractal}），丢弃前分型。\n'
                )

            # 丢弃前分型。
            result.remove(fractal)
            # 重新统计分型数量。
            fractal_count = 0 if result is None else len(result)
            # 重新索引前分型。
            fractal: FractalStandard = result[-1] if fractal_count >= 1 else None
            # 重新索引前分型的中间缠论K线 idx
            idx_fractal = candlestick_chan_list.index(fractal.middle) if fractal_count >= 1 else 0

    # --------------------
    # 生成 分型。
    # --------------------
    candle_l = candlestick_chan_list[-3]
    candle_m = candlestick_chan_list[-2]
    candle_r = candlestick_chan_list[-1]

    is_new_fractal, new_fractal_type = is_fractal(candle_l, candle_m, candle_r)
    if is_new_fractal:

        # 生成新分型。
        new_fractal: FractalStandard = FractalStandard(
            type_=new_fractal_type,
            is_confirmed=False,
            left=candle_l,
            middle=candle_m,
            right=candle_r
        )

        # 如果这是第1个分型，加入列表。
        if fractal_count == 0:
            result = [new_fractal]
            if debug:
                print(
                    f'\n'
                    f'    生成分型：\n'
                    f'        第 {fractal_count + 1} 个分型，类型为 {new_fractal_type}。\n'
                    f'        缠论K线 idx = {candlestick_chan_list.index(candle_m)}， 普通K线 idx = {candle_m.last}。'
                )

        # 这不是第1个分型：
        else:
            # 新生成的分型：
            #     1. 不能和前分型重复（中间K线一样） -> 和前分型有足够距离
            #     2. 不接受同向分型（除非极值跟大，但这样在前面就被丢弃了）
            #     3. 前分型未被确认的时候不接受反向分型 -> 取消确认一说。
            # if candle_m != fractal.middle and new_fractal_type != fractal.type_ and fractal.is_confirmed:
            if candlestick_chan_list.index(candle_m) - candlestick_chan_list.index(fractal.middle) >= 4 and \
                    new_fractal_type != fractal.type_:
                result.append(new_fractal)

                if debug:
                    print(
                        f'\n'
                        f'    生成分型：\n'
                        f'        第 {fractal_count + 1} 个分型，类型为 {new_fractal_type}。\n'
                        f'        缠论K线 idx = {candlestick_chan_list.index(candle_m)}， 普通K线 idx = {candle_m.last}。'
                    )

    return result


# def update_fractal(candlestick_chan_list: List[CandlestickChan],
#                    fractal_list: FractalList,
#                    debug: bool = False
#                    ) -> Optional[FractalList]:
#
#     result: FractalList = deepcopy(fractal_list)
#
#     # 缠论K线不足 3 根。
#     if len(candlestick_chan_list) < 3:
#         if debug:
#             print(
#                 f'\n    更新分型：\n'
#                 f'        当前不足3根缠论K线，忽略。'
#             )
#         return None
#
#     # 其他情况
#     candle_l = candlestick_chan_list[-3]
#     candle_m = candlestick_chan_list[-2]
#     candle_r = candlestick_chan_list[-1]
#
#     is_new_fractal, new_fractal_type = is_fractal(candle_l, candle_m, candle_r)
#     if is_new_fractal:
#
#         # 新分型
#         new_fractal: FractalStandard = FractalStandard(
#             type_=new_fractal_type,
#             is_confirmed=False,
#             left=candle_l,
#             middle=candle_m,
#             right=candle_r
#         )
#
#         # 已存在的分型的数量。
#         count: int = 0 if result is None else len(result)
#
#         if debug:
#             print(
#                 f'\n    更新分型：\n'
#                 f'        生成第 {count + 1} 个分型：{new_fractal_type}。\n'
#                 f'        缠论K线 idx = {candlestick_chan_list.index(candle_m)}， 普通K线 idx = {candle_m.last}。'
#             )
#
#         # 第1个分型：
#         if count == 0:
#             result = [new_fractal]
#             if debug:
#                 print(f'        缓存新分型。')
#
#         # 是第2个分型：
#         elif count == 1:
#             # 前分型。
#             old_fractal: FractalStandard = result[-1]
#
#             # 分型间距离。
#             distance: int = get_fractal_distance(old_fractal, new_fractal, candlestick_chan_list)
#
#             # 共用K线:
#             if distance <= 2:
#                 # 类型不同
#                 if new_fractal.type_ != old_fractal.type_:
#                     if debug:
#                         print(
#                             f'        新分型与前分型共用K线（距离 = {distance}），与前分型类型不同，放弃新分型。'
#                         )
#                 else:
#                     if (
#                             (
#                                     new_fractal.type_ == FractalType.Top and
#                                     new_fractal.middle.low < old_fractal.middle.low
#                             ) or
#                             (
#                                     new_fractal.type_ == FractalType.Bottom and
#                                     new_fractal.middle.high > old_fractal.middle.high
#                             )
#                     ):
#                         result[-1] = new_fractal
#                         if debug:
#                             print(
#                                 f'        新分型与前分型共用K线（距离 = {distance}），与前分型类型相同，极值更大，替换前分型。'
#                             )
#                     else:
#                         if debug:
#                             print(
#                                 f'        新分型与前分型共用K线（距离 = {distance}），与前分型类型相同，极值不如，放弃新分型。'
#                             )
#
#             # 不共用K线：
#             else:
#                 # 类型不同
#                 if new_fractal.type_ != old_fractal.type_:
#                     if (
#                             (
#                                     old_fractal.type_ == FractalType.Top and
#                                     new_fractal.middle.low > old_fractal.middle.low
#                             ) or
#                             (
#                                     new_fractal.type_ == FractalType.Bottom and
#                                     new_fractal.middle.high < old_fractal.middle.high
#                             )
#                     ):
#                         if debug:
#                             print(
#                                 f'        新分型与前分型不共用K线（距离 = {distance}），与前分型类型不同，未突破，放弃新分型。'
#                             )
#                     else:
#                         result.append(new_fractal)
#                         if debug:
#                             print(
#                                 f'        新分型与前分型不共用K线（距离 = {distance}），与前分型类型不同，突破前分型极值，确认新分型。'
#                             )
#                 else:
#                     result.append(new_fractal)
#                     if debug:
#                         print(
#                             f'        新分型与前分型不共用K线（距离 = {distance}），与前分型类型相同，确认新分型。'
#                         )
#
#         # 是更后面的分型：
#         else:
#
#             if debug:
#                 print(
#                     f'\n    更新分型：\n'
#                     f'        尚未完成。'
#                 )
#
#     return result


# def update_fractal(candlestick_chan_list: List[CandlestickChan],
#                    fractal_list: FractalList,
#                    debug: bool = False
#                    ) -> Tuple[Optional[FractalFirst], Optional[FractalLast], Optional[FractalList]]:
#
#     result: FractalList = deepcopy(fractal_list)
#
#     # 缠论K线 1 根或更少。
#     if len(candlestick_chan_list) <= 1:
#         if debug:
#             print(
#                 f'\n    更新分型：\n'
#                 f'        当前仅有1根缠论K线，忽略。'
#             )
#         return None, None, None
#
#     # 缠论K线 2 根。
#     if len(candlestick_chan_list) == 2:
#         candle_l = candlestick_chan_list[0]
#         candle_r = candlestick_chan_list[1]
#
#         trend = get_trend(candle_l=candle_l, candle_r=candle_r)
#         fractal: FractalType = FractalType.Bottom if trend == TrendType.Bullish else FractalType.Top
#
#         fractal_first: FractalFirst = FractalFirst(
#             type_=FractalType.Bottom if trend == TrendType.Bullish else FractalType.Top,
#             middle=candle_l,
#             right=candle_r
#         )
#         fractal_last: FractalLast = FractalLast(
#             type_=FractalType.Bottom if trend == TrendType.Bearish else FractalType.Top,
#             left=candle_l,
#             middle=candle_r
#         )
#
#         if debug:
#             print(
#                 f'\n    更新分型：\n'
#                 f'        当前仅有2根缠论K线，趋势为 {trend.value}，暂定 首根缠论K线为 {fractal.value}。'
#             )
#
#         return fractal_first, fractal_last, None
#
#     # 其他情况
#     candle_l = candlestick_chan_list[-3]
#     candle_m = candlestick_chan_list[-2]
#     candle_r = candlestick_chan_list[-1]
#
#     is_new_fractal, new_fractal_type = is_fractal(candle_l, candle_m, candle_r)
#     if is_new_fractal:
#         # 新分型
#         idx_new_fractal: int = len(candlestick_chan_list) - 2
#         new_fractal: FractalStandard = FractalStandard(
#             type_=new_fractal_type,
#             left=candle_l,
#             middle=candle_m,
#             right=candle_r
#         )
#         # 前分型
#         old_fractal: Fractal = result[-1]
#         idx_old_fractal: int = result[-1].middle.last
#
#         # 前后两个分型的特征距离。
#         try:
#             idx_distance: int = idx_new_fractal - idx_old_fractal
#         except TypeError as e:
#             print(f'idx_new_fractal: {idx_new_fractal}, {type(idx_new_fractal)}')
#             print(f'idx_old_fractal: {idx_old_fractal}, {type(idx_old_fractal)}')
#             raise TypeError(e)
#
#         # 如果前分型是不完整分型:
#         if old_fractal.left is None:
#
#             # 如果前后分型的特征距离==1，替换
#             if idx_distance == 1:
#                 result[-1].idx = new_fractal
#
#         # 如果前分型是完整分型：
#         else:
#             pass
#
#     if debug:
#         print(
#             f'\n    更新分型：\n'
#             f'        尚未完成。'
#         )
#
#     return result


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
                      fractal_list: FractalList,
                      base_time: dt.datetime) -> None:
    """
    Print information after processing each turn.

    :param candlestick_list:
    :param fractal_list:
    :param base_time:
    :return:
    """
    time_current: dt.datetime = dt.datetime.now()

    count_candle: int = len(candlestick_list)

    print(
        f'\n    【处理完毕】，用时 {time_current - base_time}。\n'
        f'\n        缠论K线数量： {count_candle}。'
    )
    print(
        f'        前1缠论K线：自 {candlestick_list[-1].first} 至 {candlestick_list[-1].last}，'
        f'周期 = {candlestick_list[-1].period}；'
    )
    if count_candle >= 2:
        print(
            f'        前2缠论K线：自 {candlestick_list[-2].first} 至 {candlestick_list[-2].last}，'
            f'周期 = {candlestick_list[-2].period}；'
        )
    else:
        print('        前2缠论K线：  不存在；')
    if count_candle >= 3:
        print(
            f'        前3缠论K线：自 {candlestick_list[-3].first} 至 {candlestick_list[-3].last}，'
            f'周期 = {candlestick_list[-3].period}。'
        )
    else:
        print('        前3缠论K线：  不存在。')

    count_fractal: int = 0 if fractal_list is None else len(fractal_list)
    print(
        f'\n        分型数量： {count_fractal}。'
    )
    if count_fractal >= 1:
        fractal = fractal_list[-1]
        confirmed = '已确认' if fractal.is_confirmed else '未确认'
        print(
            f'        分型(f-1)： {confirmed}，type = {fractal.type_.value}，idx = {fractal.middle.last}。'
        )
    else:
        print('        分型(f-1)：   不存在。')
    if count_fractal >= 2:
        fractal = fractal_list[-2]
        confirmed = '已确认' if fractal.is_confirmed else '未确认'
        print(
            f'        分型(f-2)： {confirmed}，type = {fractal.type_.value}，idx = {fractal.middle.last}。'
        )
    else:
        print('        分型(f-2)：   不存在。')


def theory_of_chan_2(df_origin: pd.DataFrame,
                     count: int = None,
                     debug: bool = False) -> Tuple[CandlestickChanList, FractalList]:
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

        # 如果缠论K线数量 >= 3，且有变化（新增或修正），更新分型。
        if len(candlestick_chan_list) >= 3:
            if len(candlestick_chan_list) > chan_candle_count or candlestick_chan_list[-1] != chan_candle_last:
                fractal_list = update_fractal(
                    candlestick_chan_list=candlestick_chan_list,
                    fractal_list=fractal_list,
                    debug=debug
                )
            else:
                if debug:
                    print(
                        f'\n    更新分型：\n'
                        f'        缠论K线无更新，略过。'
                    )
        else:
            if debug:
                print(
                    f'\n    更新分型：\n'
                    f'        缠论K线少于3根，略过。'
                )

        # ----------------------------------------
        # 打印 debug 信息。
        # ----------------------------------------
        if debug:
            print_debug_after(
                candlestick_list=candlestick_chan_list,
                fractal_list=fractal_list,
                base_time=time_start
            )

    time_end: dt.datetime = dt.datetime.now()

    if debug:
        print(f'\n计算完成！\n总计花费： {time_end - time_start}')

    return candlestick_chan_list, fractal_list


def plot_theory_of_chan_2(df_origin: pd.DataFrame,
                          candlestick_chan_list: CandlestickChanList,
                          fractal_list: FractalList,
                          count: int,
                          title: str = '',
                          tight_layout: bool = True,
                          show_ordinary_idx: bool = False,
                          show_chan_idx: bool = False,
                          merged_line_width: int = 3,
                          show_all_merged: bool = False,
                          hatch_merged: bool = False,
                          fractal_marker_size: int = 100,
                          fractal_marker_offset: int = 50,
                          debug: bool = False):
    """
    绘制合并后的K线。

    :param df_origin:
    :param candlestick_chan_list:
    :param fractal_list:
    :param count:
    :param title:
    :param tight_layout:
    :param show_ordinary_idx:
    :param show_chan_idx:
    :param merged_line_width:
    :param show_all_merged:
    :param hatch_merged:
    :param fractal_marker_size:
    :param fractal_marker_offset:
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

    # 附加元素
    additional_plot: list = []

    # 分型
    fractal_t: list = []
    fractal_b: list = []
    idx_fractal_to_ordinary: int
    idx_ordinary_candle: int = 0
    for fractal in fractal_list:
        idx_fractal_to_ordinary = fractal.middle.last
        for idx in range(idx_ordinary_candle, idx_fractal_to_ordinary):
            fractal_t.append(np.nan)
            fractal_b.append(np.nan)
        if fractal.type_ == FractalType.Top:
            fractal_t.append(fractal.middle.high + fractal_marker_offset)
            fractal_b.append(np.nan)
        if fractal.type_ == FractalType.Bottom:
            fractal_t.append(np.nan)
            fractal_b.append(fractal.middle.low - fractal_marker_offset)
        idx_ordinary_candle = idx_fractal_to_ordinary + 1
    for idx in range(idx_ordinary_candle, count):
        fractal_t.append(np.nan)
        fractal_b.append(np.nan)

    additional_plot.append(
        mpf.make_addplot(fractal_t, type='scatter', markersize=fractal_marker_size, marker='v')
    )
    additional_plot.append(
        mpf.make_addplot(fractal_b, type='scatter', markersize=fractal_marker_size, marker='^')
    )

    # mplfinance 的配置
    mpf_config = {}

    fig, ax_list = mpf.plot(
        df_origin.iloc[:count],
        title=title,
        type='candle',
        volume=False,
        addplot=additional_plot,
        show_nontrading=False,
        figratio=(40, 20),
        figscale=2,
        style=mpf_style,
        tight_layout=tight_layout,
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

        if not show_all_merged and candle.period == 1:
            continue
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
    patch_collection: PatchCollection
    if hatch_merged:
        patch_collection = PatchCollection(
            candle_chan,
            edgecolor='black',
            facecolor='gray',
            alpha=0.35
        )
    else:
        patch_collection = PatchCollection(
            candle_chan,
            edgecolor='black',
            facecolor='none'
        )

    ax1 = ax_list[0]
    ax1.add_collection(patch_collection)

    # 普通K线 idx
    if show_ordinary_idx:
        idx_ordinary_x: List[int] = []
        idx_ordinary_y: List[float] = []
        idx_ordinary_value: List[str] = []
        
        for idx in range(0, count, 5):
            idx_ordinary_x.append(idx - candle_width / 2)
            idx_ordinary_y.append(df_origin.iloc[idx].at['low'] - 14)
            idx_ordinary_value.append(str(idx))

        for idx in range(len(idx_ordinary_x)):
            ax1.text(
                x=idx_ordinary_x[idx],
                y=idx_ordinary_y[idx],
                s=idx_ordinary_value[idx],
                color='red',
                fontsize=7,
                horizontalalignment='left',
                verticalalignment='top'
            )

    # 缠论K线 idx
    if show_chan_idx:
        idx_chan_x: List[int] = []
        idx_chan_y: List[float] = []
        idx_chan_value: List[str] = []

        for idx in range(len(candlestick_chan_list)):
            candle = candlestick_chan_list[idx]
            idx_chan_x.append(candle.last - candle_width / 2)
            idx_chan_y.append(candle.high + 14)
            idx_chan_value.append(str(candlestick_chan_list.index(candle)))

        for idx in range(len(idx_chan_x)):
            ax1.text(
                x=idx_chan_x[idx],
                y=idx_chan_y[idx],
                s=idx_chan_value[idx],
                color='blue',
                fontsize=7,
                horizontalalignment='left',
                verticalalignment='bottom'
            )

    ax1.autoscale_view()

    print('Plot done.')
