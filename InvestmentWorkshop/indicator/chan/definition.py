# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List, Optional
from enum import Enum
from dataclasses import dataclass


class FractalType(Enum):
    Top = '顶分型'
    Bottom = '底分型'

    def __str__(self) -> str:
        return self.value


class TrendType(Enum):
    U = '上升'
    D = '下降'
    Up = '上升'
    Down = '下降'
    Bullish = '上升'
    Bearish = '下降'

    def __str__(self) -> str:
        return self.value


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


@dataclass
class InterimFractal:
    type_: FractalType
    middle_candle: MergedCandle

    @property
    def extreme_price(self) -> float:
        return self.middle_candle.high if self.type_ == FractalType.Top else self.middle_candle.low

    def __str__(self) -> str:
        return f'InterimFractal ({self.type_.value}, ' \
               f'ordinary idx = {self.middle_candle.last_ordinary_idx}, ' \
               f'range = {self.middle_candle.high} ~ {self.middle_candle.low})'


@dataclass
class Fractal(InterimFractal):
    idx: int
    is_confirmed: bool
    left_candle: MergedCandle
    right_candle: MergedCandle

    def __str__(self) -> str:
        return f'Fractal ({self.type_.value}, ' \
               f'ordinary idx = {self.middle_candle.last_ordinary_idx}, ' \
               f'range = {self.middle_candle.high} ~ {self.middle_candle.low})'


@dataclass
class LinearElement:
    idx: int
    type_: str
    trend: TrendType
    left_fractal: Fractal
    right_fractal: Fractal
    fractals: List[Fractal]

    @property
    def left_price(self) -> float:
        return self.left_fractal.extreme_price

    @property
    def right_price(self) -> float:
        return self.right_fractal.extreme_price

    @property
    def period(self) -> int:
        return self.right_fractal.middle_candle.last_ordinary_idx - \
               self.left_fractal.middle_candle.last_ordinary_idx

    @property
    def price_range(self) -> float:
        return self.right_fractal.extreme_price - self.left_fractal.extreme_price

    @property
    def slope(self) -> float:
        return self.price_range / self.period

    def __str__(self) -> str:
        return f'<LinearElement (type={self.type_}, id={self.idx}, trend={self.trend.value}, ' \
               f'ordinary idx = {self.left_fractal.middle_candle.last_ordinary_idx} ~ ' \
               f'{self.right_fractal.middle_candle.last_ordinary_idx})>'


class LinearElementMode(Enum):
    UDU = '上下上'
    DUD = '下上下'


OrdinaryCandleList = List[OrdinaryCandle]   # 普通K线序列
MergedCandleList = List[MergedCandle]       # 已合并K线序列
FractalList = List[Fractal]                 # 分型序列
StrokeList = List[LinearElement]            # 笔序列
SegmentList = List[LinearElement]           # 线段序列
