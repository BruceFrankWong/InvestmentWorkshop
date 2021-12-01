# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List, Optional, Any
from enum import Enum
from copy import deepcopy
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


class LogLevel(Enum):
    Off = 0
    Simple = 1
    Normal = 2
    Detailed = 3

    def __str__(self) -> str:
        if self.value == 0:
            return '关闭'
        elif self.value == 1:
            return '简单'
        elif self.value == 2:
            return '普通'
        else:
            return '详细'


class RelationshipInNumbers(Enum):
    Equal = '等于'
    Greater = '大于'
    Less = '小于'

    def __str__(self) -> str:
        return self.value


class FirstOrLast(Enum):
    First = '开始/左侧'
    Last = '结束/右侧'

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


class FractalPotential(Enum):
    Regular = '正规'
    Left = '左侧'
    Right = '右侧'

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
    def potential(self) -> FractalPotential:
        if self.left_candle is None:
            return FractalPotential.Left
        elif self.right_candle is None:
            return FractalPotential.Right
        else:
            return FractalPotential.Regular

    def __str__(self) -> str:
        return f'Fractal (id = {self.id}, ' \
               f'pattern = {self.pattern.value}, ' \
               f'merged id = {self.merged_id}, ' \
               f'ordinary id = {self.ordinary_id}, ' \
               f'extreme price = {self.extreme_price}, ' \
               f'potential = {self.potential.value}, ' \
               f'confirmed = {self.is_confirmed})'


@dataclass
class Stroke:
    id: int
    trend: Trend
    left_candle: MergedCandle
    right_candle: MergedCandle

    @property
    def left_merged_id(self) -> int:
        return self.left_candle.id

    @property
    def left_ordinary_id(self) -> int:
        return self.left_candle.ordinary_id

    @property
    def right_merged_id(self) -> int:
        return self.right_candle.id

    @property
    def right_ordinary_id(self) -> int:
        return self.right_candle.ordinary_id

    @property
    def left_price(self) -> float:
        if self.trend == Trend.Bullish:
            return self.left_candle.low
        else:
            return self.left_candle.high

    @property
    def right_price(self) -> float:
        if self.trend == Trend.Bullish:
            return self.right_candle.high
        else:
            return self.right_candle.low

    @property
    def period(self) -> int:
        return self.right_candle.id - self.left_candle.id

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
               f'left merged id = {self.left_ordinary_id}, ' \
               f'right merged id = {self.right_merged_id}, ' \
               f'left ordinary id = {self.left_ordinary_id}, ' \
               f'right ordinary id = {self.right_ordinary_id}, ' \
               f'left price = {self.left_price}, right price = {self.right_price})'


@dataclass
class Segment:
    id: int
    trend: Trend
    left_candle: MergedCandle
    right_candle: MergedCandle
    stroke_id_list: List[int]

    @property
    def left_merged_id(self) -> int:
        return self.left_candle.id

    @property
    def right_merged_id(self) -> int:
        return self.right_candle.id

    @property
    def left_ordinary_id(self) -> int:
        return self.left_candle.ordinary_id

    @property
    def right_ordinary_id(self) -> int:
        return self.right_candle.ordinary_id

    @property
    def strokes_count(self) -> int:
        return len(self.stroke_id_list)

    @property
    def period(self) -> int:
        return self.right_ordinary_id - self.left_ordinary_id

    @property
    def left_price(self) -> float:
        if self.trend == Trend.Bullish:
            return self.left_candle.low
        else:
            return self.left_candle.high

    @property
    def right_price(self) -> float:
        if self.trend == Trend.Bullish:
            return self.right_candle.high
        else:
            return self.right_candle.low

    @property
    def price_range(self) -> float:
        return self.right_price - self.left_price

    @property
    def slope(self) -> float:
        return self.price_range / self.period

    def __str__(self) -> str:
        return f'Segment (id = {self.id}, trend = {self.trend.value}, ' \
               f'left merged id = {self.left_merged_id}, ' \
               f'right merged id = {self.right_merged_id}, ' \
               f'left ordinary id = {self.left_ordinary_id}, ' \
               f'right ordinary id = {self.right_ordinary_id}, ' \
               f'count of strokes = {self.strokes_count}, strokes = {self.stroke_id_list})'


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
    left_candle: MergedCandle
    right_candle: MergedCandle
    high: float
    low: float

    @property
    def left_merged_id(self) -> int:
        return self.left_candle.id

    @property
    def right_merged_id(self) -> int:
        return self.right_candle.id

    @property
    def left_ordinary_id(self) -> int:
        return self.left_candle.ordinary_id

    @property
    def right_ordinary_id(self) -> int:
        return self.right_candle.ordinary_id

    @property
    def period(self) -> int:
        return self.right_ordinary_id - self.left_ordinary_id

    @property
    def price_range(self) -> float:
        return self.high - self.low

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
class PeriodUnit:
    name_zh: str
    name_en: str


class PeriodUnitEnum(Enum):
    Year = PeriodUnit(name_zh='年', name_en='Year')
    Quarter = PeriodUnit(name_zh='季', name_en='Quarter')
    Month = PeriodUnit(name_zh='月', name_en='Month')
    Week = PeriodUnit(name_zh='周', name_en='Week')
    Day = PeriodUnit(name_zh='日', name_en='Day')
    Hour = PeriodUnit(name_zh='小时', name_en='Hour')
    Minute = PeriodUnit(name_zh='分钟', name_en='Minute')
    Second = PeriodUnit(name_zh='秒', name_en='Second')

    @property
    def name_en(self) -> str:
        return self.value.name_en

    @property
    def name_zh(self) -> str:
        return self.value.name_zh


class Period:
    _value: int
    _unit: PeriodUnitEnum
    _upper: Any
    _lower: Any

    def __init__(self,
                 value: int,
                 unit: PeriodUnitEnum
                 ) -> None:
        self._value = value
        self._unit = unit
        self._lower = None
        self._upper = None

    @property
    def upper(self):
        return self._upper

    @upper.setter
    def upper(self, p):
        self._upper = p

    @property
    def lower(self):
        return self._lower

    @lower.setter
    def lower(self, p):
        self._lower = p

    @property
    def name_en(self) -> str:
        return f'{self._value}{self._unit.name_en}'

    @property
    def name_zh(self) -> str:
        return f'{self._value}{self._unit.name_zh}'


Period5S = Period(value=5, unit=PeriodUnitEnum.Second)
Period30S = Period(value=30, unit=PeriodUnitEnum.Second)
Period3M = Period(value=3, unit=PeriodUnitEnum.Minute)
Period15M = Period(value=15, unit=PeriodUnitEnum.Minute)
Period1H = Period(value=1, unit=PeriodUnitEnum.Hour)
Period1D = Period(value=1, unit=PeriodUnitEnum.Day)

Period1D.upper = None
Period1D.lower = Period1H

Period1H.upper = Period1D
Period1H.lower = Period15M

Period15M.upper = Period1H
Period15M.lower = Period3M

Period3M.upper = Period15M
Period3M.lower = Period30S

Period30S.upper = Period3M
Period30S.lower = None


class ChanTheory:

    _merged_candles: List[MergedCandle]
    _fractals: List[Fractal]
    _strokes: List[Stroke]
    _segments: List[Segment]
    _isolation_lines: List[IsolationLine]
    _stroke_pivots: List[Pivot]
    _segment_pivots: List[Pivot]

    _strict_mode: bool
    _minimum_distance: int

    _log_level: LogLevel

    def __init__(self,
                 strict_mode: bool = True,
                 log_level: LogLevel = LogLevel.Normal
                 ):
        """
        Initialize the object.

        :param strict_mode:
        """
        self._merged_candles = []
        self._fractals = []
        self._strokes = []
        self._segments = []
        self._isolation_lines = []
        self._stroke_pivots = []
        self._segment_pivots = []

        self._strict_mode = strict_mode
        self._minimum_distance = 4 if strict_mode else 3

        self._log_level = log_level

    @property
    def minimum_distance(self) -> int:
        """
        The minimum distance between two fractals. And it also is the minimum length of strokes.

        :return: int.
        """
        return self._minimum_distance

    @property
    def merged_candles_count(self) -> int:
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
    def fractals_count(self) -> int:
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
    def strokes_count(self) -> int:
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
    def segments_count(self) -> int:
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
    def isolation_lines_count(self) -> int:
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
    def stroke_pivots_count(self) -> int:
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
    def segment_pivots_count(self) -> int:
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
