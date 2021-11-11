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
    id: int
    period: int
    left_ordinary_idx: int

    @property
    def right_ordinary_idx(self) -> int:
        return self.left_ordinary_idx + self.period - 1

    def __str__(self) -> str:
        return f'MergedCandle (id={self.id}, period={self.period}, ' \
               f'left_ordinary_idx={self.left_ordinary_idx}, ' \
               f'right_ordinary_idx={self.right_ordinary_idx}, ' \
               f'price_high={self.high}, price_low={self.low})'


@dataclass
class Fractal:
    id: int
    pattern: FractalPattern
    # function: FractalFunction
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
        return self.middle_candle.right_ordinary_idx

    def __str__(self) -> str:
        return f'Fractal (id={self.id}, ' \
               f'pattern={self.pattern.value}, ' \
               f'ordinary_idx={self.ordinary_idx}, ' \
               f'extreme_price={self.extreme_price})'
    # f'pattern={self.pattern.value}, function={self.function.value}, ' \


@dataclass
class Stroke:
    id: int
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
        return self.right_fractal.middle_candle.id - self.left_fractal.middle_candle.id

    @property
    def period_ordinary(self) -> int:
        return self.right_ordinary_idx - self.left_ordinary_idx

    @property
    def price_range(self) -> float:
        return self.right_price - self.left_price

    @property
    def slope_ordinary(self) -> float:
        return self.price_range / self.period_ordinary

    def __str__(self) -> str:
        return f'Stroke (id={self.id}, trend={self.trend.value}, period={self.period}, ' \
               f'left_merged_candle_id={self.left_fractal.middle_candle.id}, ' \
               f'right_merged_candle_id={self.right_fractal.middle_candle.id}, ' \
               f'left_ordinary_idx={self.left_ordinary_idx}, ' \
               f'right_ordinary_idx={self.right_ordinary_idx})'


@dataclass
class Segment:
    id: int
    trend: Trend
    left_stroke: Stroke
    right_stroke: Stroke
    strokes: List[int]

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
    def strokes_count(self) -> int:
        return len(self.strokes)

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
        return f'Segment (id={self.id}, trend={self.trend.value}, ' \
               f'left_ordinary_idx={self.left_ordinary_idx}, ' \
               f'right_ordinary_idx={self.right_ordinary_idx}, ' \
               f'count of strokes = {self.strokes_count}, strokes = {self.strokes})'


@dataclass
class IsolationLine:
    id: int
    candle: MergedCandle

    def __str__(self) -> str:
        return f'IsolationLine (id={self.id}, ' \
               f'merged candle id={self.candle.id}, ' \
               f'ordinary_idx={self.candle.right_ordinary_idx})'


@dataclass
class Pivot:
    id: int
    left: Fractal
    right: Fractal
    high: float
    low: float

    @property
    def left_ordinary_idx(self) -> int:
        return self.left.ordinary_idx

    @property
    def right_ordinary_idx(self) -> int:
        return self.right.ordinary_idx

    @property
    def left_price(self) -> float:
        return self.left.extreme_price

    @property
    def right_price(self) -> float:
        return self.right.extreme_price

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
        return f'Pivot (id={self.id}, ' \
               f'left_ordinary_idx={self.left_ordinary_idx}, ' \
               f'right_ordinary_idx={self.right_ordinary_idx})'


class ChanTheory:
    """
    缠论。
    """

    _log: bool
    _debug: bool
    _strict: bool
    _minimum_distance: int
    _merged_candles: List[MergedCandle]
    _fractals: List[Fractal]
    _strokes: List[Stroke]
    _segments: List[Segment]
    _isolation_lines: List[IsolationLine]
    _stroke_pivots: List[Pivot]
    _segment_pivots: List[Pivot]

    def __init__(self, strict: bool = True, log: bool = False, debug: bool = False):
        """
        Initialize the object.

        :param strict:
        :param log:
        :param debug:
        """
        self._strict = strict
        self._minimum_distance = 4 if strict else 3
        self._log = log
        self._debug = debug

        self._merged_candles = []
        self._fractals = []
        self._strokes = []
        self._segments = []
        self._isolation_lines = []
        self._stroke_pivots = []
        self._segment_pivots = []

    @property
    def count_merged_candles(self) -> int:
        """
        Count of the merged candles list.

        :return: int.
        """
        return len(self._merged_candles)

    @property
    def merged_candles(self) -> List[MergedCandle]:
        """
        The merged candle list.

        :return:
        """
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
        """
        The fractal list.

        :return:
        """
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
        """
        The stroke list.

        :return:
        """
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
        """
        The segment list.

        :return:
        """
        return deepcopy(self._segments)

    @property
    def count_isolation_lines(self) -> int:
        """
        Count of the isolation lines list.

        :return:
        """
        return len(self._isolation_lines)

    @property
    def isolation_lines(self) -> List[IsolationLine]:
        """
        The isolation lines list.

        :return:
        """
        return deepcopy(self._isolation_lines)

    @property
    def count_stroke_pivots(self) -> int:
        """
        Count of the stroke pivots list.

        :return:
        """
        return len(self._stroke_pivots)

    @property
    def stroke_pivots(self) -> List[Pivot]:
        """
        Count of the segment pivots list.

        :return:
        """
        return deepcopy(self._stroke_pivots)

    @property
    def count_segment_pivots(self) -> int:
        """
        Count of the segment pivots list.

        :return:
        """
        return len(self._segment_pivots)

    @property
    def segment_pivots(self) -> List[Pivot]:
        """
        The segment pivots list.

        :return:
        """
        return deepcopy(self._segment_pivots)

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
        msg_generated: str = '\n  ● 生成K线：\n    第 {id} 根合并K线，' \
                             '起始idx（普通K线）= {ordinary_idx}，周期 = {period}，' \
                             '高点 = {high}，低点 = {low}。'
        msg_merged: str = '\n  ● 合并K线：\n    第 {id} 根合并K线，' \
                          '起始 idx（普通K线）= {ordinary_idx}，周期 = {period}，' \
                          '高点 = {high}，低点 = {low}。'

        # 申明变量类型并赋值。
        is_changed: bool = False
        is_generated: bool = False
        is_merged: bool = False

        new_merged_candle: Optional[MergedCandle] = None

        # 前合并K线不存在：
        #     直接加入。
        if self.count_merged_candles == 0:
            new_merged_candle = MergedCandle(
                    id=self.count_merged_candles,
                    high=ordinary_candle.high,
                    low=ordinary_candle.low,
                    period=1,
                    left_ordinary_idx=0
                )
            is_generated = True

        # 前合并K线存在：
        else:
            merged_candle_p1: MergedCandle = self._merged_candles[-1]  # 前1合并K线。

            # 如果没有包含关系：
            #     加入。
            if not self.is_inclusive(merged_candle_p1, ordinary_candle):
                new_merged_candle = MergedCandle(
                    id=self.count_merged_candles,
                    high=ordinary_candle.high,
                    low=ordinary_candle.low,
                    period=1,
                    left_ordinary_idx=merged_candle_p1.right_ordinary_idx + 1
                )
                is_generated = True

            # 如果有包含关系：
            else:

                # 如果前合并K线是第一根合并K线：
                #     取前合并K线和新普通K线的最大范围。
                if self.count_merged_candles == 1:
                    new_merged_candle = MergedCandle(
                        id=merged_candle_p1.id,
                        high=max(
                            merged_candle_p1.high,
                            ordinary_candle.high
                        ),
                        low=min(
                            merged_candle_p1.low,
                            ordinary_candle.low
                        ),
                        period=merged_candle_p1.period + 1,
                        left_ordinary_idx=merged_candle_p1.left_ordinary_idx
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
                            id=merged_candle_p1.id,
                            high=max(
                                merged_candle_p1.high,
                                ordinary_candle.high
                            ),
                            low=max(
                                merged_candle_p1.low,
                                ordinary_candle.low
                            ),
                            period=merged_candle_p1.period + 1,
                            left_ordinary_idx=merged_candle_p1.left_ordinary_idx
                        )
                        is_merged = True

                    # 如果 前1缠论K线 与 前2缠论K线： 高点 > 高点 且 低点 > 低点：
                    #     合并取 低-低。
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
                            left_ordinary_idx=merged_candle_p1.left_ordinary_idx
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

            if self._log:
                print(
                    msg_generated.format(
                        id=new_merged_candle.id + 1,
                        ordinary_idx=new_merged_candle.right_ordinary_idx,
                        period=new_merged_candle.period,
                        high=new_merged_candle.high,
                        low=new_merged_candle.low
                    )
                )
        if is_merged:
            is_changed = True
            self._merged_candles[-1] = new_merged_candle

            if self._log:
                print(
                    msg_merged.format(
                        id=new_merged_candle.id + 1,
                        ordinary_idx=new_merged_candle.right_ordinary_idx,
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

        # debug message.
        msg_generated: str = '\n  ● 生成分型：\n' \
                             '    第 {id} 个分型，模式 = {pattern}，idx（普通K线）= {ordinary_idx}。'

        # 声明变量类型且赋值。
        new_fractal: Optional[Fractal]
        left_candle = self._merged_candles[-3]
        middle_candle = self._merged_candles[-2]
        right_candle = self._merged_candles[-1]
        is_changed: bool = False

        # 如果：
        #     最新的合并K线的id == 最新的分型的右侧合并K线的id
        # 退出
        if self.count_fractals >= 1 and \
                self._merged_candles[-1].id == self._fractals[-1].right_candle.id:
            return False

        # 如果：
        #     中间K线的最高价比左右K线的最高价都高：
        # 顶分型。
        if middle_candle.high > left_candle.high and middle_candle.high > right_candle.high:
            new_fractal = Fractal(
                id=self.count_fractals,
                pattern=FractalPattern.Top,
                left_candle=left_candle,
                middle_candle=middle_candle,
                right_candle=right_candle
            )

        # 如果：
        #     中间K线的最低价比左右K线的最低价都低：
        # 底分型。
        elif middle_candle.low < left_candle.low and middle_candle.low < right_candle.low:
            new_fractal = Fractal(
                id=self.count_fractals,
                pattern=FractalPattern.Bottom,
                left_candle=left_candle,
                middle_candle=middle_candle,
                right_candle=right_candle
            )

        # 否则不是分型。
        else:
            new_fractal = None

        if new_fractal is not None:
            self._fractals.append(new_fractal)
            is_changed = True

            if self._log:
                print(
                    msg_generated.format(
                        id=new_fractal.id + 1,
                        pattern=new_fractal.pattern.value,
                        ordinary_idx=new_fractal.ordinary_idx
                    )
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
        msg_generate: str = '\n  ● 生成笔：\n    第 {id} 根笔，趋势 = {trend}，' \
                            '起点 idx（普通K线 ）= {left}，终点 idx（普通K线）= {right}。'
        msg_extend: str = '\n  ● 延伸笔：\n    第 {id} 根笔，趋势 = {trend}，' \
                          '原终点 idx（普通K线）= {old}，现终点 idx（普通K线）= {new}。'

        # 如果 笔的数量 == 0：
        #     向前穷举 fractal_p2，如果：
        #         1. fractal_p1 和 fractal_p2 类型不同
        #         2. fractal_p1 和 fractal_p2 的距离满足要求。
        #   生成笔。
        if self.count_strokes == 0:

            # 申明变量类型并赋值。
            new_stroke: Stroke
            distance: int
            last_fractal: Fractal = self._fractals[-1]
            fractal_p2: Fractal

            if self._debug:
                print(
                    f'\n  ○ 尝试生成笔：目前共有分型 {self.count_fractals} 个。\n'
                    f'    右分型，id = {last_fractal.id}，pattern = {last_fractal.pattern.value}，'
                    f'idx（普通K线）= {last_fractal.middle_candle.id}'
                )
            for i in range(0, last_fractal.id):
                fractal_p2 = self._fractals[i]
                distance = last_fractal.middle_candle.id - fractal_p2.middle_candle.id
                if self._debug:
                    print(
                        f'    左分型，id = {fractal_p2.id}，pattern = {fractal_p2.pattern.value}，'
                        f'idx（普通K线）= {fractal_p2.middle_candle.id}，距离 = {distance}，'
                        f'{"满足" if distance >= self._minimum_distance else "不满足"}'
                    )
                if distance >= self._minimum_distance and \
                        fractal_p2.pattern != last_fractal.pattern:
                    new_stroke = Stroke(
                        id=self.count_strokes,
                        trend=Trend.Bullish if fractal_p2.pattern == FractalPattern.Bottom
                        else Trend.Bearish,
                        left_fractal=fractal_p2,
                        right_fractal=last_fractal
                    )
                    self._strokes.append(new_stroke)

                    if self._log:
                        print(
                            msg_generate.format(
                                id=new_stroke.id + 1,
                                trend=new_stroke.trend,
                                left=new_stroke.left_ordinary_idx,
                                right=new_stroke.right_ordinary_idx
                            )
                        )

                    return True

        # 如果 笔的数量 >= 1：
        else:

            # 申明变量类型并赋值。
            last_stroke: Stroke = self._strokes[-1]
            last_fractal: Fractal = self._fractals[-1]

            # 如果：
            #     A1. last_stroke 的 trend 是 上升，且
            #     A2. fractal_p1 是顶分型，且
            #     A3. fractal_p1 的最高价 >= last_stroke 的右侧价 （顺向超越或达到）：
            #   或
            #     B1. last_stroke 的 trend 是 下降，且
            #     B2. fractal_p1 是 底分型，且
            #     B3. fractal_p1 的最高价 <= last_stroke 的右侧价 （顺向超越或达到）：
            # 延伸（调整）笔。

            if self._debug:
                print(
                    f'\n  ○ 尝试顺向延伸笔：目前共有分型 {self.count_fractals} 个。'
                    f'\n    最新笔   id = {last_stroke.id}，{last_stroke.trend}，'
                    f'右侧价 = {last_stroke.right_price}，'
                    f'\n    最新分型 id = {last_fractal.id}，{last_fractal.pattern}，'
                    f'右侧价 = {last_fractal.extreme_price}'
                )

            if (
                    last_stroke.trend == Trend.Bullish and
                    last_fractal.pattern == FractalPattern.Top and
                    last_fractal.extreme_price >= last_stroke.right_price
            ) or (
                    last_stroke.trend == Trend.Bearish and
                    last_stroke.trend == Trend.Bearish and
                    last_fractal.extreme_price <= last_stroke.right_price
            ):

                if self._log:
                    print(
                        msg_extend.format(
                            id=last_stroke.id + 1,
                            trend=last_stroke.trend,
                            old=last_stroke.right_ordinary_idx,
                            new=last_fractal.middle_candle.right_ordinary_idx
                        )
                    )

                last_stroke.right_fractal = last_fractal

                return True

            # 如果：
            #     A1. last_stroke 的 trend 是 上升，且
            #     A2. fractal_p1 是 底分型，且
            #     A3. fractal_p1 的3根 merged candle 的最高价 < last_stroke 的 右侧价，且
            #   或
            #     B1. last_stroke 的 trend 是 下降，且
            #     B2. fractal_p1 是 顶分型，且
            #     B3. fractal_p1 的3根 merged candle 的最低价 > last_stroke 的 右侧价，且
            #   且
            #     3. fractal_p1 和 last_stroke 的右分型的距离满足要求，且
            # 生成（反向）笔。
            distance = last_fractal.middle_candle.id - last_stroke.right_fractal.middle_candle.id

            if self._debug:
                print(
                    f'\n  ○ 尝试反向生成笔：目前共有分型 {self.count_fractals} 个。'
                    f'\n    最新笔   id = {last_stroke.id}，{last_stroke.trend}，'
                    f'右侧分型 id= {last_stroke.right_fractal.id}，'
                    f'idx = {last_stroke.right_ordinary_idx}'
                    f'\n    最新分型 id = {last_fractal.id}，{last_fractal.pattern}，'
                    f'idx = {last_fractal.ordinary_idx}，距离 = {distance}'
                )

            if (
                    (
                            last_stroke.trend == Trend.Bullish and
                            last_fractal.pattern == FractalPattern.Bottom and
                            max(
                                last_fractal.left_candle.high,
                                last_fractal.middle_candle.high,
                                last_fractal.right_candle.high
                            ) < last_stroke.right_price
                    ) or (
                            last_stroke.trend == Trend.Bearish and
                            last_fractal.pattern == FractalPattern.Top and
                            min(
                                last_fractal.left_candle.low,
                                last_fractal.middle_candle.low,
                                last_fractal.right_candle.low
                            ) > last_stroke.right_price
                    )
            ) and distance >= self._minimum_distance:

                new_stroke: Stroke = Stroke(
                    id=self.count_strokes,
                    trend=Trend.Bullish if last_stroke.trend == Trend.Bearish
                    else Trend.Bearish,
                    left_fractal=last_stroke.right_fractal,
                    right_fractal=last_fractal
                )
                self._strokes.append(new_stroke)

                if self._log:
                    print(
                        msg_generate.format(
                            id=new_stroke.id + 1,
                            trend=new_stroke.trend,
                            left=new_stroke.left_fractal.middle_candle.right_ordinary_idx,
                            right=new_stroke.right_fractal.middle_candle.right_ordinary_idx
                        )
                    )

                return True

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
        msg_generate: str = '\n  ● 生成线段：\n    第 {id} 根线段，趋势 = {trend}，' \
                            '起点（普通K线 idx） = {left}，终点（普通K线 idx） = {right}。\n'
        msg_extend: str = '\n  ● 延伸线段：\n    第 {id} 根线段，趋势 = {trend}，' \
                          '原终点起点（普通K线 idx） = {old}，现终点（普通K线 idx） = {new}。\n'

        # 如果 线段的数量 == 0：
        #     向前穷举 stroke_p3，如果：
        #         stroke_p3 和 stroke_p1 有重叠：
        #   生成线段。
        if self.count_segments == 0:

            # 申明变量类型并赋值。
            stroke_p1: Stroke = self._strokes[-1]
            stroke_p2: Stroke
            stroke_p3: Stroke
            overlap_high: float = 0.0   # 重叠区间高值
            overlap_low: float = 0.0    # 重叠区间低值

            if self._debug:
                print(
                    f'\n  ○ 尝试生成首根线段：'
                    f'目前共有线段 {self.count_segments} 根，笔 {self.count_strokes} 根。\n'
                    f'    向前（左）第1根笔，id = {stroke_p1.id}，'
                    f'high = {max(stroke_p1.left_price, stroke_p1.right_price)}，'
                    f'low = {min(stroke_p1.left_price, stroke_p1.right_price)}'
                )
            for i in range(0, stroke_p1.id - 1):
                stroke_p3 = self._strokes[i]
                stroke_p2 = self._strokes[i + 1]

                # 如果 前1笔 的趋势与 前3笔 不一致，重新循环。
                # （理论上不可能，但是留做保险。）
                if stroke_p3.trend != stroke_p1.trend:
                    continue

                # 上升笔
                if stroke_p1.trend == Trend.Bullish:
                    # 前1笔的左侧价 >= 前3笔的左侧价（前1笔的左侧价必须 < 前3笔的右侧价）
                    if stroke_p1.left_price >= stroke_p3.left_price:
                        overlap_low = stroke_p1.left_price
                        if stroke_p1.right_price >= stroke_p3.right_price:
                            overlap_high = stroke_p3.right_price
                        else:
                            overlap_high = stroke_p1.right_price

                    # 前1笔的左侧价 < 前3笔的左侧价
                    else:
                        overlap_low = stroke_p3.left_price
                        if stroke_p1.right_price >= stroke_p3.right_price:
                            overlap_high = stroke_p3.right_price
                        elif stroke_p3.left_price <= stroke_p1.right_price < stroke_p3.right_price:
                            overlap_high = stroke_p3.left_price
                        elif stroke_p1.right_price < stroke_p3.left_price:
                            return False

                # 下降笔
                else:
                    # 前1笔的左侧价 <= 前3笔的左侧价（前1笔的左侧价必须 > 前3笔的右侧价）
                    if stroke_p1.left_price <= stroke_p3.left_price:
                        overlap_low = stroke_p1.right_price
                        if stroke_p1.right_price <= stroke_p3.right_price:
                            overlap_high = stroke_p3.right_price
                        else:
                            overlap_high = stroke_p1.right_price

                    # 前1笔的左侧价 > 前3笔的左侧价
                    else:
                        overlap_high = stroke_p3.left_price
                        if stroke_p1.right_price <= stroke_p3.right_price:
                            overlap_low = stroke_p3.right_price
                        elif stroke_p3.right_price <= stroke_p1.right_price < stroke_p3.left_price:
                            overlap_low = stroke_p1.right_price
                        elif stroke_p1.right_price > stroke_p3.left_price:
                            return False

                if self._debug:
                    print(
                        f'    向前（左）第{stroke_p1.id - stroke_p3.id + 1}根笔，id = {stroke_p3.id}，'
                        f'high = {max(stroke_p3.left_price, stroke_p3.right_price)}，'
                        f'low = {min(stroke_p3.left_price, stroke_p3.right_price)}，'
                        f'overlap high = {overlap_high}，overlap low = {overlap_low}'
                    )

                if overlap_high > overlap_low:

                    new_segment: Segment = Segment(
                        id=self.count_segments,
                        trend=Trend.Bullish if stroke_p1.trend == Trend.Bullish else Trend.Bearish,
                        left_stroke=stroke_p3,
                        right_stroke=stroke_p1,
                        strokes=[stroke_p3.id, stroke_p2.id, stroke_p1.id]
                    )
                    self._segments.append(new_segment)

                    new_isolation_line: IsolationLine = IsolationLine(
                        id=self.count_isolation_lines,
                        candle=stroke_p3.left_fractal.middle_candle
                    )
                    self._isolation_lines.append(new_isolation_line)

                    if self._log:
                        print(
                            msg_generate.format(
                                id=new_segment.id + 1,
                                trend=new_segment.trend,
                                left=new_segment.left_ordinary_idx,
                                right=new_segment.right_ordinary_idx
                            )
                        )

                    return True

        # 如果 线段数量 >= 1：
        else:
            last_segment: Segment = self._segments[-1]
            last_stroke: Stroke = self._strokes[-1]

            if last_stroke.id - last_segment.right_stroke.id < 2:
                pass

            # 在 最新笔的 id - 最新线段的右侧笔的 id == 2 时：
            elif last_stroke.id - last_segment.right_stroke.id == 2:

                if self._debug:
                    print(
                        f'\n  ○ 尝试顺向延伸线段：'
                        f'目前共有线段 {self.count_segments} 根，笔 {self.count_strokes} 根。\n'
                        f'    最新线段的最新笔 id = {last_segment.right_stroke.id}，'
                        f'trend = {last_segment.right_stroke.trend}，'
                        f'price left = {last_segment.left_price}，'
                        f'price right = {last_segment.right_price}\n'
                        f'    最新          笔 id = {last_stroke.id}，'
                        f'trend = {last_stroke.trend}，'
                        f'price left = {last_stroke.left_price}，'
                        f'price right = {last_stroke.right_price}'
                    )

                # 如果：
                #     A1. 上升线段，且
                #     A2. 线段后第2笔 是 上升笔，且
                #     A3. 线段后第2笔的右侧价 >= 线段右侧价
                #   或
                #     B1. 下降线段，且
                #     B2. 线段后第2笔 是 下降笔，且
                #     B3. 线段后第2笔的右侧价 <= 线段右侧价
                # 延伸线段。
                if (
                        last_segment.trend == Trend.Bullish and
                        last_stroke.trend == Trend.Bullish and
                        last_stroke.right_price >= last_segment.right_price
                ) or (
                        last_segment.trend == Trend.Bearish and
                        last_stroke.trend == Trend.Bearish and
                        last_stroke.right_price <= last_segment.right_price
                ):

                    if self._log:
                        print(
                            msg_extend.format(
                                id=last_segment.id + 1,
                                trend=last_segment.trend,
                                old=last_segment.right_ordinary_idx,
                                new=last_stroke.right_ordinary_idx
                            )
                        )
                    for i in range(last_segment.right_stroke.id + 1, last_stroke.id + 1):
                        last_segment.strokes.append(i)
                    last_segment.right_stroke = last_stroke

                    return True

            # 在 最新笔的 id - 最新线段的右侧笔的 id == 3 时：
            elif last_stroke.id - last_segment.right_stroke.id == 3:
                stroke_n1: Stroke = self._strokes[-3]
                stroke_n2: Stroke = self._strokes[-2]
                stroke_n3: Stroke = self._strokes[-1]

                if self._debug:
                    print(
                        f'\n  ○ 尝试生成反向线段：'
                        f'目前共有线段 {self.count_segments} 根，笔 {self.count_strokes} 根。\n'
                        f'    最新线段的最新笔 id = {last_segment.right_stroke.id}，'
                        f'trend = {last_segment.right_stroke.trend}，'
                        f'price left = {last_segment.left_price}，'
                        f'price right = {last_segment.right_price}\n'
                        f'    最新线段的右侧第1笔 id = {stroke_n1.id}，'
                        f'trend = {stroke_n1.trend}，'
                        f'price left = {stroke_n1.left_price}，'
                        f'price right = {stroke_n1.right_price}\n'
                        f'    最新线段的右侧第3笔 id = {stroke_n3.id}，'
                        f'trend = {stroke_n3.trend}，'
                        f'price left = {stroke_n3.left_price}，'
                        f'price right = {stroke_n3.right_price}'
                    )

                # 如果：
                #     A1. 上升线段，且
                #         A2A. 线段后第1笔的右侧价 <= 线段右侧笔的左侧价，且
                #         A2B. 线段后第3笔的右侧价 <  线段右侧笔的左侧价
                #       或
                #         A3. 线段后第3笔的右侧价 <=  线段后第1笔的右侧价
                #   或
                #     B1. 下降线段，且
                #         B2A. 线段后第1笔的右侧价 >= 线段右侧笔的左侧价，且
                #         B2B. 线段后第3笔的右侧价 >  线段右侧笔的左侧价
                #       或
                #         B3. 线段后第2笔的右侧价 >= 线段后第1笔的右侧价
                # 生成反向线段。
                if (
                        last_segment.trend == Trend.Bullish and
                        stroke_n3.trend == Trend.Bearish and
                        (
                                stroke_n3.right_price <= stroke_n1.right_price or
                                (
                                        stroke_n1.right_price
                                        <= last_segment.right_stroke.left_price
                                        and
                                        stroke_n3.right_price
                                        < last_segment.right_stroke.left_price
                                )
                        )
                ) or (
                        last_segment.trend == Trend.Bearish and
                        stroke_n3.trend == Trend.Bullish and
                        (
                                stroke_n3.right_price >= stroke_n1.right_price or
                                (
                                        stroke_n1.right_price
                                        >= last_segment.right_stroke.left_price
                                        and
                                        stroke_n3.right_price
                                        > last_segment.right_stroke.left_price
                                )
                        )
                ):
                    new_segment = Segment(
                        id=self.count_segments,
                        trend=Trend.Bullish
                        if stroke_n3.trend == Trend.Bullish else Trend.Bearish,
                        left_stroke=stroke_n1,
                        right_stroke=stroke_n3,
                        strokes=[stroke_n1.id, stroke_n2.id, stroke_n3.id]
                    )
                    self._segments.append(new_segment)

                    new_isolation_line: IsolationLine = IsolationLine(
                        id=self.count_isolation_lines,
                        candle=stroke_n1.left_fractal.middle_candle
                    )
                    self._isolation_lines.append(new_isolation_line)

                    if self._log:
                        print(
                            msg_generate.format(
                                id=new_segment.id + 1,
                                trend=new_segment.trend,
                                left=new_segment.left_ordinary_idx,
                                right=new_segment.right_ordinary_idx
                            )
                        )
                    # last_segment.right_stroke = self._strokes[stroke_n1.id - 1]

                    return True

            # 在 最新笔的 id - 最新线段的右侧笔的 id > 3 时：
            #     既不能顺向突破（id差 == 2）
            #     又不能反向突破（id差 == 3）
            # 跳空。
            else:

                stroke_p1: Stroke = self._strokes[-1]
                stroke_p3: Stroke = self._strokes[-3]

                if self._debug:
                    print(
                        f'\n  ○ 尝试生成跳空线段：'
                        f'目前共有线段 {self.count_segments} 根，笔 {self.count_strokes} 根。\n'
                        f'    最新线段的最新笔 id = {last_segment.right_stroke.id}，'
                        f'trend = {last_segment.right_stroke.trend}，'
                        f'price left = {last_segment.left_price}，'
                        f'price right = {last_segment.right_price}\n'
                        f'    向前（左）第1笔 id = {stroke_p1.id}，'
                        f'trend = {stroke_p1.trend}，'
                        f'price left = {stroke_p1.left_price}，'
                        f'price right = {stroke_p1.right_price}\n'
                        f'    向前（左）第3笔 id = {stroke_p3.id}，'
                        f'trend = {stroke_p3.trend}，'
                        f'price left = {stroke_p3.left_price}，'
                        f'price right = {stroke_p3.right_price}'
                    )

                # 如果：
                #     A1. stroke_p1 是 上升笔，且
                #     A2. stroke_p3 的 左侧价 <= stroke_p1 的 左侧价 < stroke_p3 的 右侧价，且
                #     A3. stroke_p1 的 右侧价 > stroke_p3 的 右侧价
                #   或
                #     B1. stroke_p1 是 下降笔，且
                #     B2. stroke_p3 的 左侧价 <= stroke_p1 的 左侧价 < stroke_p3 的 右侧价，且
                #     B3. stroke_p1 的 右侧价 < stroke_p3 的 右侧价
                # 生成跳空线段。
                if (
                        stroke_p1.trend == Trend.Bullish and
                        stroke_p3.left_price <= stroke_p1.left_price < stroke_p3.right_price
                        < stroke_p1.right_price
                ) or (
                        stroke_p1.trend == Trend.Bearish and
                        stroke_p1.right_price < stroke_p3.right_price <= stroke_p1.left_price
                        < stroke_p3.left_price
                ):
                    new_segment: Segment

                    # 如果 stroke_p1 与 last_segment 同向：
                    if stroke_p1.trend == last_segment.trend:
                        # 如果 stroke_p3 的 id 与 last_segment 的右侧笔的 id 相差 2：
                        # 延伸 last_segment
                        if stroke_p3.id - last_segment.right_stroke.id == 2:
                            if self._log:
                                print(
                                    msg_extend.format(
                                        id=last_segment.id + 1,
                                        trend=last_segment.trend,
                                        old=last_segment.right_ordinary_idx,
                                        new=stroke_p1.right_ordinary_idx
                                    )
                                )
                            for i in range(last_segment.right_stroke.id + 1, stroke_p1.id + 1):
                                last_segment.strokes.append(i)
                            last_segment.right_stroke = stroke_p1

                            return True

                        # 其他情况（ stroke_p3 的 id 与 last_segment 的右侧笔的 id 相差 4 以上）：
                        # 补一根反向线段，起点是 last_segment 的右端点，终点是 stroke_p3 的左端点。
                        else:
                            new_segment = Segment(
                                id=self.count_segments,
                                trend=Trend.Bearish
                                if stroke_p1.trend == Trend.Bullish else Trend.Bullish,
                                left_stroke=self._strokes[last_segment.right_stroke.id + 1],
                                right_stroke=self._strokes[stroke_p3.id - 1],
                                strokes=[
                                    i for i in range(last_segment.right_stroke.id + 1, stroke_p3.id)
                                ]
                            )
                            self._segments.append(new_segment)

                            new_isolation_line: IsolationLine = IsolationLine(
                                id=self.count_isolation_lines,
                                candle=new_segment.left_stroke.left_fractal.middle_candle
                            )
                            self._isolation_lines.append(new_isolation_line)

                            if self._log:
                                print(
                                    msg_generate.format(
                                        id=new_segment.id + 1,
                                        trend=new_segment.trend,
                                        left=new_segment.left_ordinary_idx,
                                        right=new_segment.right_ordinary_idx
                                    )
                                )
                            return True
                    # 如果 stroke_p1 与 last_segment 反向：
                    else:
                        new_segment = Segment(
                            id=self.count_segments,
                            trend=Trend.Bullish
                            if stroke_p1.trend == Trend.Bullish else Trend.Bearish,
                            left_stroke=self._strokes[last_segment.right_stroke.id + 1],
                            right_stroke=stroke_p1,
                            strokes=[
                                i for i in range(last_segment.right_stroke.id + 1, stroke_p1.id + 1)
                            ]
                        )
                        self._segments.append(new_segment)

                        new_isolation_line: IsolationLine = IsolationLine(
                            id=self.count_isolation_lines,
                            candle=new_segment.left_stroke.left_fractal.middle_candle
                        )
                        self._isolation_lines.append(new_isolation_line)

                        if self._log:
                            print(
                                msg_generate.format(
                                    id=new_segment.id + 1,
                                    trend=new_segment.trend,
                                    left=new_segment.left_ordinary_idx,
                                    right=new_segment.right_ordinary_idx
                                )
                            )

                        return True

        return False

    def generate_stroke_pivot(self) -> bool:
        """
        Generate the pivots.
        :return:
        """
        return False

    def run_step_by_step(self, high: float, low: float):
        """
        Run step by step, with a pair of float.

        :param high: float, the high price of new candle.
        :param low:  float, the low price of new candle.
        :return: None.
        """
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
        if is_changed:
            is_changed = self.generate_stroke_pivot()

    def run_with_dataframe(self, df: pd.DataFrame, count: int = 0) -> None:
        """
        Run with lots of data in pandas DataFrame format.

        :param df:    pandas DataFrame. A series of bar data, the index should be DatetimeIndex,
                      and the columns should contains open, high, low, close and volume.
        :param count: int. How many rows of df should be calculate.
        :return: None.
        """
        working_count: int = len(df) if count == 0 else count
        width: int = len(str(working_count - 1)) + 1

        for idx in range(working_count):

            if self._log:
                print(f'\n【第 {idx:>{width}} / {working_count - 1:>{width}} 轮】（按普通K线编号）')

            self.run_step_by_step(
                high=df.iloc[idx].at['high'].copy(),
                low=df.iloc[idx].at['low'].copy()
            )

            if self._log:
                print(f'\n  ■ 处理完毕。')

                # 合并K线
                print(f'\n    合并K线数量： {self.count_merged_candles}。')
                for i in range(1, 4):
                    if self.count_merged_candles >= i:
                        candle = self._merged_candles[-i]
                        print(
                            f'      向前（左）第{i}根合并K线：'
                            f'自 {candle.left_ordinary_idx} 至 {candle.right_ordinary_idx}，'
                            f'周期 = {candle.period}；'
                        )
                    else:
                        print(f'      向前（左）第{i}根合并K线：不存在；')

                # 分型
                print(f'\n    分型数量： {self.count_fractals}。')
                for i in range(1, 3):
                    if self.count_fractals >= i:
                        fractal = self._fractals[-i]
                        print(
                            f'      向前（左）第{i}个分型：id = {fractal.id}，'
                            f'pattern = {fractal.pattern.value}，'
                            f'idx（普通K线）= {fractal.ordinary_idx}。'
                        )
                    else:
                        print(f'      向前（左）第{i}个分型：不存在。')

                # 笔
                print(f'\n    笔数量： {self.count_strokes}。')
                for i in range(1, 4):
                    if self.count_strokes >= i:
                        stroke = self._strokes[-i]
                        print(
                            f'      向前（左）第{i}个笔：id = {stroke.id}，trend = {stroke.trend.value}，'
                            f'idx（普通K线）= '
                            f'{stroke.left_ordinary_idx} ~ {stroke.right_ordinary_idx}，'
                            f'price = {stroke.left_price} ~ {stroke.right_price}。'
                        )
                    else:
                        print(f'      向前（左）第{i}个笔：不存在。')

                # 线段
                print(f'\n    线段数量： {self.count_segments}。')
                for i in range(1, 4):
                    if self.count_segments >= i:
                        segment = self._segments[-i]
                        print(
                            f'      向前（左）第{i}个线段：id = {segment.id}，trend = {segment.trend.value}，'
                            f'idx（普通K线）= '
                            f'{segment.left_ordinary_idx} ~ {segment.right_ordinary_idx}，'
                            f'price = {segment.left_price} ~ {segment.right_price}。'
                        )
                    else:
                        print(f'      向前（左）第{i}个线段：不存在。')

                # 笔中枢
                print(f'\n    笔中枢数量： {self.count_stroke_pivots}。')
                for i in range(1, 3):
                    if self.count_stroke_pivots >= i:
                        pivot = self._stroke_pivots[-i]
                        print(
                            f'      向前（左）第{i}个笔中枢：id = {pivot.id}，'
                            f'idx（普通K线）= {pivot.left_ordinary_idx} ~ {pivot.right_ordinary_idx}，'
                            f'price = {pivot.left_price} ~ {pivot.right_price}。'
                        )
                    else:
                        print(f'      向前（左）第{i}个笔中枢：不存在。')

                # 段中枢
                print(f'\n    段中枢数量： {self.count_segment_pivots}。')
                for i in range(1, 3):
                    if self.count_segment_pivots >= i:
                        pivot = self._segment_pivots[-i]
                        print(
                            f'      向前（左）第{i}个段中枢：id = {pivot.id}，'
                            f'idx（普通K线）= {pivot.left_ordinary_idx} ~ {pivot.right_ordinary_idx}，'
                            f'price = {pivot.left_price} ~ {pivot.right_price}。'
                        )
                    else:
                        print(f'      向前（左）第{i}个段中枢：不存在。')

    def plot(self,
             df: pd.DataFrame,
             count: int,
             show_ordinary_id: bool = False,
             show_merged_id: bool = False,
             show_fractal_id: bool = False,
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
        previous_fractal_ordinary_idx: int = 0

        for i in range(self.count_fractals):
            fractal = self._fractals[i]

            # idx from previous fractal.ordinary_idx to current fractal.ordinary_idx
            for j in range(previous_fractal_ordinary_idx, fractal.ordinary_idx):
                fractal_t.append(np.nan)
                fractal_b.append(np.nan)

            if fractal.pattern == FractalPattern.Top:
                fractal_t.append(fractal.middle_candle.high + fractal_marker_offset)
                fractal_b.append(np.nan)
            else:
                fractal_t.append(np.nan)
                fractal_b.append(fractal.middle_candle.low - fractal_marker_offset)
            previous_fractal_ordinary_idx = fractal.ordinary_idx + 1

        for i in range(previous_fractal_ordinary_idx, count):
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
        plot_stroke.append(
            (
                df.index[self._strokes[-1].right_ordinary_idx],
                self._strokes[-1].right_price
            )
        )

        # 线段
        plot_segment: List[Tuple[str, float]] = []
        for segment in self._segments:
            plot_segment.append(
                (
                    df.index[segment.left_ordinary_idx],
                    segment.left_price
                )
            )
        plot_segment.append(
            (
                df.index[self._segments[-1].right_ordinary_idx],
                self._segments[-1].right_price
            )
        )

        # 同级别分解线
        plot_isolation: List[str] = []
        for isolation in self._isolation_lines:
            plot_isolation.append(
                df.index[isolation.candle.right_ordinary_idx]
            )

        # mplfinance 的配置
        mpf_config = {}

        fig, ax_list = mpf.plot(
            df.iloc[:count],
            type='candle',
            volume=False,
            addplot=additional_plot,
            vlines={
                'vlines': plot_isolation,
                'colors': 'g',
                'linewidths': 2
            },
            alines={
                'alines': [plot_stroke, plot_segment],
                'colors': ['k', 'r'],
                'linestyle': '--',
                'linewidths': 0.01
            },
            show_nontrading=False,
            figratio=(40, 20),
            figscale=2,
            style=style,
            returnfig=True,
            return_width_config=mpf_config,
            warn_too_much_data=1000
        )

        if self._debug:
            for k, v in mpf_config.items():
                print(k, ': ', v)

        candle_width = mpf_config['candle_width']
        line_width = mpf_config['line_width']

        # 生成合并K线元素。
        candle_chan = []
        for idx in range(self.count_merged_candles):
            candle = self._merged_candles[idx]

            if candle.left_ordinary_idx > count:
                break

            if not show_all_merged and candle.period == 1:
                continue
            candle_chan.append(
                Rectangle(
                    xy=(
                        candle.left_ordinary_idx - candle_width / 2,
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
        if show_ordinary_id:
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
        if show_merged_id:
            idx_chan_x: List[int] = []
            idx_chan_y: List[float] = []
            idx_chan_value: List[str] = []

            for i in range(self.count_merged_candles):
                candle = self._merged_candles[i]
                idx_chan_x.append(candle.right_ordinary_idx - candle_width / 2)
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
