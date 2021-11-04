# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List
from copy import deepcopy

from .definition import (
    OrdinaryCandle,
    MergedCandle,
    MergedCandleList,
)
from .utility import (
    is_inclusive_candle,
)


def merge_candle(chan_candle_list: MergedCandleList,
                 ordinary_candle: OrdinaryCandle,
                 debug: bool = False
                 ) -> List[MergedCandle]:
    """
    合并K线。

    :param chan_candle_list:
    :param ordinary_candle:
    :param debug:

    :return:
    """

    result: List[MergedCandle] = deepcopy(chan_candle_list)

    is_inclusive: bool = is_inclusive_candle(
        chan_candle_list[-1],
        ordinary_candle
    )

    # 本普通K线与前缠论K线之间，不存在包含关系：
    if not is_inclusive:

        # 新的缠论K线，高点 = 普通K线高点，低点 = 普通K线低点，周期 = 1，。
        result.append(
            MergedCandle(
                high=ordinary_candle.high,
                low=ordinary_candle.low,
                period=1,
                idx_first_ordinary_candle=chan_candle_list[-1].idx_last_ordinary_candle + 1,
            )
        )

    # 如果存在包含：
    else:
        # 前1缠论K线的周期 + 1。
        result[-1].period += 1

        # 前1缠论K线所合并的普通K线，其第一根的序号为0（从序号 0 开始的普通K线都被合并了），取前1缠论K线和本普通K线的最大范围。
        if result[-1].idx_first_ordinary_candle == 0:
            result[-1].high = max(
                result[-1].high,
                ordinary_candle.high
            )
            result[-1].low = min(
                result[-1].low,
                ordinary_candle.low
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
                    ordinary_candle.high
                )
                result[-1].low = max(
                    result[-1].low,
                    ordinary_candle.low
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
                    ordinary_candle.high
                )
                result[-1].low = min(
                    result[-1].low,
                    ordinary_candle.low
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
            f'\n'
            f'  ○ 合并K线：\n'
            f'    K线关系：{"包含" if is_inclusive else "非包含"}\n'
            f'    当前缠论K线：高点 = {result[-1].high}，低点 = {result[-1].low}。'
        )

    # 返回新的缠论K线。
    return result
