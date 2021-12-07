# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Optional

import pandas as pd

from .definition import (
    Action,
    LogLevel,
    RelationshipInNumbers,

    FractalPattern,
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
from .utility import (
    is_inclusive_candle,
    is_regular_fractal,
    is_overlap,
    generate_merged_candle,
    generate_fractal,
)
from .log_message import (
    log_event_new_turn,
    log_event_candle_generated,
    log_event_candle_updated,
    log_event_fractal_generated,
    log_event_fractal_updated,
    log_event_fractal_dropped,
    log_event_stroke_generated,
    log_event_stroke_updated,
    log_event_segment_generated,
    log_event_segment_extended,
    log_event_segment_expanded,
    log_event_isolation_line_generated,
    log_event_stroke_pivot_generated,
    log_event_stroke_pivot_extended,

    log_try_to_generate_fractal,
    log_try_to_update_fractal,

    log_failed_in_not_enough_merged_candles,

)


class ChanTheoryStatic(ChanTheory):
    """
    缠论静态版.
    """

    def __init__(self,
                 strict_mode: bool = True,
                 log_level: LogLevel = LogLevel.Normal
                 ):
        """
        Initialize the object.

        :param strict_mode:
        :param log_level:
        """
        super().__init__(strict_mode, log_level)

    def generate_merged_candles(self,
                                df: pd.DataFrame,
                                count: Optional[int] = None,
                                log_level: Optional[LogLevel] = None
                                ) -> None:
        """
        Generate merged candles.

        :param df:
        :param count:
        :param log_level:
        :return:
        """

        # Handle parameters.
        if count is None or count <= 0:
            count = len(df)
        if log_level is None:
            log_level = self._log_level

        # Declare variables type.
        ordinary_candle: OrdinaryCandle
        new_candle: MergedCandle

        old_candle_left: Optional[MergedCandle]
        old_candle_right: Optional[MergedCandle]

        # Run the loop.
        for idx in range(count):
            log_event_new_turn(log_level, idx, count)

            ordinary_candle = OrdinaryCandle(
                high=df.iloc[idx].at['high'].copy(),
                low=df.iloc[idx].at['low'].copy()
            )

            if self.merged_candles_count >= 2:
                old_candle_right = self._merged_candles[-1]
                old_candle_left = self._merged_candles[-2]
            elif self.merged_candles_count == 1:
                old_candle_right = self._merged_candles[-1]
                old_candle_left = None
            else:
                old_candle_right = None
                old_candle_left = None

            new_candle = generate_merged_candle(
                ordinary_candle=ordinary_candle,
                last_candle=(old_candle_left, old_candle_right)
            )

            if old_candle_right is None or new_candle.id != old_candle_right.id:
                log_event_candle_generated(
                    log_level=log_level,
                    new_merged_candle=new_candle
                )

                self._merged_candles.append(new_candle)
            else:
                log_event_candle_updated(
                    log_level=log_level,
                    merged_candle=new_candle
                )

    def generate_fractals(self,
                          log_level: Optional[LogLevel] = None
                          ) -> None:
        """
        Generate fractals.

        :param log_level:
        :return:
        """
        if log_level is None:
            log_level = self._log_level

        if self.merged_candles_count == 0:
            raise RuntimeError('No merged candle data, run <generate_merged_candles> before.')

        fractal_count: int
        last_fractal: Fractal
        left_candle: MergedCandle
        middle_candle: MergedCandle
        right_candle: MergedCandle
        for idx in range(self.merged_candles_count):
            log_event_new_turn(log_level, idx, self.merged_candles_count)

            # 如果分型数量 == 0，生成第1个分型。
            # 第1个分型只需要保证中间合并K线的最高价/最低价是三个合并K线的极值即可。
            if self.fractals_count == 0:

                # Log trying.
                log_try_to_generate_fractal(log_level=log_level)

                # 如果合并K线的数量少于3个，log 信息。
                if self.merged_candles_count < 3:
                    log_failed_in_not_enough_merged_candles(
                        log_level=log_level,
                        count=self.merged_candles_count,
                        required=self.minimum_distance
                    )
                    continue

                left_candle = self._merged_candles[idx - 2]
                middle_candle = self._merged_candles[idx - 1]
                right_candle = self._merged_candles[idx]


                    # left_candle,
                #     middle_candle,
                #     right_candle
                # )

                new_fractal = is_regular_fractal(left_candle, middle_candle, right_candle)

                # 是否能够形成分型。
                if new_fractal is None:
                    log_failed_in_not_enough_merged_candles(log_level)
                    continue
                else:
                    log_failed_in_not_enough_merged_candles(log_level)

                # 分型是否相同。
                # 分型的距离。
                new_fractal = generate_fractal(
                    left_candle,
                    middle_candle,
                    right_candle,
                    last_fractal=None
                )

                if new_fractal is not None:
                    self._fractals.append(new_fractal)
                    log_event_fractal_generated(
                        log_level=log_level,
                        element_id=new_fractal.id + 1,
                        pattern=new_fractal.pattern,
                        mc_id=middle_candle.id,
                        oc_id=middle_candle.ordinary_id
                    )
                else:
                    continue

            # 修正分型
            if self.fractals_count >= 2:
                last_fractal = self._fractals[-1]
                last_candle: MergedCandle = self._merged_candles[idx]

                log_try_to_update_fractal(log_level, last_fractal, last_candle)

                is_updated: bool = False

                # 如果当前合并K线顺向突破（即最高价大于顶分型中间K线的最高价，对底分型反之）。
                if last_fractal.pattern == FractalPattern.Top:
                    if last_candle.high < last_fractal.middle_candle.high:
                        if verbose:
                            print('        最新合并K线的最高价 <= 最新笔的右侧价，不满足。')
                    else:
                        if verbose:
                            print('        最新合并K线的最高价 > 最新笔的右侧价，满足。')
                        is_updated = True

                else:  # last_fractal.pattern == FractalPattern.Bottom
                    if last_candle.low > last_fractal.middle_candle.low:
                        if verbose:
                            print('        最新合并K线的最高价 >= 最新笔的右侧价，不满足。')
                    else:
                        if verbose:
                            print('        最新合并K线的最高价 < 最新笔的右侧价，满足。')
                        is_updated = True

                if is_updated:
                    log_event_fractal_updated(
                        log_level=log_level,
                        element_id=last_fractal.id + 1,
                        pattern=last_fractal.pattern,
                        extreme_price=last_fractal.extreme_price,
                        mc_id=last_candle.id,
                        oc_id=last_candle.ordinary_id
                    )

                    # 修正前分型。
                    last_fractal.left_candle = self._merged_candles[last_candle.id - 1]
                    last_fractal.middle_candle = last_candle
                    last_fractal.right_candle = None
                    last_fractal.is_confirmed = False

                    continue
