# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Optional
from copy import deepcopy

from .definition import (
    MergedCandle,
    MergedCandleList,

    Fractal,
    FractalList,
    FractalType,
)
from .utility import (
    get_fractal_distance,
)


def generate_fractal(merged_candle_list: MergedCandleList,
                     fractal_list: FractalList,
                     debug: bool = False
                     ) -> Optional[FractalList]:
    # --------------------
    # 声明变量
    # --------------------

    # 结果
    result: FractalList = deepcopy(fractal_list)

    if len(merged_candle_list) < 3:
        return result

    # 最新的缠论K线
    last_merged_candle: MergedCandle = merged_candle_list[-1]

    # 已存在的分型的数量。
    fractal_count: int = 0 if result is None else len(result)

    # 前分型。
    last_fractal: Fractal = result[-1] if fractal_count >= 1 else None

    # ----------------------------------------
    # 丢弃 前分型。
    # ----------------------------------------

    # 如果分型数量 > 0：
    if fractal_count > 0 and last_fractal.is_confirmed is False:

        is_to_be_dropped: bool
        extreme_type: str
        candle_price: float
        fractal_price: float

        # 如果当前缠论K线的极值顺着前分型的方向突破（即最高价大于顶分型中间K线的最高价，对底分型反之）。
        if last_fractal.type_ == FractalType.Top and \
                last_merged_candle.high >= last_fractal.middle_candle.high:
            is_to_be_dropped = True
            extreme_type = '最高价'
            candle_price = last_merged_candle.high
            fractal_price = last_fractal.middle_candle.high
        elif last_fractal.type_ == FractalType.Bottom and \
                last_merged_candle.low <= last_fractal.middle_candle.low:
            is_to_be_dropped = True
            extreme_type = '最低价'
            candle_price = last_merged_candle.low
            fractal_price = last_fractal.middle_candle.low
        else:
            is_to_be_dropped = False
            extreme_type = ''
            candle_price = 0.0
            fractal_price = 0.0

        if is_to_be_dropped:
            if debug:
                print(
                    f'\n'
                    f'  丢弃分型：\n'
                    f'    当前缠论K线的{extreme_type}({candle_price})达到或超越了与前分型'
                    f'（idx = {fractal_list.index(last_fractal)}，'
                    f'type = {last_fractal.type_}）的极值（{fractal_price}），'
                    f'丢弃前分型。\n'
                )

            # 丢弃前分型。
            result.remove(last_fractal)
            # 重新统计分型数量。
            fractal_count = 0 if result is None else len(result)
            # 重新索引前分型。
            last_fractal = result[-1] if fractal_count >= 1 else None

    # --------------------
    # 生成 分型。
    # --------------------
    new_fractal: Optional[Fractal]

    left_candle = merged_candle_list[-3]
    middle_candle = merged_candle_list[-2]
    right_candle = merged_candle_list[-1]

    if middle_candle.high > left_candle.high and middle_candle.high > right_candle.high:
        new_fractal = Fractal(
            type_=FractalType.Top,
            is_confirmed=False,
            left_candle=left_candle,
            middle_candle=middle_candle,
            right_candle=right_candle
        )
    elif middle_candle.low < left_candle.low and middle_candle.low < right_candle.low:
        new_fractal = Fractal(
            type_=FractalType.Bottom,
            is_confirmed=False,
            left_candle=left_candle,
            middle_candle=middle_candle,
            right_candle=right_candle
        )
    else:
        new_fractal = None

    if new_fractal is not None:

        # 如果这是第1个分型，加入列表。
        if fractal_count == 0:
            result = [new_fractal]
            if debug:
                print(
                    f'\n'
                    f'  生成分型：\n'
                    f'    第 {fractal_count + 1} 个分型，type = {new_fractal.type_.value}。\n'
                    f'    缠论K线 idx = {merged_candle_list.index(middle_candle)}，'
                    f'普通K线 idx = {middle_candle.idx_last_ordinary_candle}。'
                )

        # 这不是第1个分型：
        else:
            # 新生成的分型：
            #     1. 不能和前分型重复（中间K线一样） -> 和前分型有足够距离
            #     2. 不接受同向分型（除非极值跟大，但这样在前面就被丢弃了）
            #     3. 前分型未被确认的时候不接受反向分型 -> 取消确认一说。
            distance = get_fractal_distance(
                left_fractal=last_fractal,
                right_fractal=new_fractal,
                merged_candle_list=merged_candle_list
            )
            if distance >= 4 and new_fractal.type_ != last_fractal.type_:
                last_fractal.is_confirmed = True
                result.append(new_fractal)

                if debug:
                    print(
                        f'\n'
                        f'  生成分型：\n'
                        f'    第 {fractal_count + 1} 个分型，type = {new_fractal.type_.value}。\n'
                        f'    缠论K线 idx = {merged_candle_list.index(middle_candle)}，'
                        f'普通K线 idx = {middle_candle.idx_last_ordinary_candle}。'
                    )

    return result
