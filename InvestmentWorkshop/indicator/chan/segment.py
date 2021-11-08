# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Optional
from copy import deepcopy

from .definition import (
    TrendType,

    Fractal,
    FractalList,
    FractalType,

    LinearElement,
    SegmentList,
)


def generate_segment(segment_list: SegmentList,
                     fractal_list: FractalList,
                     debug: bool = False
                     ) -> Optional[SegmentList]:
    """
    Generate stroke list.

    :param segment_list:
    :param fractal_list:
    :param debug:
    :return:
    """
    result: SegmentList = deepcopy(segment_list)

    # 已存在的线段的数量。
    segment_count: int = 0 if result is None else len(result)

    # 声明变量类型
    last_segment: LinearElement
    last_fractal: Fractal

    # 如果这不是第1个线段：
    if segment_count > 0:

        last_segment = result[-1]
        last_fractal = fractal_list[-1]

        print(f'last_fractal idx: {last_fractal.idx}')
        print(f'last_segment idx: {last_segment.fractals[-1].idx}')
        print(f'last_segment right idx: {last_segment.fractals[-1].idx}')
        print(f'last_segment len: {len(last_segment.fractals)}')

        # 如果 倒数第一个分型的编号 > 线段含有的倒数第一个分型的编号：
        #     生成了新分型，判断是否线段延伸。
        if last_fractal.idx > last_segment.right_fractal.idx:
            # 线段修正。
            # 线段延伸。
            is_extended: bool = False

            # 如果是：
            #     1. 上升线段
            #     2. 顶分型
            #     3. 顶分型的极值 >= 线段右侧值
            if last_segment.trend == TrendType.Bullish and \
                    last_fractal.type_ == FractalType.Top and \
                    last_fractal.extreme_price >= last_segment.right_price:
                is_extended = True

            # 如果是：
            #     1. 下降线段
            #     2. 底分型
            #     3. 底分型的极值 <= 线段右侧值
            if last_segment.trend == TrendType.Bearish and \
                    last_fractal.type_ == FractalType.Bottom and \
                    last_fractal.extreme_price <= last_segment.right_price:
                is_extended = True

            if is_extended:
                last_segment.right_fractal = last_fractal
                last_segment.fractals.extend(
                    [fractal_list[-2], fractal_list[-1]]
                )
                if debug:
                    print(
                        f'\n'
                        f'  ○ 延伸线段：\n'
                        f'    第 {segment_count - 1} 个线段，type = {last_segment.trend.value}。\n'
                        f'    起点：分型 idx = {fractal_list.index(last_segment.left_fractal)}，'
                        f'普通K线 idx = {last_segment.left_fractal.middle_candle.last_ordinary_idx}。\n'
                        f'    终点：分型 idx = {fractal_list.index(last_segment.right_fractal)}，'
                        f'普通K线 idx = {last_segment.right_fractal.middle_candle.last_ordinary_idx}。\n'
                        f'    含有分型数量： {len(last_segment.fractals)}。\n'
                    )

        # # 如果 倒数第一个分型的编号 < 线段含有的倒数第一个分型的编号：
        # #     丢弃了分型，判断丢弃线段包含的分型或者丢弃线段。
        # if last_fractal.idx < last_segment.fractals[-1].idx or \
        #         last_fractal.idx < last_segment.right_fractal.idx:
        #     # fractal_list[-1].idx == result[-1].fractals[-2].idx:
        #
        #     # 如果线段包含的分型数量 <= 4 ，丢弃线段。
        #     if len(last_segment.fractals) <= 4:
        #         if debug:
        #             print(
        #                 f'\n'
        #                 f'  ○ 丢弃线段：\n'
        #                 f'    因分型被丢弃，第 {segment_count - 1} 个线段包含的分型不足4个，线段已不成立。'
        #             )
        #         result.pop()
        #         segment_count = 0 if result is None else len(result)
        #
        #     # 否则丢弃线段包含的分型。
        #     else:
        #         if debug:
        #             last_segment.fractals.pop()
        #             last_segment.fractals.pop()
        #             print(
        #                 f'\n'
        #                 f'  ○ 丢弃线段分型：\n'
        #                 f'    因分型被丢弃，第 {segment_count - 1} 个线段包含的分型仍有4个，清理被丢弃的分型。'
        #                 f'含有分型数量： {len(last_segment.fractals)}。\n'
        #             )

    # 如果分型的数量 >= 4：
    #     尝试生成线段：
    if len(fractal_list) >= 4:

        # 声明变量类型
        new_segment: Optional[LinearElement] = None  # 新的线段
        is_overlap: bool  # 是否有重叠区域
        overlap_high: float  # 重叠区间左值
        overlap_low: float  # 重叠区间右值

        # 分型
        fractal_p1: Fractal = fractal_list[-1]
        fractal_p2: Fractal = fractal_list[-2]
        fractal_p3: Fractal = fractal_list[-3]
        fractal_p4: Fractal = fractal_list[-4]

        # fractal_p4 是 底分型
        if fractal_p4.type_ == FractalType.Bottom:

            # 检测重叠区间
            overlap_high = min(fractal_p3.extreme_price, fractal_p1.extreme_price)
            overlap_low = max(fractal_p4.extreme_price, fractal_p2.extreme_price)

            if overlap_high > overlap_low:
                new_segment = LinearElement(
                    idx=segment_count,
                    type_='Segment',
                    trend=TrendType.Bullish,
                    left_fractal=fractal_p4,
                    right_fractal=fractal_p1,
                    fractals=[fractal_p4, fractal_p3, fractal_p2, fractal_p1]
                )

        # fractal_p4 是 顶分型
        elif fractal_p4.type_ == FractalType.Top:

            # 检测重叠区间
            overlap_high = min(fractal_p4.extreme_price, fractal_p2.extreme_price)
            overlap_low = max(fractal_p3.extreme_price, fractal_p1.extreme_price)

            if debug:
                print('*****')
                print('线段检测')
                print(f'    fractal_p1: idx = {fractal_p1.middle_candle.last_ordinary_idx}')
                print(f'    fractal_p2: idx = {fractal_p2.middle_candle.last_ordinary_idx}')
                print(f'    fractal_p3: idx = {fractal_p3.middle_candle.last_ordinary_idx}')
                print(f'    fractal_p4: idx = {fractal_p4.middle_candle.last_ordinary_idx}')
                print(f'    overlap_high: min( {fractal_p4.extreme_price}, {fractal_p2.extreme_price} ) = {overlap_high}')
                print(f'    overlap_low:  max( {fractal_p3.extreme_price}, {fractal_p1.extreme_price} ) = {overlap_low}')

            if overlap_high > overlap_low:
                new_segment = LinearElement(
                    idx=segment_count,
                    type_='Segment',
                    trend=TrendType.Bearish,
                    left_fractal=fractal_p4,
                    right_fractal=fractal_p1,
                    fractals=[fractal_p4, fractal_p3, fractal_p2, fractal_p1]
                )

        # 如果有重叠部分
        if new_segment is not None:
            is_added: bool = False

            # 如果这是第1个线段，加入列表。
            if segment_count == 0:
                result = [new_segment]
                is_added = True
            else:
                last_segment = result[-1]
                if debug:
                    print(f'new_segment.left_fractal {new_segment.left_fractal}')
                    print(f'last_segment.right_fractal {last_segment.right_fractal}')
                if new_segment.left_fractal == last_segment.right_fractal:
                    result.append(new_segment)
                    is_added = True
            if debug and is_added:
                print(
                    f'\n'
                    f'  ○ 生成线段：\n'
                    f'    第 {segment_count} 个线段，type = {new_segment.trend.value}。\n'
                    f'    起点：分型 idx = {fractal_list.index(new_segment.left_fractal)}，'
                    f'普通K线 idx = {new_segment.left_fractal.middle_candle.last_ordinary_idx}。\n'
                    f'    终点：分型 idx = {fractal_list.index(new_segment.right_fractal)}，'
                    f'普通K线 idx = {new_segment.right_fractal.middle_candle.last_ordinary_idx}。\n'
                )

    return result
