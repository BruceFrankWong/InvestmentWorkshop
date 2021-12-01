# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from .definition import (
    LogLevel,

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

    ChanTheory,
)
from .procedure import (
    generate_merged_candles_with_dataframe,
    generate_fractals,
    generate_strokes,
    generate_segments,
    generate_isolation_lines,
    generate_stroke_pivots,
    generate_segment_pivots,
    run_with_dataframe,
)
from .static import ChanTheoryStatic
from .dynamic import ChanTheoryDynamic
from .plot import (
    plot_chan_theory,
    plot_pure_merged_candle
)
