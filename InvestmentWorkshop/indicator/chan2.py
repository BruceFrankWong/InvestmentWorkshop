# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
from copy import deepcopy

import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import mplfinance as mpf


class FractalPattern(Enum):
    Top = '顶分型'
    Bottom = '底分型'

    def __str__(self) -> str:
        return self.value


class FractalFunction(Enum):
    Reversal = '转折'
    Continuation = '中继'

    def __str__(self) -> str:
        return self.value


class Trend(Enum):
    U = '上升'
    D = '下降'
    Up = '上升'
    Down = '下降'
    Bullish = '上升'
    Bearish = '下降'

    def __str__(self) -> str:
        return self.value


@dataclass
class PlotConfig:
    merged_candles: bool
    fractals: bool
    strokes: bool
    segments: bool
    pivots: bool


@dataclass
class OrdinaryCandle:
    high: float
    low: float


@dataclass
class MergedCandle(OrdinaryCandle):
    idx: int
    period: int
    first_ordinary_idx: int

    @property
    def last_ordinary_idx(self) -> int:
        return self.first_ordinary_idx + self.period - 1

    def __str__(self) -> str:
        return f'MergedCandle (idx={self.idx}, period={self.period}, ' \
               f'first_ordinary_idx={self.first_ordinary_idx}, ' \
               f'last_ordinary_idx={self.last_ordinary_idx}, ' \
               f'price_high={self.high}, price_low={self.low})'


@dataclass
class Fractal:
    idx: int
    pattern: FractalPattern
    function: FractalFunction
    left_candle: MergedCandle
    middle_candle: MergedCandle
    right_candle: MergedCandle

    @property
    def extreme_price(self) -> float:
        if self.pattern == FractalPattern.Top:
            return self.middle_candle.high
        else:
            return self.middle_candle.low

    @property
    def ordinary_idx(self) -> int:
        return self.middle_candle.last_ordinary_idx

    def __str__(self) -> str:
        return f'Fractal (idx={self.idx}, ' \
               f'pattern={self.pattern.value}, function={self.function.value}, ' \
               f'ordinary_idx={self.ordinary_idx}, ' \
               f'extreme_price={self.extreme_price})'


@dataclass
class Stroke:
    idx: int
    trend: Trend
    left_fractal: Fractal
    right_fractal: Fractal

    @property
    def left_price(self) -> float:
        return self.left_fractal.extreme_price

    @property
    def right_price(self) -> float:
        return self.right_fractal.extreme_price

    @property
    def left_ordinary_idx(self) -> int:
        return self.left_fractal.ordinary_idx

    @property
    def right_ordinary_idx(self) -> int:
        return self.right_fractal.ordinary_idx

    @property
    def period(self) -> int:
        return self.right_ordinary_idx - self.left_ordinary_idx

    @property
    def price_range(self) -> float:
        return self.right_price - self.left_price

    @property
    def slope(self) -> float:
        return self.price_range / self.period

    def __str__(self) -> str:
        return f'Stroke (idx={self.idx}, trend={self.trend.value}, ' \
               f'left_ordinary_idx={self.left_ordinary_idx}, ' \
               f'right_ordinary_idx={self.right_ordinary_idx})'


@dataclass
class Segment:
    idx: int
    trend: Trend
    left_stroke: Stroke
    right_stroke: Stroke

    @property
    def left_price(self) -> float:
        return self.left_stroke.left_price

    @property
    def right_price(self) -> float:
        return self.right_stroke.right_price

    @property
    def left_ordinary_idx(self) -> int:
        return self.left_stroke.left_ordinary_idx

    @property
    def right_ordinary_idx(self) -> int:
        return self.right_stroke.right_ordinary_idx

    @property
    def period(self) -> int:
        return self.right_ordinary_idx - self.left_ordinary_idx

    @property
    def price_range(self) -> float:
        return self.right_price - self.left_price

    @property
    def slope(self) -> float:
        return self.price_range / self.period


@dataclass
class Pivot:
    idx: int


class ChanTheory:
    """
    缠论。
    """

    _debug: bool
    _strict: bool
    _minimum_distance: int
    _merged_candles: List[MergedCandle]
    _fractals: List[Fractal]
    _strokes: List[Stroke]
    _segments: List[Segment]
    _pivots: List[Pivot]

    def __init__(self, strict: bool = True, debug: bool = False):
        """
        Initialize the object.
        :param strict:
        :param debug:
        """
        self._strict = strict
        self._minimum_distance = 4 if strict else 3
        self._debug = debug

        self._merged_candles = []
        self._fractals = []
        self._strokes = []
        self._segments = []
        self._pivots = []

    @property
    def count_merged_candles(self) -> int:
        """
        Count of the merged candles list.

        :return: int.
        """
        return len(self._merged_candles)

    @property
    def merged_candles(self) -> List[MergedCandle]:
        return deepcopy(self._merged_candles)

    @property
    def count_fractals(self) -> int:
        """
        Count of the fractals list.

        :return:
        """
        return len(self._fractals)

    @property
    def fractals(self) -> List[Fractal]:
        return deepcopy(self._fractals)

    @property
    def count_strokes(self) -> int:
        """
        Count of the strokes list.

        :return:
        """
        return len(self._strokes)

    @property
    def strokes(self) -> List[Stroke]:
        return deepcopy(self._strokes)

    @property
    def count_segments(self) -> int:
        """
        Count of the segments list.

        :return:
        """
        return len(self._segments)

    @property
    def segments(self) -> List[Segment]:
        return deepcopy(self._segments)

    @property
    def count_pivots(self) -> int:
        """
        Count of the pivots list.

        :return:
        """
        return len(self._pivots)

    @staticmethod
    def is_inclusive(left_candle: OrdinaryCandle,
                     right_candle: OrdinaryCandle
                     ) -> bool:
        """
        判断两根K线是否存在包含关系。两根K线的关系有以下九种：

        :param left_candle: OrdinaryCandle, candlestick 1.
        :param right_candle: OrdinaryCandle, candlestick 2.

        ----
        :return: bool. Return True if a candle include another, otherwise False.
        """

        if (left_candle.high > right_candle.high and left_candle.low > right_candle.low) or \
                (left_candle.high < right_candle.high and left_candle.low < right_candle.low):
            return False
        else:
            return True

    def generate_merged_candle(self, ordinary_candle: OrdinaryCandle) -> bool:
        """
        Generate the merged candles。

        :param ordinary_candle:
        :return: bool, if new merged candle was generated or last merged candle was changed,
                 return True. Otherwise False.
        """

        # debug message.
        msg_generated: str = '\n  ○ 生成K线：\n    第 {idx} 根合并K线 起始普通K线idx={ordinary_idx}，周期={period}，' \
                             '高点={high}，低点={low}。\n'
        msg_merged: str = '\n  ○ 合并K线：\n    第 {idx} 根合并K线 起始普通K线idx={ordinary_idx}，周期={period}，' \
                          '高点={high}，低点={low}。\n'

        # 申明变量类型并赋值。
        is_changed: bool = False
        is_generated: bool = False
        is_merged: bool = False

        new_merged_candle: Optional[MergedCandle] = None

        # 前合并K线不存在：
        #     直接加入。
        if self.count_merged_candles == 0:
            new_merged_candle = MergedCandle(
                    idx=self.count_merged_candles,
                    high=ordinary_candle.high,
                    low=ordinary_candle.low,
                    period=1,
                    first_ordinary_idx=0
                )
            is_generated = True

        # 前合并K线存在：
        else:
            merged_candle_p1: MergedCandle = self._merged_candles[-1]  # 前1合并K线。

            # 如果没有包含关系：
            #     加入。
            if not self.is_inclusive(merged_candle_p1, ordinary_candle):
                new_merged_candle = MergedCandle(
                    idx=self.count_merged_candles,
                    high=ordinary_candle.high,
                    low=ordinary_candle.low,
                    period=1,
                    first_ordinary_idx=merged_candle_p1.last_ordinary_idx + 1
                )
                is_generated = True

            # 如果有包含关系：
            else:
                # 前1合并K线的周期 + 1。
                # merged_candle_p1.period += 1

                # 如果前合并K线是第一根合并K线：
                #     取前合并K线和新普通K线的最大范围。
                if self.count_merged_candles == 1:
                    new_merged_candle = MergedCandle(
                        idx=merged_candle_p1.idx,
                        high=max(
                            merged_candle_p1.high,
                            ordinary_candle.high
                        ),
                        low=min(
                            merged_candle_p1.low,
                            ordinary_candle.low
                        ),
                        period=merged_candle_p1.period + 1,
                        first_ordinary_idx=merged_candle_p1.first_ordinary_idx
                    )
                    is_merged = True

                # 前合并K线不是第一根合并K线：
                #     判断前1缠论K线和前2缠论K线的方向。
                else:
                    merged_candle_p2: MergedCandle = self._merged_candles[-2]   # 前2合并K线。

                    # 如果 前1缠论K线 与 前2缠论K线： 高点 > 高点 且 低点 > 低点：
                    #     合并取 高-高。
                    if (
                            merged_candle_p1.high > merged_candle_p2.high and
                            merged_candle_p1.low > merged_candle_p2.low
                    ):
                        new_merged_candle = MergedCandle(
                            idx=merged_candle_p1.idx,
                            high=max(
                                merged_candle_p1.high,
                                ordinary_candle.high
                            ),
                            low=min(
                                merged_candle_p1.low,
                                ordinary_candle.low
                            ),
                            period=merged_candle_p1.period + 1,
                            first_ordinary_idx=merged_candle_p1.first_ordinary_idx
                        )
                        is_merged = True

                    # 如果 前1缠论K线 与 前2缠论K线： 高点 > 高点 且 低点 > 低点：
                    #     合并取 低-低。
                    elif (
                            merged_candle_p1.high < merged_candle_p2.high and
                            merged_candle_p1.low < merged_candle_p2.low
                    ):
                        new_merged_candle = MergedCandle(
                            idx=merged_candle_p1.idx,
                            high=min(
                                merged_candle_p1.high,
                                ordinary_candle.high
                            ),
                            low=max(
                                merged_candle_p1.low,
                                ordinary_candle.low
                            ),
                            period=merged_candle_p1.period + 1,
                            first_ordinary_idx=merged_candle_p1.first_ordinary_idx
                        )
                        is_merged = True

                    # 其它情况：
                    #     判定为出错。
                    else:
                        print(
                            f'【ERROR】在合并K线时发生错误——未知的前K与前前K高低关系。\n'
                            f'前1高：{merged_candle_p1.high}，前2高：{merged_candle_p1.high}；\n'
                            f'前1低：{merged_candle_p1.low}，前2低：{merged_candle_p1.low}。'
                        )
        if is_generated:
            is_changed = True
            self._merged_candles.append(new_merged_candle)

            if self._debug:
                print(
                    msg_generated.format(
                        idx=new_merged_candle.idx,
                        ordinary_idx=new_merged_candle.last_ordinary_idx,
                        period=new_merged_candle.period,
                        high=new_merged_candle.high,
                        low=new_merged_candle.low
                    )
                )
        if is_merged:
            is_changed = True
            self._merged_candles[-1] = new_merged_candle

            if self._debug:
                print(
                    msg_merged.format(
                        idx=new_merged_candle.idx,
                        ordinary_idx=new_merged_candle.last_ordinary_idx,
                        period=new_merged_candle.period,
                        high=new_merged_candle.high,
                        low=new_merged_candle.low
                    )
                )

        return is_changed

    def generate_fractal(self) -> bool:
        """
        Generate the fractals.

        :return: bool, if new fractal was generated or last fractal was changed, return True.
                 Otherwise False.
        """
        if self.count_merged_candles < 3:
            return False

        # 声明变量类型且赋值。
        new_fractal: Optional[Fractal]
        left_candle = self._merged_candles[-3]
        middle_candle = self._merged_candles[-2]
        right_candle = self._merged_candles[-1]
        is_changed: bool = False

        # 如果 中间K线的最高价比左右K线的最高价都高：
        #     顶分型，暂定为中继。
        if middle_candle.high > left_candle.high and middle_candle.high > right_candle.high:
            new_fractal = Fractal(
                idx=self.count_fractals,
                pattern=FractalPattern.Top,
                function=FractalFunction.Continuation,
                left_candle=left_candle,
                middle_candle=middle_candle,
                right_candle=right_candle
            )

        # 如果 中间K线的最低价比左右K线的最低价都低：
        #     底分型，暂定为中继。
        elif middle_candle.low < left_candle.low and middle_candle.low < right_candle.low:
            new_fractal = Fractal(
                idx=self.count_fractals,
                pattern=FractalPattern.Bottom,
                function=FractalFunction.Continuation,
                left_candle=left_candle,
                middle_candle=middle_candle,
                right_candle=right_candle
            )

        # 否则不是分型。
        else:
            new_fractal = None

        if new_fractal is not None:

            # 如果是第1个分型：
            #     加入。
            if self.count_fractals == 0:
                self._fractals.append(new_fractal)
                is_changed = True

            # 如果不是第1个分型：
            #     新生成的分型和前分型有足够距离：
            #         加入。
            else:
                previous_fractal: Fractal = self._fractals[-1]
                distance = new_fractal.middle_candle.idx - previous_fractal.middle_candle.idx
                if distance >= self._minimum_distance:
                    self._fractals.append(new_fractal)
                    is_changed = True

        if is_changed and self._debug:
            print(
                f'\n'
                f'  生成分型：\n'
                f'    第 {self.count_fractals} 个分型，pattern = {new_fractal.pattern.value}，'
                f'function = {new_fractal.function.value}，'
                f'普通K线 idx = {middle_candle.last_ordinary_idx}。'
            )

        return is_changed

    def generate_stroke(self) -> bool:
        """
        Generate the stroke.

        :return: bool, if new stroke was generated or last stroke was changed, return True.
                 Otherwise False.
        """

        # 如果 分型数量 < 2： 退出。
        if self.count_fractals < 2:
            return False

        # debug message
        msg_generate: str = '\n  ○ 生成笔：\n    第 {idx} 根笔，趋势 = {trend}，' \
                            '起点（普通K线 idx） = {left}，终点（普通K线 idx） = {right}。\n'
        msg_extend: str = '\n  ○ 延伸笔：\n    第 {idx} 根笔，趋势 = {trend}，' \
                          '原终点起点（普通K线 idx） = {old}，现终点（普通K线 idx） = {new}。\n'

        # 申明变量类型并赋值。
        new_stroke: Stroke
        is_changed: bool = False
        fractal_p1: Fractal = self._fractals[-1]
        fractal_p2: Fractal = self._fractals[-2]

        # 如果 笔的数量 == 0：
        #     生成笔（距离由 generate_fractal 保证）。
        if self.count_strokes == 0:
            new_stroke = Stroke(
                    idx=self.count_strokes,
                    trend=Trend.Bullish if fractal_p2.pattern == FractalPattern.Bottom
                    else Trend.Bearish,
                    left_fractal=fractal_p2,
                    right_fractal=fractal_p1
                )
            self._strokes.append(new_stroke)
            is_changed = True

            if self._debug:
                print(
                    msg_generate.format(
                        idx=new_stroke.idx,
                        trend=new_stroke.trend,
                        left=new_stroke.left_fractal.middle_candle.last_ordinary_idx,
                        right=new_stroke.right_fractal.middle_candle.last_ordinary_idx
                    )
                )

        # 如果 笔的数量 >= 1：
        else:
            # 申明变量类型并赋值。
            last_stroke: Stroke = self._strokes[-1]
            is_extended: bool = False
            is_generated: bool = False

            # 如果 最新分型的idx > 最新笔的右分型idx （有新生成的分型）：
            if fractal_p1.idx > last_stroke.right_fractal.idx:

                # 如果 上升笔：
                if last_stroke.trend == Trend.Bullish:
                    # 如果 最新分型是顶分型 且 最新分型的最高价 >= 最新笔的右侧价 （顺向超越或达到）：
                    #     延伸（调整）笔
                    if fractal_p1.pattern == FractalPattern.Top and \
                            fractal_p1.extreme_price >= last_stroke.right_price:
                        is_extended = True

                    # 如果 最新分型是底分型
                    if fractal_p1.pattern == FractalPattern.Bottom:
                        is_generated = True

                # 如果 下降笔：
                else:
                    # 如果 最新分型是底分型 且 最新分型的最低价 <= 最新笔的右侧价 （顺向超越或达到）：
                    #     延伸（调整）笔
                    if last_stroke.trend == Trend.Bearish and \
                            fractal_p1.extreme_price <= last_stroke.right_price:
                        is_extended = True

                    # 如果 最新分型是顶分型
                    if fractal_p1.pattern == FractalPattern.Top:
                        is_generated = True

                # 如果 延伸（调整）笔：
                if is_extended:
                    if self._debug:
                        print(
                            msg_extend.format(
                                idx=last_stroke.idx,
                                trend=last_stroke.trend,
                                old=last_stroke.right_fractal.middle_candle.last_ordinary_idx,
                                new=fractal_p1.middle_candle.last_ordinary_idx
                            )
                        )

                    # 最新笔的右侧分型的功能 修正为 中继类型。
                    last_stroke.right_fractal.function = FractalFunction.Continuation
                    # 最新笔的右侧分型 修正为 最新分型。
                    last_stroke.right_fractal = fractal_p1
                    # 最新笔的右侧分型的功能 修正为 反转类型。
                    last_stroke.right_fractal.function = FractalFunction.Reversal

                    # 有修改
                    is_changed = True

                # 如果 生成笔：
                if is_generated:
                    new_stroke = Stroke(
                        idx=self.count_strokes,
                        trend=Trend.Bullish if fractal_p2.pattern == FractalPattern.Bottom
                        else Trend.Bearish,
                        left_fractal=fractal_p2,
                        right_fractal=fractal_p1
                    )
                    self._strokes.append(new_stroke)
                    is_changed = True

                    if self._debug:
                        print(
                            msg_generate.format(
                                idx=new_stroke.idx,
                                trend=new_stroke.trend,
                                left=new_stroke.left_fractal.middle_candle.last_ordinary_idx,
                                right=new_stroke.right_fractal.middle_candle.last_ordinary_idx
                            )
                        )

        return is_changed

    def generate_segment(self) -> bool:
        """
        Generate the segments.

        :return: bool, if new segment was generated or last segment was changed, return True.
                 Otherwise False.
        """

        # 如果 笔数量 < 3： 退出。
        if self.count_strokes < 3:
            return False

        # debug message
        msg_generate: str = '\n  ○ 生成线段：\n    第 {count} 根线段，趋势 = {trend}，' \
                            '起点（普通K线 idx） = {left}，终点（普通K线 idx） = {right}。\n'
        msg_extend: str = '\n  ○ 延伸线段：\n    第 {count} 根线段，趋势 = {trend}，' \
                          '原终点起点（普通K线 idx） = {old}，现终点（普通K线 idx） = {new}。\n'

        # 申明变量类型并赋值。
        is_changed: bool = False
        is_extended: bool = False
        is_generated: bool = False

        # 如果 线段数量 >= 1：
        if self.count_segments >= 1:
            last_segment: Segment = self._segments[-1]
            stroke_p1: Stroke = self._strokes[-1]
            stroke_p3: Stroke = self._strokes[-3]

            # --------------------
            # 生成（反转）线段
            # --------------------
            # 如果 最新笔 idx - 最新线段右侧笔 idx == 2：
            if stroke_p1.idx - last_segment.right_stroke.idx == 2:
                # 如果：
                #     1. 上升线段 且
                #     2. stroke_p1 的右值 >= 线段右值：
                # 顺向突破，延伸线段。
                if last_segment.trend == Trend.Bullish and \
                        stroke_p1.right_price >= last_segment.right_price:
                    is_extended = True

                # 如果：
                #     1. 下降线段 且
                #     2. stroke_p1 的右值 <= 线段右值：
                # 顺向突破，延伸线段。
                if last_segment.trend == Trend.Bearish and \
                        stroke_p1.right_price <= last_segment.right_price:
                    is_extended = True

            # 如果是 最新笔 idx - 最新线段右侧笔 idx == 3：
            if stroke_p1.idx - last_segment.right_stroke.idx == 3:
                # 如果：
                #     1. 上升线段 且
                #     2. 前第1笔 笔右侧值 < 前第3笔 笔右侧值 或
                #     3A. 前第1笔 笔右侧值 < 线段最后一笔的左值 或
                #     3B. 前第3笔 笔右侧值 < 线段最后一笔的左值:
                # 反转击穿，反转线段。
                if last_segment.trend == Trend.Bullish:
                    if stroke_p1.right_price < stroke_p3.right_price:
                        is_generated = True
                    elif stroke_p1.right_price <= last_segment.right_stroke.left_price and \
                            stroke_p3.right_price <= last_segment.right_stroke.left_price:
                        is_generated = True

                # 如果：
                #     1. 下降线段
                #     2. 前第3笔 笔右侧值 > 线段右侧笔的左侧值
                #     2. 前第1笔 笔右侧值 > 线段右侧笔的左侧值
                # 反转击穿。
                if last_segment.trend == Trend.Bearish:
                    if stroke_p1.right_price > stroke_p3.right_price:
                        is_generated = True
                    elif stroke_p1.right_price >= last_segment.right_stroke.left_price and \
                            stroke_p3.right_price >= last_segment.right_stroke.left_price:
                        is_generated = True

            # 声明变量类型
            new_segment: Optional[Segment] = None  # 新的线段
            overlap_high: float  # 重叠区间左值
            overlap_low: float  # 重叠区间右值

            stroke_p1: Stroke = self._strokes[-1]
            stroke_p2: Stroke = self._strokes[-2]
            stroke_p3: Stroke = self._strokes[-3]

            # stroke_p3 是 上升趋势：
            if stroke_p3.trend == Trend.Bullish:

                # 检测重叠区间
                overlap_high = min(stroke_p3.right_price, stroke_p1.right_price)
                overlap_low = max(stroke_p3.left_price, stroke_p1.left_price)

                if overlap_high > overlap_low:
                    new_segment = Segment(
                        idx=self.count_segments,
                        trend=Trend.Bullish,
                        left_stroke=stroke_p3,
                        right_stroke=stroke_p1
                    )

            # stroke_p3 是 下降趋势：
            else:

                # 检测重叠区间
                overlap_high = min(stroke_p3.left_price, stroke_p1.left_price)
                overlap_low = max(stroke_p3.right_price, stroke_p1.right_price)

                if overlap_high > overlap_low:
                    new_segment = Segment(
                        idx=self.count_segments,
                        trend=Trend.Bearish,
                        left_stroke=stroke_p3,
                        right_stroke=stroke_p1
                    )

            if new_segment is not None:
                # 如果 线段数量 == 0： 加入列表。
                if self.count_segments == 0:
                    self._segments.append(
                        new_segment
                    )
                    is_changed = True
                    if self._debug:
                        print(
                            msg_generate.format(
                                count=self.count_segments,
                                trend=new_segment.trend,
                                left=new_segment.left_ordinary_idx,
                                right=new_segment.right_ordinary_idx
                            )
                        )
        if is_generated:
            is_changed = True
        if is_extended:
            is_changed = True
        return is_changed

    def generate_pivot(self):
        """
        Generate the pivots.
        :return:
        """
        pass

    def run_step_by_step(self, high: float, low: float):
        ordinary_candle: OrdinaryCandle = OrdinaryCandle(
            high=high,
            low=low
        )
        is_changed: bool = self.generate_merged_candle(ordinary_candle)
        if is_changed:
            is_changed = self.generate_fractal()
        if is_changed:
            is_changed = self.generate_stroke()
        if is_changed:
            is_changed = self.generate_segment()

    def run_with_dataframe(self, df: pd.DataFrame, count: int = 0):
        working_count: int = len(df) if count == 0 else count
        width: int = len(str(working_count - 1)) + 1
        for idx in range(working_count):
            if self._debug:
                print(f'\n【第 {idx:>{width}} / {working_count - 1:>{width}} 轮】（按普通K线编号）')
            self.run_step_by_step(
                high=df.iloc[idx].at['high'].copy(),
                low=df.iloc[idx].at['low'].copy()
            )

    def plot(self,
             df: pd.DataFrame,
             count: int,
             show_ordinary_idx: bool = False,
             show_merged_idx: bool = False,
             show_fractal_idx: bool = False,
             merged_candle_edge_width: int = 3,
             show_all_merged: bool = False,
             hatch_merged: bool = False,
             fractal_marker_size: int = 100,
             fractal_marker_offset: int = 50
             ):
        # 白底配色
        color = mpf.make_marketcolors(
            up='red',  # 上涨K线的颜色
            down='green',  # 下跌K线的颜色
            inherit=True
        )
        # 黑色配色
        # style = {
        #     'style_name': 'background_black',
        #     'base_mpf_style':'nightclouds',
        #     'base_mpl_style': 'dark_background',
        #     'marketcolors': {
        #         'candle': {
        #             'up': 'w',
        #             'down': '#0095ff'
        #         },
        #         'edge': {
        #             'up': 'w',
        #             'down': '#0095ff'
        #         },
        #         'wick': {
        #             'up': 'w',
        #             'down': 'w'
        #         },
        #         'ohlc': {
        #             'up': 'w',
        #             'down': 'w'
        #         },
        #         'volume': {
        #             'up': 'w',
        #             'down': '#0095ff'
        #         },
        #         'vcdopcod': False,
        #         'alpha': 1.0,
        #     },
        #     'mavcolors': [
        #         '#40e0d0',
        #         '#ff00ff',
        #         '#ffd700',
        #         '#1f77b4',
        #         '#ff7f0e',
        #         '#2ca02c',
        #         '#e377c2'
        #     ],
        #     'y_on_right': False,
        #     'facecolor': '#0b0b0b',
        #     'gridcolor': '#999999',
        #     'gridstyle': '--',
        #     'rc': [
        #         ('patch.linewidth', 1.0),
        #         ('lines.linewidth', 1.0),
        #         ('figure.titlesize', 'x-large'),
        #         ('figure.titleweight', 'semibold'),
        #     ],
        # }

        style = mpf.make_mpf_style(
            marketcolors=color,
            rc={
                'font.family': 'SimHei',  # 指定默认字体：解决plot不能显示中文问题
                'axes.unicode_minus': False,  # 解决保存图像是负号'-'显示为方块的问题
            }
        )

        # 附加元素
        additional_plot: list = []

        # 分型
        fractal_t: list = []
        fractal_b: list = []
        idx_fractal_to_ordinary: int
        idx_ordinary_candle: int = 0

        for i in range(self.count_fractals):
            fractal = self._fractals[i]
            idx_fractal_to_ordinary = fractal.ordinary_idx
            idx_fractal_to_df = df.index[idx_fractal_to_ordinary]
            for j in range(idx_ordinary_candle, idx_fractal_to_ordinary):
                fractal_t.append(np.nan)
                fractal_b.append(np.nan)
            if fractal.pattern == FractalPattern.Top:
                fractal_t.append(fractal.middle_candle.high + fractal_marker_offset)
                fractal_b.append(np.nan)
            if fractal.pattern == FractalPattern.Bottom:
                fractal_t.append(np.nan)
                fractal_b.append(fractal.middle_candle.low - fractal_marker_offset)
            idx_ordinary_candle = idx_fractal_to_ordinary + 1
        for i in range(idx_ordinary_candle, count):
            fractal_t.append(np.nan)
            fractal_b.append(np.nan)

        additional_plot.append(
            mpf.make_addplot(fractal_t, type='scatter', markersize=fractal_marker_size, marker='v')
        )
        additional_plot.append(
            mpf.make_addplot(fractal_b, type='scatter', markersize=fractal_marker_size, marker='^')
        )

        # 笔
        plot_stroke: List[Tuple[str, float]] = []

        for stroke in self._strokes:
            plot_stroke.append(
                (
                    df.index[stroke.left_ordinary_idx],
                    stroke.left_price
                )
            )

        # mplfinance 的配置
        mpf_config = {}

        fig, ax_list = mpf.plot(
            df.iloc[:count],
            type='candle',
            volume=False,
            addplot=additional_plot,
            alines=dict(alines=plot_stroke, colors='k', linestyle='--', linewidths=0.05),
            show_nontrading=False,
            figratio=(40, 20),
            figscale=2,
            style=style,
            returnfig=True,
            return_width_config=mpf_config,
            warn_too_much_data=1000
        )

        candle_width = mpf_config['candle_width']
        line_width = mpf_config['line_width']

        # 生成合并K线元素。
        candle_chan = []
        for idx in range(self.count_merged_candles):
            candle = self._merged_candles[idx]

            if candle.first_ordinary_idx > count:
                break

            if not show_all_merged and candle.period == 1:
                continue
            candle_chan.append(
                Rectangle(
                    xy=(
                        candle.first_ordinary_idx - candle_width / 2,
                        candle.low
                    ),
                    width=candle.period - 1 + candle_width,
                    height=candle.high - candle.low,
                    angle=0,
                    linewidth=line_width * merged_candle_edge_width
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
                idx_ordinary_y.append(df.iloc[idx].at['low'] - 14)
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
        if show_merged_idx:
            idx_chan_x: List[int] = []
            idx_chan_y: List[float] = []
            idx_chan_value: List[str] = []

            for i in range(self.count_merged_candles):
                candle = self._merged_candles[i]
                idx_chan_x.append(candle.last_ordinary_idx - candle_width / 2)
                idx_chan_y.append(candle.high + 14)
                idx_chan_value.append(str(self._merged_candles.index(candle)))

            for i in range(len(idx_chan_x)):
                ax1.text(
                    x=idx_chan_x[i],
                    y=idx_chan_y[i],
                    s=idx_chan_value[i],
                    color='blue',
                    fontsize=7,
                    horizontalalignment='left',
                    verticalalignment='bottom'
                )

        ax1.autoscale_view()

        print('Plot done.')
