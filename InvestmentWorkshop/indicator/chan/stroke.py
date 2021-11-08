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
    StrokeList,
    InterimFractal,
)


def generate_stroke(stroke_list: StrokeList,
                    fractal_list: FractalList,
                    debug: bool = False
                    ) -> Optional[StrokeList]:
    result: StrokeList = deepcopy(stroke_list)

    # 已存在的笔的数量。
    stroke_count: int = 0 if result is None else len(result)

    return result
