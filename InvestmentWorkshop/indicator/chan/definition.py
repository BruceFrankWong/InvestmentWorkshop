# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass


class Action(Enum):
    NothingChanged = '没有任何改变'

    MergedCandleGenerated = '合并K线已生成'
    MergedCandleUpdated = '合并K线已更新'

    FractalGenerated = '分型已生成'
    FractalConfirmed = '分型已确认'
    FractalDropped = '分型已丢弃'

    StrokeGenerated = '笔已生成'
    StrokeExtended = '笔已延伸'

    SegmentGenerated = '线段已生成'
    SegmentExtended = '线段已延伸'
    SegmentExpanded = '线段已扩张'

    IsolationLineGenerated = '同级别分解线已生成'

    StrokePivotGenerated = '笔中枢已生成'
    StrokePivotExtended = '笔中枢已延伸'

    SegmentPivotGenerated = '段中枢已生成'
    SegmentPivotExtended = '段中枢已延伸'

    def __str__(self) -> str:
        return self.value


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


class Direction(Enum):
    Left = '左'
    Right = '右'


class Trend(Enum):
    U = '上升'
    D = '下降'
    Up = '上升'
    Down = '下降'
    Bullish = '上升'
    Bearish = '下降'

    def __str__(self) -> str:
        return self.value


class LinearElementMode(Enum):
    UDU = '上下上'
    DUD = '下上下'


@dataclass
class OrdinaryCandle:
    high: float
    low: float

    def __str__(self) -> str:
        return f'OrdinaryCandle (high = {self.high}, low = {self.low})'


@dataclass
class MergedCandle(OrdinaryCandle):
    id: int
    period: int
    left_ordinary_id: int

    @property
    def right_ordinary_id(self) -> int:
        return self.left_ordinary_id + self.period - 1

    @property
    def ordinary_id(self) -> int:
        return self.right_ordinary_id

    def __str__(self) -> str:
        return f'MergedCandle (id = {self.id}, period = {self.period}, ' \
               f'left ordinary id = {self.left_ordinary_id}, ' \
               f'right ordinary id = {self.right_ordinary_id}, ' \
               f'high = {self.high}, low = {self.low})'


@dataclass
class Fractal:
    id: int
    pattern: FractalPattern
    left_candle: Optional[MergedCandle]
    middle_candle: MergedCandle
    right_candle: Optional[MergedCandle]
    is_confirmed: bool

    @property
    def extreme_price(self) -> float:
        if self.pattern == FractalPattern.Top:
            return self.middle_candle.high
        else:
            return self.middle_candle.low

    @property
    def merged_id(self) -> int:
        return self.middle_candle.id

    @property
    def ordinary_id(self) -> int:
        return self.middle_candle.ordinary_id

    @property
    def is_potential(self) -> Tuple[bool, Optional[Direction]]:
        if self.left_candle is None:
            return True, Direction.Left
        elif self.right_candle is None:
            return True, Direction.Right
        else:
            return False, None

    def __str__(self) -> str:
        return f'Fractal (id = {self.id}, ' \
               f'pattern = {self.pattern.value}, ' \
               f'merged id = {self.merged_id}, ' \
               f'ordinary id = {self.ordinary_id}, ' \
               f'extreme price = {self.extreme_price}, ' \
               f'confirmed = {self.is_confirmed})'


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
    def left_ordinary_id(self) -> int:
        return self.left_fractal.ordinary_id

    @property
    def right_ordinary_id(self) -> int:
        return self.right_fractal.ordinary_id

    @property
    def period(self) -> int:
        return self.right_fractal.middle_candle.id - self.left_fractal.middle_candle.id

    @property
    def period_ordinary(self) -> int:
        return self.right_ordinary_id - self.left_ordinary_id

    @property
    def price_range(self) -> float:
        return self.right_price - self.left_price

    @property
    def slope_ordinary(self) -> float:
        return self.price_range / self.period_ordinary

    def __str__(self) -> str:
        return f'Stroke (id = {self.id}, trend = {self.trend.value}, period = {self.period}, ' \
               f'left merged id = {self.left_fractal.middle_candle.id}, ' \
               f'right merged id = {self.right_fractal.middle_candle.id}, ' \
               f'left ordinary id = {self.left_ordinary_id}, ' \
               f'right ordinary id = {self.right_ordinary_id}, ' \
               f'left price = {self.left_price}, right price = {self.right_price})'


@dataclass
class Segment:
    id: int
    trend: Trend
    left_stroke: Stroke
    right_stroke: Stroke
    strokes: List[int]

    @property
    def left_fractal(self) -> Fractal:
        return self.left_stroke.left_fractal

    @property
    def right_fractal(self) -> Fractal:
        return self.right_stroke.right_fractal

    @property
    def left_price(self) -> float:
        return self.left_stroke.left_price

    @property
    def right_price(self) -> float:
        return self.right_stroke.right_price

    @property
    def left_ordinary_id(self) -> int:
        return self.left_stroke.left_ordinary_id

    @property
    def right_ordinary_id(self) -> int:
        return self.right_stroke.right_ordinary_id

    @property
    def strokes_count(self) -> int:
        return len(self.strokes)

    @property
    def period(self) -> int:
        return self.right_ordinary_id - self.left_ordinary_id

    @property
    def price_range(self) -> float:
        return self.right_price - self.left_price

    @property
    def slope(self) -> float:
        return self.price_range / self.period

    def __str__(self) -> str:
        return f'Segment (id = {self.id}, trend = {self.trend.value}, ' \
               f'left ordinary id = {self.left_ordinary_id}, ' \
               f'right ordinary id = {self.right_ordinary_id}, ' \
               f'count of strokes = {self.strokes_count}, strokes = {self.strokes})'


@dataclass
class IsolationLine:
    id: int
    candle: MergedCandle

    @property
    def merged_id(self) -> int:
        return self.candle.id

    @property
    def ordinary_id(self) -> int:
        return self.candle.ordinary_id

    def __str__(self) -> str:
        return f'IsolationLine (id = {self.id}, ' \
               f'merged candle id = {self.candle.id}, ' \
               f'ordinary id = {self.candle.right_ordinary_id})'


@dataclass
class Pivot:
    id: int
    left: Fractal
    right: Fractal
    high: float
    low: float

    @property
    def left_ordinary_id(self) -> int:
        return self.left.ordinary_id

    @property
    def right_ordinary_id(self) -> int:
        return self.right.ordinary_id

    @property
    def left_price(self) -> float:
        return self.left.extreme_price

    @property
    def right_price(self) -> float:
        return self.right.extreme_price

    @property
    def period(self) -> int:
        return self.right_ordinary_id - self.left_ordinary_id

    @property
    def price_range(self) -> float:
        return self.right_price - self.left_price

    @property
    def slope(self) -> float:
        return self.price_range / self.period

    def __str__(self) -> str:
        return f'Pivot (id = {self.id}, ' \
               f'high = {self.high}, ' \
               f'low = {self.low}, ' \
               f'left ordinary id = {self.left_ordinary_id}, ' \
               f'right ordinary idx = {self.right_ordinary_id})'


@dataclass
class Chan:
    merged_candles: List[MergedCandle]
    fractals: List[Fractal]
    strokes: List[Stroke]
    segments: List[Segment]
    isolation_lines: List[IsolationLine]
    stroke_pivots: List[Pivot]
    segment_pivots: List[Pivot]


OrdinaryCandleList = List[OrdinaryCandle]   # 普通K线序列
MergedCandleList = List[MergedCandle]       # 已合并K线序列
FractalList = List[Fractal]                 # 分型序列
StrokeList = List[Stroke]                   # 笔序列
SegmentList = List[Segment]                 # 线段序列
IsolationLineList = List[IsolationLine]
StrokePivotList = List[Pivot]
SegmentPivotList = List[Pivot]
