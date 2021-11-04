# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List, Tuple
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
    period: int
    idx_first_ordinary_candle: int

    @property
    def idx_last_ordinary_candle(self) -> int:
        return self.idx_first_ordinary_candle + self.period - 1


@dataclass
class Fractal:
    type_: FractalType
    is_confirmed: bool
    left_candle: MergedCandle
    middle_candle: MergedCandle
    right_candle: MergedCandle

    @property
    def extreme(self) -> float:
        return self.middle_candle.high if self.type_ == FractalType.Top else self.middle_candle.low

    def __str__(self) -> str:
        return f'Fractal ({self.type_.value}, ' \
               f'idx = {self.middle_candle.idx_last_ordinary_candle}, ' \
               f'range = {self.middle_candle.high} ~ {self.middle_candle.low})'


@dataclass
class FractalFirst:
    type_: FractalType
    middle: MergedCandle
    right: MergedCandle


@dataclass
class FractalLast:
    type_: FractalType
    left: MergedCandle
    middle: MergedCandle


OrdinaryCandleList = List[OrdinaryCandle]
MergedCandleList = List[MergedCandle]
FractalList = List[Fractal]
StrokeList = List[Tuple[str, str]]
