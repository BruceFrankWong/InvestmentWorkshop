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
)
from .static import (
    update_merged_candles,
    update_fractals,
    generate_strokes,
    generate_segments,
    generate_isolation_lines,
    generate_stroke_pivots,
    generate_segment_pivots,
)
from .dynamic import (
    ChanTheoryDynamic
)
from .plot import (
    plot_chan_theory,
    plot_pure_merged_candle
)
