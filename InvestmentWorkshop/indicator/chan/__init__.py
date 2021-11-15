# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from .definition import (
    FractalPattern,
    FractalFunction,
    Trend,

    OrdinaryCandle,
    MergedCandle,
    Fractal,
    Stroke,
    Segment,
    IsolationLine,
    Pivot,

    OrdinaryCandleList,
    MergedCandleList,
    FractalList,
    StrokeList,
    SegmentList,
)
from .static import (
    generate_merged_candles,
    generate_fractals,
    generate_strokes,
    generate_segments,
    generate_isolation_lines,
    generate_stroke_pivots,
    generate_segment_pivots,
)
from .dynamic import (
    ChanTheory
)
from .plot import (
    plot_chan_theory,
    plot_pure_merged_candle
)
