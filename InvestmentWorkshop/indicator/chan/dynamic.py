# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import mplfinance as mpf

from .definition import (
    Action,
    LogLevel,

    FirstOrLast,
    FractalPattern,
    Trend,
    OrdinaryCandle,
    MergedCandle,
    Fractal,
    Stroke,
    Segment,
    Pivot,
    IsolationLine,

    ChanTheory,
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

    log_try_to_generate_stroke,
    log_show_candles,
)
from .utility import (
    is_regular_fractal,
    is_potential_fractal,
    generate_merged_candle,
)


@dataclass
class PotentialFractal:
    candle: MergedCandle
    pattern: FractalPattern

    @property
    def merged_id(self) -> int:
        return self.candle.id

    @property
    def ordinary_id(self) -> int:
        return self.candle.ordinary_id

    @property
    def extreme_price(self) -> float:
        if self.pattern == FractalPattern.Top:
            return self.candle.high
        else:
            return self.candle.low

    def __str__(self) -> str:
        return f'PotentialFractal (pattern={self.pattern.value}, ' \
               f'merged id={self.merged_id}, ' \
               f'ordinary id = {self.ordinary_id}, ' \
               f'extreme price = {self.extreme_price})'


class ChanTheoryDynamic(ChanTheory):
    """
    缠论动态版。
    """

    _potential_fractal: PotentialFractal

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

    def get_ordinary_candle_id(self, merged_candle_id: int) -> Optional[int]:
        return self._merged_candles[merged_candle_id].right_ordinary_id

    def update_merged_candle(self,
                             ordinary_candle: OrdinaryCandle,
                             log_level: Optional[LogLevel] = None
                             ) -> Action:
        """
        Update (generate or merge) merged candles for Chan Theory.

        :param ordinary_candle:
        :param log_level:
        :return: Action. If new merged candle was generated, return <Action.MergedCandleGenerated>.
                 If last merged candle was updated, return <Action.MergedCandleUpdated>.
        """

        if log_level is None:
            log_level = self._log_level

        new_candle: MergedCandle
        old_candle_left: Optional[MergedCandle]
        old_candle_right: Optional[MergedCandle]

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

            return Action.MergedCandleGenerated
        else:
            log_event_candle_updated(
                log_level=log_level,
                merged_candle=new_candle
            )

            return Action.MergedCandleUpdated

    def update_strokes(self,
                       log_level: Optional[LogLevel] = None
                       ) -> Action:
        """
        Update strokes.

        :param log_level:
        :return:
        """

        return Action.NothingChanged

    def generate_first_stroke(self,
                              log_level: Optional[LogLevel] = None
                              ) -> Action:
        """
        生成第1个笔，同时生成第1个、第2个分型。

        正式分型：需要有左中右三根K线。

        潜在分型：缺少左侧或右侧K线。

        假设右侧的合并K线是潜在分型，自前向后（自左向右），从 id=1 开始穷举合并K线，
        如果：
            1. 该 id 的合并K线 与 右侧潜在分型 的距离满足最小要求，且
            2. 该 id 的合并K线可以构成正式分型，且
            3. 该 id 的合并K线构成的正式分型 与 右侧潜在分型 的类型不同，且
            4. 该 id 的合并K线构成的正式分型 与 右侧潜在分型 之间没有极值突破两个分型极值的K线
        生成：
            1. 第1、第2两个分型，第1个分型是 confirmed，第2个不是；
            2. 第1个笔。

        :return:
        """

        if log_level is None:
            log_level = self._log_level

        if self.merged_candles_count == 0:
            raise RuntimeError(
                'No merged candle data, run <generate_merged_candles_with_dataframe> before.'
            )

        # Declare variables。
        potential_fractal_pattern: FractalPattern
        potential_fractal_candle: MergedCandle = self._merged_candles[-1]
        is_fractal: bool

        # Get the potential fractal (the last candle) pattern.
        is_fractal, potential_fractal_pattern = is_potential_fractal(
            [
                self._merged_candles[-2],
                self._merged_candles[-1]
            ],
            FirstOrLast.Last
        )

        # log trying.
        log_try_to_generate_stroke(log_level=log_level)

        log_show_candles(
            log_level=log_level,
            left_candle=
        )
        if log_level.value >= LogLevel.Detailed.value:
            print(
                f'\n  ○ 尝试生成笔：'
                f'\n    最新合并K线，'
                f'id（合并K线）= {potential_fractal_candle.id}，'
                f'id（普通K线）= {potential_fractal_candle.ordinary_id}，'
                f'分型（潜在） = {potential_fractal_pattern.value}。'
            )

        # 申明变量类型并赋值。
        left_candle: MergedCandle
        middle_candle: MergedCandle
        right_candle: MergedCandle
        left_fractal_pattern: FractalPattern

        # 开始循环。
        for i in range(1, potential_fractal_candle.id):

            # 取得 left_merged_candle。
            left_candle = self._merged_candles[i]
            if log_level.value >= LogLevel.Detailed.value:
                print(
                    f'    左合并K线，'
                    f'id（合并K线）= {left_candle.id}，'
                    f'id（普通K线）= {left_candle.ordinary_id}'
                )

            # 判定距离。
            # 如果：
            #     left_candle 与 right_candle 之间的距离不满足最小要求
            # 退出循环。
            distance: int = potential_fractal_candle.id - left_candle.id

            if distance < self.minimum_distance:
                if log_level.value >= LogLevel.Detailed.value:
                    print(f'        距离 = {distance}，< {self.minimum_distance}，不满足。')
                return Action.NothingChanged
            else:
                if log_level.value >= LogLevel.Detailed.value:
                    print(f'        距离 = {distance}，≥ {self.minimum_distance}，满足。')

            # 判定正规分型。
            left_candle = self._merged_candles[i - 1]
            middle_candle = self._merged_candles[i]
            right_candle = self._merged_candles[i + 1]
            is_fractal, left_fractal_pattern = is_regular_fractal(
                left_candle,
                middle_candle,
                right_candle,
            )

            # 如果：
            #     left_candle 不能形成分型
            # 退出循环。
            if not is_fractal:
                if log_level.value >= LogLevel.Detailed.value:
                    print('        正式分型 = 不是分型，不满足。')
                continue

            # 如果：
            #     形成的分型与 right_merged_candle 形成的潜在分型同类
            # 退出循环。
            if left_fractal_pattern == potential_fractal_pattern:
                if log_level.value >= LogLevel.Detailed.value:
                    print(f'        正式分型 = {left_fractal_pattern.value}，与右侧潜在分型相同，不满足。')
                continue
            else:
                if log_level.value >= LogLevel.Detailed.value:
                    print(f'        正式分型 = {left_fractal_pattern.value}，与右侧潜在分型不同，满足。')

            # 判定两端分型的中间K线。
            price_low: float
            price_high: float
            if potential_fractal_pattern == FractalPattern.Top:
                price_low = middle_candle.low
                price_high = potential_fractal_candle.high
            else:
                price_low = potential_fractal_candle.low
                price_high = middle_candle.high

            is_price_break_high: bool = False
            is_price_break_low: bool = False
            candle: MergedCandle
            for j in range(middle_candle.id + 1, potential_fractal_candle.id):
                candle = self.merged_candles[j]
                if candle.low < price_low:
                    is_price_break_low = True
                    if log_level.value >= LogLevel.Detailed.value:
                        print(
                            f'        第 {j} 个合并K线的最低价 = {candle.low}，'
                            f'超越了两个分型的最低价 {price_low}，不满足。'
                        )
                    continue
                if candle.high > price_high:
                    is_price_break_high = True
                    if log_level.value >= LogLevel.Detailed.value:
                        print(
                            f'        第 {j} 个合并K线的最高价 = {candle.high}，'
                            f'超越了两个分型的最低价 {price_high}，不满足。'
                        )
                    continue

            if is_price_break_high or is_price_break_low:
                continue

            if log_level.value >= LogLevel.Detailed.value:
                print(f'        两个分型之间的合并K线均没有超越分型的最高价或者最低价，满足。')

            # 创建首对分型
            new_fractal: Fractal = Fractal(
                id=self.fractals_count,
                pattern=left_fractal_pattern,
                left_candle=left_candle,
                middle_candle=middle_candle,
                right_candle=right_candle,
                is_confirmed=True
            )
            if self._log:
                print(
                    LOG_FRACTAL_GENERATED.format(
                        id=new_fractal.id + 1,
                        pattern=new_fractal.pattern,
                        mc_id=new_fractal.merged_id,
                        oc_id=new_fractal.ordinary_id
                    )
                )
            self._fractals.append(new_fractal)

            new_fractal: Fractal = Fractal(
                id=self.fractals_count,
                pattern=potential_fractal_pattern,
                left_candle=left_candle,
                middle_candle=middle_candle,
                right_candle=None,
                is_confirmed=False
            )
            if self._log:
                print(
                    LOG_FRACTAL_GENERATED.format(
                        id=new_fractal.id + 1,
                        pattern=new_fractal.pattern,
                        mc_id=new_fractal.merged_id,
                        oc_id=new_fractal.ordinary_id
                    )
                )
            self._fractals.append(new_fractal)

            new_stroke: Stroke = Stroke(
                id=self.strokes_count,
                trend=Trend.Bullish if left_fractal_pattern == FractalPattern.Bottom
                else Trend.Bearish,
                left_candle=middle_candle,
                right_candle=potential_fractal_candle
            )

            log_event_stroke_generated(
                log_level=log_level,
                new_stroke=new_stroke
            )

            self._strokes.append(new_stroke)

            return Action.StrokeGenerated

        return Action.NothingChanged

    def extend_stroke(self) -> Action:
        """
        延伸笔，同时修正分型。

        如果：
            A1. 最新笔是上升笔：
            A2. 最新合并K线的 最高价 >= 最新笔的 右侧价 （顺向超越或达到）：
          或
            B1. 最新笔是下降笔：
            B2. 最新合并K线的 最低价 <= 最新笔的 右侧价 （顺向超越或达到）：
        修正最新分型为潜在，向右侧移动，并且延伸笔。
        否则，修正分型为正式分型。
        :return:
        """

        # 申明变量类型并赋值。
        last_stroke: Stroke = self._strokes[-1]
        last_fractal: Fractal = self._fractals[-1]
        last_candle: MergedCandle = self._merged_candles[-1]

        if log_level.value >= LogLevel.Detailed.value:
            print(
                f'\n  ○ 尝试延伸笔：'
                f'\n    最新笔 id = {last_stroke.id}，趋势 = {last_stroke.trend.value}，'
                f'右侧合并K线 id = {last_stroke.right_candle.id}，右侧价 = {last_stroke.right_price}'
                f'\n    最新合并K线 id = {last_candle.id}，'
                f'最高价 = {last_candle.high}，最低价 = {last_candle.low}'
            )

        if last_stroke.trend == Trend.Bullish:
            if last_candle.high < last_stroke.right_price:
                if log_level.value >= LogLevel.Detailed.value:
                    print('        最新合并K线的最高价 <= 最新笔的右侧价，不满足。')
                if last_fractal.right_candle is None:
                    last_fractal.right_candle = last_candle
                    if log_level.value >= LogLevel.Detailed.value:
                        print('    最新分型的右侧合并K线已填补，最新分型由潜在分型修正为正是分型。')
                return Action.NothingChanged
            else:
                if log_level.value >= LogLevel.Detailed.value:
                    print('        最新合并K线的最高价 > 最新笔的右侧价，满足。')

        else:   # last_stroke.trend == Trend.Bearish
            if last_candle.low > last_stroke.right_price:
                if log_level.value >= LogLevel.Detailed.value:
                    print('        最新合并K线的最高价 >= 最新笔的右侧价，不满足。')
                if last_fractal.right_candle is None:
                    last_fractal.right_candle = last_candle
                    if log_level.value >= LogLevel.Detailed.value:
                        print('    最新分型的右侧合并K线已填补，最新分型由潜在分型修正为正是分型。')
                return Action.NothingChanged
            else:
                if log_level.value >= LogLevel.Detailed.value:
                    print('        最新合并K线的最高价 < 最新笔的右侧价，满足。')

        # 修正分型。
        last_fractal: Fractal = self._fractals[-1]
        last_fractal.left_candle = last_fractal.middle_candle
        last_fractal.middle_candle = last_candle
        if self._log:
            print(
                LOG_FRACTAL_UPDATED.format(
                    id=last_fractal.id + 1,
                    pattern=last_fractal.pattern,
                    extreme_price=last_fractal.extreme_price,
                    mc_id=last_candle.id,
                    oc_id=last_candle.ordinary_id
                )
            )

        # 延伸笔。
        if self._log:
            print(
                LOG_STROKE_EXTENDED.format(
                    id=last_stroke.id + 1,
                    trend=last_stroke.trend,
                    old_mc_id=last_stroke.right_candle.id,
                    new_mc_id=last_candle.id,
                    old_oc_id=last_stroke.right_candle.ordinary_id,
                    new_oc_id=last_candle.ordinary_id
                )
            )
        last_stroke.right_candle = last_candle

        return Action.StrokeExtended

    def generate_following_stroke(self) -> Action:
        """
        生成后续的笔以及分型。

        如果：
            1. 最新合并K线 与 最新笔的右K线 之间的距离满足要求
          且
            A1. 最新合并K线构成的潜在分型 与 最新笔的右侧分型 不同，且
            A2. last_merged_candle 的最高价 < last_stroke 的 右侧价，且？
          或
            B1. last_stroke 的 trend 是 下降，且
            B2. last_merged_candle 是 潜在顶分型，且
            B3. fractal_p1 的3根 merged candle 的最低价 > last_stroke 的 右侧价，且？
        生成（反向）笔，及一个新的分型。
        :return:
        """

        last_candle: MergedCandle = self._merged_candles[-1]
        last_stroke: Stroke = self._strokes[-1]

        if log_level.value >= LogLevel.Detailed.value:
            print(
                f'\n  ○ 尝试生成后续笔：'
                f'\n    最新笔 id = {last_stroke.id}，趋势 = {last_stroke.trend}，'
                f'右侧 id（合并K线）= {last_stroke.right_merged_id}，右侧价 = {last_stroke.right_price}'
                f'\n    最新合并K线 id = {last_candle.id}，'
                f'最高价 = {last_candle.high}，最低价 = {last_candle.low}'
            )

        # 判定距离。
        distance = last_candle.id - last_stroke.right_candle.id
        if distance < self._minimum_distance:
            if log_level.value >= LogLevel.Detailed.value:
                print(f'        距离 = {distance}，< {self._minimum_distance}，不满足。')
            return Action.NothingChanged
        else:
            if log_level.value >= LogLevel.Detailed.value:
                print(f'        距离 = {distance}，≥ {self._minimum_distance}，满足。')

        # 判定潜在分型。
        left_fractal_pattern: FractalPattern
        if last_stroke.trend == Trend.Bullish:
            left_fractal_pattern = FractalPattern.Top
        else:
            left_fractal_pattern = FractalPattern.Bottom

        right_fractal_pattern: FractalPattern
        _, right_fractal_pattern = is_potential_fractal(
            [self._merged_candles[-2], last_candle],
            FirstOrLast.Last
        )
        if right_fractal_pattern == left_fractal_pattern:
            if log_level.value >= LogLevel.Detailed.value:
                print(
                    f'        潜在分型 = {right_fractal_pattern.value}，与最新笔的右侧分型相同，不满足。'
                )
            return Action.NothingChanged
        else:
            if log_level.value >= LogLevel.Detailed.value:
                print(
                    f'        潜在分型 = {right_fractal_pattern.value}，与最新笔的右侧分型不同，满足。'
                )

        # 判定两端分型的中间K线。
        price_low: float
        price_high: float
        if last_stroke.trend == Trend.Bullish:
            price_low = last_candle.low
            price_high = last_stroke.right_price
        else:
            price_low = last_stroke.right_price
            price_high = last_candle.high

        candle: MergedCandle
        for j in range(last_stroke.right_merged_id + 1, last_candle.id):
            candle = self.merged_candles[j]
            if candle.low < price_low:
                if log_level.value >= LogLevel.Detailed.value:
                    print(
                        f'        第 {j} 个合并K线的最低价 = {candle.low}，'
                        f'超越了两个分型的最低价 {price_low}，不满足。'
                    )
                return Action.NothingChanged
            if candle.high > price_high:
                if log_level.value >= LogLevel.Detailed.value:
                    print(
                        f'        第 {j} 个合并K线的最高价 = {candle.high}，'
                        f'超越了两个分型的最低价 {price_high}，不满足。'
                    )
                return Action.NothingChanged
        if log_level.value >= LogLevel.Detailed.value:
            print(
                f'        中间合并K线的最高价或者最低价没有超越两个分型的极值，满足。'
            )

        # 确认旧的分型。
        self._fractals[-1].is_confirmed = True

        # 生成新的分型。
        new_fractal: Fractal = Fractal(
            id=self.fractals_count,
            pattern=right_fractal_pattern,
            left_candle=self._merged_candles[-2],
            middle_candle=last_candle,
            right_candle=None,
            is_confirmed=False
        )
        if self._log:
            print(
                LOG_FRACTAL_GENERATED.format(
                    id=new_fractal.id + 1,
                    pattern=new_fractal.pattern,
                    mc_id=new_fractal.merged_id,
                    oc_id=new_fractal.ordinary_id
                )
            )
        self._fractals.append(new_fractal)

        # 生成新的笔。
        new_stroke: Stroke = Stroke(
            id=self.strokes_count,
            trend=Trend.Bullish if last_stroke.trend == Trend.Bearish
            else Trend.Bearish,
            left_candle=last_stroke.right_candle,
            right_candle=last_candle,
        )
        if self._log:
            print(
                LOG_STROKE_GENERATED.format(
                    id=new_stroke.id + 1,
                    trend=new_stroke.trend,
                    left_mc_id=new_stroke.left_candle.id,
                    right_mc_id=new_stroke.right_candle.id,
                    left_oc_id=new_stroke.left_candle.ordinary_id,
                    right_oc_id=new_stroke.right_candle.ordinary_id
                )
            )
        self._strokes.append(new_stroke)

        return Action.StrokeGenerated

    def generate_first_segment(self) -> Action:
        """
        Generate the first segments.
        :return: None.
        """
        # 如果 笔数量 < 3： 退出。
        if self.strokes_count < 3:
            if log_level.value >= LogLevel.Detailed.value:
                print(
                    f'\n  ○ 尝试生成线段：目前共有 {self.strokes_count} 根笔，最少需要 3 根。'
                )
            return Action.NothingChanged

        # 申明变量类型并赋值。
        right_stroke: Stroke = self._strokes[-1]    # 右侧笔
        middle_stroke: Stroke = self._strokes[-2]   # 中间笔
        left_stroke: Stroke = self._strokes[-3]     # 左侧笔
        overlap_high: float     # 重叠区间高值
        overlap_low: float      # 重叠区间低值

        if log_level.value >= LogLevel.Detailed.value:
            print(
                f'\n  ○ 尝试生成首根线段：目前共有 {self.strokes_count} 根笔。\n'
                f'    右侧笔，id = {right_stroke.id}，{right_stroke.trend.value}，'
                f'high = {max(right_stroke.left_price, right_stroke.right_price)}，'
                f'low = {min(right_stroke.left_price, right_stroke.right_price)}。\n'
                f'    左侧笔，id = {left_stroke.id}，{left_stroke.trend.value}，'
                f'high = {max(left_stroke.left_price, left_stroke.right_price)}，'
                f'low = {min(left_stroke.left_price, left_stroke.right_price)}。'
            )

        # 如果：
        #     1. 右侧笔是上升笔，右侧笔的左侧价 < 左侧笔的左侧价，右侧笔的右侧价 < 左侧笔的左侧价
        #   或者
        #     2. 右侧笔是下降笔，右侧笔的左侧价 > 左侧笔的左侧价，右侧笔的右侧价 > 左侧笔的左侧价
        # 无重叠。

        if (
                right_stroke.trend == Trend.Bullish and
                right_stroke.left_price < left_stroke.left_price and
                right_stroke.right_price < left_stroke.left_price
        ) or (
                right_stroke.trend == Trend.Bearish and
                right_stroke.left_price > left_stroke.left_price and
                right_stroke.right_price > left_stroke.left_price
        ):
            if log_level.value >= LogLevel.Detailed.value:
                print(
                    f'        右侧笔的两个端点'
                    f'（{right_stroke.left_price}, {right_stroke.right_price}）'
                    f'均在左侧笔的左端点（{left_stroke.left_price}）一侧，无重叠。'
                )
            return Action.NothingChanged

        # 如果：
        #     1. 右侧笔是上升笔，且
        #     2A. 右侧笔的左侧价 < 左侧笔的左侧价，右侧笔的右侧价 >= 左侧笔的左侧价
        #       有重叠：
        #       高点 = min(右侧笔的右侧价, 左侧笔的右侧价)，低点 = 左侧笔的左侧价
        #
        # A3. 右侧笔是上升笔，右侧笔的左侧价 >= 左侧笔的左侧价，右侧笔的右侧价 > 左侧笔的右侧价
        #       有重叠：
        #       高点 = min(右侧笔的右侧价, 左侧笔的左侧价)，低点 = 右侧笔的左侧价

        if right_stroke.trend == Trend.Bullish:
            if right_stroke.left_price < left_stroke.left_price <= right_stroke.right_price:
                overlap_high = min(right_stroke.right_price, left_stroke.right_price)
                overlap_low = left_stroke.left_price
            elif right_stroke.left_price >= left_stroke.left_price:
                overlap_high = min(right_stroke.right_price, left_stroke.right_price)
                overlap_low = right_stroke.left_price
            else:
                raise RuntimeError('Unknown parameters in generating first segment (Bullish).')

        # B2. 右侧笔是下降笔，右侧笔的左侧价 > 左侧笔的左侧价，右侧笔的右侧价 <= 左侧笔的右侧价
        #       有重叠：
        #       高点 = 左侧笔的左侧价，低点 = max(右侧笔的右侧价, 左侧笔的右侧价)
        #
        # B3. 右侧笔是下降笔，右侧笔的左侧价 <= 左侧笔的左侧价，右侧笔的右侧价 < 左侧笔的右侧价
        #       有重叠：
        #       高点 = 右侧笔的左侧价，低点 = max(右侧笔的右侧价, 左侧笔的左侧价)
        else:
            if right_stroke.left_price > right_stroke.left_price and \
                    right_stroke.right_price <= left_stroke.right_price:
                overlap_high = left_stroke.left_price
                overlap_low = max(right_stroke.right_price, left_stroke.right_price)
            elif right_stroke.left_price <= right_stroke.left_price:
                overlap_high = right_stroke.left_price
                overlap_low = max(right_stroke.right_price, left_stroke.left_price)
            else:
                raise RuntimeError('Unknown parameters in generating first segment (Bearish).')

        if log_level.value >= LogLevel.Detailed.value:
            print(
                f'        重叠区间 high = {overlap_high}，low = {overlap_low}，满足。'
            )

        new_segment: Segment = Segment(
            id=self.segments_count,
            trend=Trend.Bullish if right_stroke.trend == Trend.Bullish else Trend.Bearish,
            left_candle=left_stroke.left_candle,
            right_candle=right_stroke.right_candle,
            stroke_id_list=[left_stroke.id, middle_stroke.id, right_stroke.id]
        )
        self._segments.append(new_segment)

        if self._log:
            print(
                LOG_SEGMENT_GENERATED.format(
                    id=new_segment.id + 1,
                    trend=new_segment.trend,
                    left_mc_id=new_segment.left_merged_id,
                    right_mc_id=new_segment.right_merged_id,
                    left_oc_id=new_segment.left_ordinary_id,
                    right_oc_id=new_segment.right_ordinary_id,
                    strokes=new_segment.stroke_id_list
                )
            )

        return Action.SegmentGenerated

    def extend_segment(self) -> Action:
        """
        Extend an existed segment.

        Extending means do NOT add any stroke into a segment. In another word, it happens only
        when self._strokes[-1].id == self._segments[-1].strokes_id[-1].
        Updating segment with adding strokes into a segment is named as Expanding.

        :return:
        """
        verbose_message: Dict[str, str] = {
            'extend_segment':
                '\n  ○ 尝试延伸线段：最新线段 id = {segment_id}。'
                '\n    线段右侧笔 id = {segment_stroke_id}，{segment_stroke_trend}，'
                '右侧合并K线 id = {segment_right_candle_id}，右侧价 = {segment_right_price}。'
                '\n    最新    笔 id = {stroke_id}，{stroke_trend}，'
                '右侧合并K线 id = {stroke_right_candle_id}，右侧价 = {stroke_right_price}。',
            'not_same_stroke':
                '        笔 id（stroke_id） > 线段的右侧笔 id（segment_stroke_id），不满足。',
            'pass':
                '        笔 id 相同，趋势相同，笔右侧价 达到或超越 线段右侧价，满足。',
        }

        # 申明变量类型并赋值。
        last_segment: Segment = self._segments[-1]
        last_stroke: Stroke = self._strokes[-1]

        # 如果：
        #     A1. last_segment 的 trend 是 上升，且
        #     A3. last_stroke 的最高价 >= last_segment 的右侧价 （顺向超越或达到）：
        #   或
        #     B1. last_segment 的 trend 是 下降，且
        #     B3. last_stroke 的最低价 <= last_segment 的右侧价 （顺向超越或达到）：
        # 延伸（调整）笔。

        if log_level.value >= LogLevel.Detailed.value:
            print(
                verbose_message['extend_segment'].format(
                    segment_id=last_segment.id,
                    segment_stroke_id=last_segment.stroke_id_list[-1],
                    segment_stroke_trend=last_segment.trend.value,
                    segment_right_candle_id=last_segment.right_candle.id,
                    segment_right_price=last_segment.right_price,
                    stroke_id=last_stroke.id,
                    stroke_trend=last_stroke.trend.value,
                    stroke_right_candle_id=last_stroke.right_candle.id,
                    stroke_right_price=last_stroke.right_price
                )
            )

        if last_stroke.id > last_segment.stroke_id_list[-1]:
            if log_level.value >= LogLevel.Detailed.value:
                print(
                    verbose_message['not_same_stroke'].format(
                        stroke_id=last_stroke.id,
                        segment_stroke_id=last_segment.stroke_id_list[-1]
                    )
                )
            return Action.NothingChanged

        if (
                last_segment.trend == Trend.Bullish and
                last_stroke.trend == Trend.Bullish and
                last_stroke.right_price >= last_segment.right_price
        ) or (
                last_segment.trend == Trend.Bearish and
                last_stroke.trend == Trend.Bearish and
                last_stroke.right_price <= last_segment.right_price
        ):
            if log_level.value >= LogLevel.Detailed.value:
                print(verbose_message['pass'])

            if self._log:
                print(
                    LOG_SEGMENT_EXTENDED.format(
                        id=last_segment.id + 1,
                        trend=last_segment.trend,
                        old_mc_id=last_segment.right_candle.id,
                        new_mc_id=last_stroke.right_candle.id,
                        old_oc_id=last_segment.right_ordinary_id,
                        new_oc_id=last_stroke.right_ordinary_id
                    )
                )

            last_segment.right_candle = last_stroke.right_candle

            return Action.SegmentExtended

        return Action.NothingChanged

    def expand_segment(self) -> Action:
        """
        Expand an existed segment.

        Expanding means DO add strokes into a segment. In another word, it happens only
        when self._strokes[-1].id > self._segments[-1].strokes_id[-1].
        Updating segment without adding strokes into a segment is named as Extending.

        :return:
        """

        verbose_message: Dict[str, str] = {
            'expand_segment':
                '\n  ○ 尝试扩张线段：最新线段 id = {segment_id}。'
                '\n    线段右侧笔 id = {segment_stroke_id}，{segment_stroke_trend}，'
                '右侧合并K线 id = {segment_right_candle_id}，右侧价 = {segment_right_price}。'
                '\n    最新    笔 id = {stroke_id}，{stroke_trend}，'
                '右侧合并K线 id = {stroke_right_candle_id}，右侧价 = {stroke_right_price}。',
            'not_same_trend':
                '        最新笔的趋势 与 线段右侧笔的趋势 不同，不满足。',
            'same_trend':
                '        最新笔的趋势 与 线段右侧笔的趋势 相同，满足。',
            'not_achieve_or_beyond':
                '        最新笔的右侧价 没有达到或超越 线段的右侧价，不满足。',
            'achieve_or_beyond':
                '        最新笔的右侧价 达到或超越 线段的右侧价，满足。',
        }

        # 申明变量类型并赋值。
        last_segment: Segment = self._segments[-1]
        right_stroke_in_last_segment: Stroke = self._strokes[last_segment.stroke_id_list[-1]]
        last_stroke: Stroke = self._strokes[-1]

        # 如果：
        #     A1. last_segment 的 trend 是 上升，且
        #     A3. last_stroke 的最高价 >= last_segment 的右侧价 （顺向超越或达到）：
        #   或
        #     B1. last_segment 的 trend 是 下降，且
        #     B3. last_stroke 的最低价 <= last_segment 的右侧价 （顺向超越或达到）：
        # 延伸（调整）线段。

        if log_level.value >= LogLevel.Detailed.value:
            print(
                verbose_message['expand_segment'].format(
                    segment_id=last_segment.id,
                    segment_stroke_id=last_segment.stroke_id_list[-1],
                    segment_stroke_trend=last_segment.trend.value,
                    segment_right_candle_id=last_segment.right_candle.id,
                    segment_right_price=last_segment.right_price,
                    stroke_id=last_stroke.id,
                    stroke_trend=last_stroke.trend.value,
                    stroke_right_candle_id=last_stroke.right_candle.id,
                    stroke_right_price=last_stroke.right_price
                )
            )

        if last_stroke.trend != right_stroke_in_last_segment.trend:
            if log_level.value >= LogLevel.Detailed.value:
                print(verbose_message['not_same_trend'])
            return Action.NothingChanged
        else:
            if log_level.value >= LogLevel.Detailed.value:
                print(verbose_message['same_trend'])

        if (
                last_stroke.trend == Trend.Bullish and
                last_stroke.right_price >= right_stroke_in_last_segment.right_price
        ) or (
                last_stroke.trend == Trend.Bearish and
                last_stroke.right_price <= right_stroke_in_last_segment.right_price
        ):

            if log_level.value >= LogLevel.Detailed.value:
                print(verbose_message['achieve_or_beyond'])

            if self._log:
                print(
                    LOG_SEGMENT_EXPANDED.format(
                        id=last_segment.id + 1,
                        trend=last_segment.trend,
                        old_mc_id=last_segment.right_candle.id,
                        new_mc_id=last_stroke.right_candle.id,
                        old_oc_id=last_segment.right_ordinary_id,
                        new_oc_id=last_stroke.right_ordinary_id,
                        new_strokes=[
                            i for i in range(
                                last_segment.stroke_id_list[-1] + 1,
                                last_stroke.id + 1
                            )
                        ]
                    )
                )

            for i in range(last_segment.stroke_id_list[-1] + 1, last_stroke.id + 1):
                last_segment.stroke_id_list.append(i)
            last_segment.right_candle = last_stroke.right_candle

            return Action.SegmentExpanded

        if log_level.value >= LogLevel.Detailed.value:
            print(verbose_message['not_achieve_or_beyond'])
        return Action.NothingChanged

    def generate_following_segment(self) -> Action:
        """
        Generate the following segment reversely.
        :return:
        """
        last_segment: Segment = self._segments[-1]
        last_stroke_in_segment: Stroke = self._strokes[last_segment.stroke_id_list[-1]]

        left_stroke: Stroke = self._strokes[-3]
        middle_stroke: Stroke = self._strokes[-2]
        right_stroke: Stroke = self._strokes[-1]

        if log_level.value >= LogLevel.Detailed.value:
            print(
                f'\n  ○ 尝试生成反向线段：'
                f'目前共有线段 {self.segments_count} 根，笔 {self.strokes_count} 根。\n'
                f'    最新线段的右侧笔 id = {last_stroke_in_segment.id}，'
                f'trend = {last_stroke_in_segment.trend}，'
                f'price left = {last_segment.left_price}，'
                f'price right = {last_segment.right_price}\n'
                f'    最新3根笔的左侧笔 id = {left_stroke.id}，'
                f'trend = {left_stroke.trend}，'
                f'price left = {left_stroke.left_price}，'
                f'price right = {left_stroke.right_price}\n'
                f'    最新3根笔的右侧笔 id = {right_stroke.id}，'
                f'trend = {right_stroke.trend}，'
                f'price left = {right_stroke.left_price}，'
                f'price right = {right_stroke.right_price}'
            )

        # 如果：
        #     A1. 上升线段，且
        #     A2. 右侧笔的左侧价 < 左侧笔的左侧价，且
        #         （不新高）
        #     A3.
        #         A. 右侧笔的右侧价 <= 左侧笔的右侧价   （= 可以吗？）
        #           （创左侧笔的新低）
        #       或
        #         B. 左侧笔的右侧价 < 线段内右侧笔的左侧价
        #           （创线段内右侧笔的新低）
        #   或
        #     B1. 下降线段，且
        #     B2. 右侧笔的左侧价 > 左侧笔的左侧价，且
        #         （不新低）
        #     B3.
        #         A. 右侧笔的右侧价 >= 左侧笔的右侧价
        #           （创左侧笔的新高）
        #       或
        #         B. 左侧笔的右侧价 > 线段内右侧笔的左侧价
        #            （创线段内右侧笔的新高）
        # 生成反向线段。
        if (
                last_segment.trend == Trend.Bullish and
                right_stroke.trend == Trend.Bearish and
                right_stroke.left_price < left_stroke.left_price and
                (
                        right_stroke.right_price <= left_stroke.right_price
                        or
                        left_stroke.right_price < last_stroke_in_segment.left_price
                )
        ) or (
                last_segment.trend == Trend.Bearish and
                right_stroke.trend == Trend.Bullish and
                right_stroke.left_price > left_stroke.left_price and
                (
                        right_stroke.right_price >= left_stroke.right_price
                        or
                        left_stroke.right_price > last_stroke_in_segment.left_price
                )
        ):
            new_segment = Segment(
                id=self.segments_count,
                trend=Trend.Bullish
                if right_stroke.trend == Trend.Bullish else Trend.Bearish,
                left_candle=left_stroke.left_candle,
                right_candle=right_stroke.right_candle,
                stroke_id_list=[left_stroke.id, middle_stroke.id, right_stroke.id]
            )
            self._segments.append(new_segment)

            if self._log:
                print(
                    LOG_SEGMENT_GENERATED.format(
                        id=new_segment.id + 1,
                        trend=new_segment.trend,
                        left_mc_id=new_segment.left_merged_id,
                        right_mc_id=new_segment.right_merged_id,
                        left_oc_id=new_segment.left_ordinary_id,
                        right_oc_id=new_segment.right_ordinary_id,
                        strokes=new_segment.stroke_id_list
                    )
                )
            # last_segment.right_stroke = self._strokes[stroke_n1.id - 1]

            return Action.StrokeGenerated
        return Action.NothingChanged

    def generate_gap_segment(self) -> Action:
        last_segment: Segment = self._segments[-1]
        last_stroke_in_segment: Stroke = self._strokes[last_segment.stroke_id_list[-1]]

        stroke_right: Stroke = self._strokes[-1]
        stroke_left: Stroke = self._strokes[-3]

        delta: int = stroke_right.id - last_segment.stroke_id_list[-1]
        if delta % 2 == 0:
            action = self.expand_segment()
            if action == Action.SegmentExpanded:
                return Action.SegmentExpanded

        if log_level.value >= LogLevel.Detailed.value:
            print(
                f'\n  ○ 尝试生成跳空线段：'
                f'目前共有线段 {self.segments_count} 根，笔 {self.strokes_count} 根。\n'
                f'    最新线段的最新笔 id = {last_stroke_in_segment.id}，'
                f'trend = {last_stroke_in_segment.trend}，'
                f'price left = {last_segment.left_price}，'
                f'price right = {last_segment.right_price}\n'
                f'    向向左第1笔 id = {stroke_right.id}，'
                f'trend = {stroke_right.trend}，'
                f'price left = {stroke_right.left_price}，'
                f'price right = {stroke_right.right_price}\n'
                f'    向向左第3笔 id = {stroke_left.id}，'
                f'trend = {stroke_left.trend}，'
                f'price left = {stroke_left.left_price}，'
                f'price right = {stroke_left.right_price}'
            )

        # 如果：
        #     A1. stroke_right 是 上升笔，且
        #     A2. stroke_right 的 左侧价 >= stroke_left 的 左侧价，且
        #     A3. stroke_right 的 右侧价 > stroke_left 的 右侧价
        #   或
        #     B1. stroke_right 是 下降笔，且
        #     B2. stroke_right 的 左侧价 <= stroke_left 的 左侧价，且
        #     B3. stroke_right 的 右侧价 < stroke_left 的 右侧价
        # 生成跳空线段。
        if (
                stroke_right.trend == Trend.Bullish and
                stroke_right.left_price >= stroke_left.left_price and
                stroke_right.right_price > stroke_left.right_price
        ) or (
                stroke_right.trend == Trend.Bearish and
                stroke_right.left_price <= stroke_left.left_price and
                stroke_right.right_price < stroke_left.right_price
        ):
            new_segment: Segment

            # 如果 stroke_right 与 last_segment 同向：
            if stroke_right.trend == last_segment.trend:
                # 如果 stroke_left 的 id 与 last_segment 的右侧笔的 id 相差 2：
                # 延伸 last_segment
                if stroke_left.id - last_stroke_in_segment.id == 2:
                    if self._log:
                        print(
                            LOG_SEGMENT_EXPANDED.format(
                                id=last_segment.id + 1,
                                trend=last_segment.trend,
                                old_mc_id=last_segment.right_merged_id,
                                new_mc_id=stroke_right.right_candle.id,
                                old_oc_id=last_segment.right_ordinary_id,
                                new_oc_id=stroke_right.right_ordinary_id,
                                old_strokes=last_segment.stroke_id_list,
                                new_strokes=[
                                    i for i in range(
                                        last_segment.stroke_id_list[-1] + 1,
                                        stroke_right.id + 1
                                    )
                                ]
                            )
                        )
                    for i in range(last_segment.stroke_id_list[-1] + 1, stroke_right.id + 1):
                        last_segment.stroke_id_list.append(i)
                    last_segment.right_stroke = stroke_right

                    return Action.SegmentGenerated

                # 其他情况（ stroke_left 的 id 与 last_segment 的右侧笔的 id 相差 4 以上）：
                # 补一根反向线段，起点是 last_segment 的右端点，终点是 stroke_left 的左端点。
                else:
                    new_segment = Segment(
                        id=self.segments_count,
                        trend=Trend.Bearish
                        if stroke_right.trend == Trend.Bullish else Trend.Bullish,
                        left_candle=last_segment.right_candle,
                        right_candle=stroke_left.left_candle,
                        stroke_id_list=[
                            i for i in range(last_stroke_in_segment.id + 1, stroke_left.id)
                        ]
                    )
                    self._segments.append(new_segment)

                    if self._log:
                        print(
                            LOG_SEGMENT_GENERATED.format(
                                id=new_segment.id + 1,
                                trend=new_segment.trend,
                                left_mc_id=new_segment.left_merged_id,
                                right_mc_id=new_segment.right_merged_id,
                                left_oc_id=new_segment.left_ordinary_id,
                                right_oc_id=new_segment.right_ordinary_id,
                                strokes=new_segment.stroke_id_list
                            )
                        )
                    return Action.SegmentGenerated
            # 如果 stroke_right 与 last_segment 反向：
            else:
                new_segment = Segment(
                    id=self.segments_count,
                    trend=Trend.Bullish
                    if stroke_right.trend == Trend.Bullish else Trend.Bearish,
                    left_candle=last_segment.right_candle,
                    right_candle=stroke_right.right_candle,
                    stroke_id_list=[
                        i for i in range(last_stroke_in_segment.id + 1, stroke_right.id + 1)
                    ]
                )
                self._segments.append(new_segment)

                if self._log:
                    print(
                        LOG_SEGMENT_GENERATED.format(
                            id=new_segment.id + 1,
                            trend=new_segment.trend,
                            left_mc_id=new_segment.left_merged_id,
                            right_mc_id=new_segment.right_merged_id,
                            left_oc_id=new_segment.left_ordinary_id,
                            right_oc_id=new_segment.right_ordinary_id,
                            strokes=new_segment.stroke_id_list
                        )
                    )

                return Action.SegmentGenerated

        return Action.NothingChanged

    def generate_segment(self) -> bool:
        """
        Generate the segments.

        :return: bool, if new segment was generated or last segment was changed, return True.
                 Otherwise False.
        """

        # 如果 线段的数量 == 0：
        #     向前穷举 stroke_p3，如果：
        #         stroke_p3 和 stroke_p1 有重叠：
        #   生成线段。
        if self.segments_count == 0:

            self.generate_first_segment()

        # 如果 线段数量 >= 1：
        else:
            last_segment: Segment = self._segments[-1]
            last_stroke_in_segment: Stroke = self._strokes[last_segment.stroke_id_list[-1]]
            last_stroke: Stroke = self._strokes[-1]

            if last_stroke.id - last_stroke_in_segment.id < 2:
                pass

            # 在 最新笔的 id - 最新线段的右侧笔的 id == 2 时：
            elif last_stroke.id - last_segment.stroke_id_list[-1] == 2:

                self.extend_segment()

            # 在 最新笔的 id - 最新线段的右侧笔的 id == 3 时：
            elif last_stroke.id - last_stroke_in_segment.id == 3:
                self.generate_following_segment()

            # 在 最新笔的 id - 最新线段的右侧笔的 id > 3 时：
            #     既不能顺向突破（id差 == 2）
            #     又不能反向突破（id差 == 3）
            # 跳空。
            else:
                self.generate_gap_segment()

        return False

    def generate_isolation_line(self):
        last_segment: Segment = self._segments[-1]
        new_isolation_line: IsolationLine = IsolationLine(
            id=self.isolation_lines_count,
            candle=last_segment.left_candle
        )
        self._isolation_lines.append(new_isolation_line)
        if self._log:
            print(
                LOG_ISOLATION_LINE_GENERATED.format(
                    id=new_isolation_line.id + 1,
                    mc_id=new_isolation_line.candle,
                    oc_id=new_isolation_line.ordinary_id
                )
            )

    def generate_stroke_pivot(self) -> bool:
        """
        Generate the pivots.
        :return:
        """
        if self.segments_count == 0:
            if log_level.value >= LogLevel.Detailed.value:
                print(f'\n  ○ 尝试生成笔中枢：目前尚无线段。')
            return False

        last_segment: Segment = self._segments[-1]
        if last_segment.strokes_count <= 3:
            if log_level.value >= LogLevel.Detailed.value:
                print(f'\n  ○ 尝试生成笔中枢：当前线段仅包含3根笔。')
            return False

        stroke_2_id: int = last_segment.stroke_id_list[1]
        stroke_2: Stroke = self._strokes[stroke_2_id]
        stroke_3_id: int = last_segment.stroke_id_list[2]
        stroke_3: Stroke = self._strokes[stroke_3_id]
        stroke_4_id: int = last_segment.stroke_id_list[3]
        stroke_4: Stroke = self._strokes[stroke_4_id]
        
        if log_level.value >= LogLevel.Detailed.value:
            print(
                f'\n  ○ 尝试生成笔中枢：当前线段包含 {last_segment.strokes_count} 根笔。'
                f'\n    最新线段的第2笔 id = {stroke_2_id}，trend = {stroke_2.trend.value}，'
                f'left price = {stroke_2.left_price}，right price = {stroke_2.right_price}'
                f'\n    最新线段的第3笔 id = {stroke_3_id}，trend = {stroke_3.trend.value}，'
                f'left price = {stroke_3.left_price}，right price = {stroke_3.right_price}'
                f'\n    最新线段的第4笔 id = {stroke_4_id}，trend = {stroke_4.trend.value}，'
                f'left price = {stroke_4.left_price}，right price = {stroke_4.right_price}'
            )

        overlap_high: float    # 重叠区间高值
        overlap_low: float     # 重叠区间低值

        # 如果 stroke_2 是上升笔，且，stroke_4 是上升笔：
        if stroke_2.trend == Trend.Bullish and stroke_4.trend == Trend.Bullish:

            # 如果 stroke_4 的右侧价 < stroke_2 的左侧价：
            if stroke_4.left_price < stroke_2.left_price:
                # 如果
                #     1. stroke_4 的右侧价 < stroke_2 的左侧价
                # 没有重叠
                if stroke_4.right_price < stroke_2.left_price:
                    if log_level.value >= LogLevel.Detailed.value:
                        print(
                            f'上升笔，'
                            f'第4笔的右侧价（{stroke_4.right_price}）'
                            f' < '
                            f'第2笔的左侧价（{stroke_2.left_price}），'
                            f'没有重叠。'
                        )
                    return False

                # 其他情况（stroke_4 的右侧价 >= stroke_2 的左侧价）
                else:
                    overlap_high = min(stroke_2.right_price, stroke_4.right_price)
                    overlap_low = stroke_2.left_price

            # 如果 stroke_2 的左侧价 <= stroke_4 的左侧价 < stroke_2 的右侧价：
            elif stroke_2.left_price <= stroke_4.left_price < stroke_2.right_price:
                overlap_high = min(stroke_2.right_price, stroke_4.right_price)
                overlap_low = stroke_4.left_price

            # 如果 stroke_4.left_price >= stroke_2.right_price
            else:
                if log_level.value >= LogLevel.Detailed.value:
                    print(
                        '出错了！\n'
                        f'第4笔的左侧价（{stroke_4.left_price}）'
                        f' >= '
                        f'第2笔的右侧价（{stroke_2.right_price}）。'
                    )
                return False

        # 如果 stroke_2 是下降笔，且，stroke_4 是下降笔：
        elif stroke_2.trend == Trend.Bearish and stroke_4.trend == Trend.Bearish:

            # 如果 stroke_4 的左侧价 > stroke_2 的左侧价：
            if stroke_4.left_price > stroke_2.left_price:
                # 如果
                #     1. stroke_4 的右侧价 > stroke_2 的左侧价
                # 没有重叠
                if stroke_4.right_price > stroke_2.left_price:
                    if log_level.value >= LogLevel.Detailed.value:
                        print(
                            f'下降笔，'
                            f'第4笔的右侧价（{stroke_4.right_price}）'
                            f' > '
                            f'第2笔的左侧价（{stroke_2.left_price}），'
                            f'没有重叠。'
                        )
                    return False
                else:
                    overlap_high = stroke_2.left_price
                    overlap_low = max(stroke_2.right_price, stroke_4.right_price)

            # 如果 stroke_2 的右侧价 <= stroke_4 的左侧价 < stroke_2 的左侧价：
            elif stroke_2.right_price <= stroke_4.left_price < stroke_2.left_price:
                overlap_high = stroke_4.left_price
                overlap_low = max(stroke_2.right_price, stroke_4.right_price)

            # 如果 stroke_4.left_price <= stroke_2.right_price
            else:
                if log_level.value >= LogLevel.Detailed.value:
                    print(
                        '出错了！\n'
                        f'第4笔的左侧价（{stroke_4.left_price}）'
                        f' <= '
                        f'第2笔的右侧价（{stroke_2.right_price}）。'
                    )
                return False

        # 如果：
        #     stroke_2 的趋势和 stroke_4 的不同：
        # 出错了。
        else:
            if log_level.value >= LogLevel.Detailed.value:
                print(
                    f'第2笔的趋势（{stroke_2.trend.value}）和第4笔的趋势（{stroke_4.trend.value}）不同。'
                )
            return False

        if log_level.value >= LogLevel.Detailed.value:
            print(
                f'        重叠区域 high = {overlap_high}，low = {overlap_low}。'
            )

        new_stroke_pivots: Pivot = Pivot(
            id=self.stroke_pivots_count,
            left_candle=stroke_2.left_candle,
            right_candle=stroke_4.right_candle,
            high=overlap_high,
            low=overlap_low
        )
        self._stroke_pivots.append(new_stroke_pivots)

        if self._log:
            print(
                LOG_STROKE_PIVOT_GENERATED.format(
                    id=new_stroke_pivots.id + 1,
                    high=new_stroke_pivots.high,
                    low=new_stroke_pivots.low,
                    left=new_stroke_pivots.left_ordinary_id,
                    right=new_stroke_pivots.right_ordinary_id
                )
            )
        
        return True

    def run_step_by_step(self, high: float, low: float):
        """
        Run step by step, with a pair of float.

        :param high: float, the high price of new candle.
        :param low:  float, the low price of new candle.
        :return: None.
        """
        action: Action

        # --------------------
        # 关于 合并K线
        # --------------------
        ordinary_candle: OrdinaryCandle = OrdinaryCandle(
            high=high,
            low=low
        )

        action = self.update_merged_candle(ordinary_candle)

        # 如果 不是 生成新的合并K线，返回。
        if action != Action.MergedCandleGenerated:
            return

        # --------------------
        # 关于 笔
        # --------------------
        # 如果 笔的数量 == 0：
        if self.strokes_count == 0:
            # 尝试生成首根笔（同时生成第1、第2个分型）。
            self.generate_first_stroke()

            # 即使生成了新的笔，笔的数量也就是1根，不足以进一步计算。
            # 返回。
            return

        # 如果 笔的数量 > 0，尝试延伸笔（同时修正分型）。
        else:
            action = self.extend_stroke()

            # 如果 延伸笔 没有成功，尝试生成反向笔。
            if action != Action.StrokeExtended:
                self.generate_following_stroke()

            # 无论 延伸笔 或者 生成反向笔 的结果是成功或者失败，
            # 都需要根据线段的数量判定下一步。

        # --------------------
        # 关于 线段
        # --------------------
        # 如果线段的数量 == 0，尝试生成首根线段。
        if self.segments_count == 0:
            self.generate_first_segment()
            # 即使生成了新的线段，线段的数量也就是1根，不足以进一步计算。
            # 返回。
            return

        # 如果线段的数量 > 0，尝试扩张线段。
        else:
            last_stroke: Stroke = self._strokes[-1]
            last_segment: Segment = self._segments[-1]

            # 最新笔id 与 最新线段内右侧笔id 的距离。
            delta = last_stroke.id - last_segment.stroke_id_list[-1]
            print('笔和线段右侧笔 id Delta = ', delta)

            if delta == 0:
                self.extend_segment()   # 最新合并K线 id > 最新线段右侧合并K线 id ?
            elif delta == 1:
                pass
            elif delta == 2:
                self.expand_segment()
            elif delta == 3:
                self.generate_following_segment()
            else:
                self.generate_gap_segment()

    def run_with_dataframe(self,
                           df: pd.DataFrame,
                           count: Optional[int] = None,
                           log_level: Optional[LogLevel] = None
                           ) -> None:
        """
        Run with lots of data in pandas DataFrame format.

        :param df:    pandas DataFrame. A series of bar data, the index should be DatetimeIndex,
                      and the columns should contains open, high, low, close and volume.
        :param count: int. How many rows of df should be calculate.
        :param log_level:
        :return: None.
        """
        # Handle parameters.
        if count is None or count <= 0:
            count = len(df)
        if log_level is None:
            log_level = self._log_level

        width: int = len(str(count - 1)) + 1

        for idx in range(count):

            log_event_new_turn(log_level, idx, count)

            self.run_step_by_step(
                high=df.iloc[idx].at['high'].copy(),
                low=df.iloc[idx].at['low'].copy()
            )

            if log_level.value >= LogLevel.Normal.value:
                print(f'\n  ■ 处理完毕。')

                # 合并K线
                print(f'\n    合并K线数量： {self.merged_candles_count}。')
                for i in range(1, 4):
                    if self.merged_candles_count >= i:
                        candle = self._merged_candles[-i]
                        print(
                            f'      向向左第{i}根合并K线：'
                            f'自 {candle.left_ordinary_id} 至 {candle.right_ordinary_id}，'
                            f'周期 = {candle.period}；'
                        )
                    else:
                        print(f'      向向左第{i}根合并K线：不存在；')

                # 分型
                print(f'\n    分型数量： {self.fractals_count}。')
                for i in range(1, 3):
                    if self.fractals_count >= i:
                        fractal = self._fractals[-i]
                        print(
                            f'      向向左第{i}个分型：id = {fractal.id}，'
                            f'pattern = {fractal.pattern.value}，'
                            f'id（普通K线）= {fractal.ordinary_id}。'
                        )
                    else:
                        print(f'      向向左第{i}个分型：不存在。')

                # 笔
                print(f'\n    笔数量： {self.strokes_count}。')
                for i in range(1, 4):
                    if self.strokes_count >= i:
                        stroke = self._strokes[-i]
                        print(
                            f'      向左第{i}个笔：id = {stroke.id}，trend = {stroke.trend.value}，'
                            f'idx（普通K线）= '
                            f'{stroke.left_ordinary_id} ~ {stroke.right_ordinary_id}，'
                            f'price = {stroke.left_price} ~ {stroke.right_price}。'
                        )
                    else:
                        print(f'      向前左第{i}个笔：不存在。')

                # 线段
                print(f'\n    线段数量： {self.segments_count}。')
                for i in range(1, 4):
                    if self.segments_count >= i:
                        segment = self._segments[-i]
                        print(
                            f'      向向左第{i}个线段：id = {segment.id}，'
                            f'trend = {segment.trend.value}，'
                            f'idx（普通K线）= '
                            f'{segment.left_ordinary_id} ~ {segment.right_ordinary_id}，'
                            f'price = {segment.left_price} ~ {segment.right_price}，'
                            f'笔 id = {[stroke_id for stroke_id in segment.stroke_id_list]}。'
                        )
                    else:
                        print(f'      向向左第{i}个线段：不存在。')

                # 笔中枢
                print(f'\n    笔中枢数量： {self.stroke_pivots_count}。')
                for i in range(1, 3):
                    if self.stroke_pivots_count >= i:
                        pivot = self._stroke_pivots[-i]
                        print(
                            f'      向向左第{i}个笔中枢：id = {pivot.id}，'
                            f'idx（普通K线）= {pivot.left_ordinary_id} ~ {pivot.right_ordinary_id}，'
                            f'price = {pivot.high} ~ {pivot.low}。'
                        )
                    else:
                        print(f'      向向左第{i}个笔中枢：不存在。')

                # 段中枢
                print(f'\n    段中枢数量： {self.segment_pivots_count}。')
                for i in range(1, 3):
                    if self.segment_pivots_count >= i:
                        pivot = self._segment_pivots[-i]
                        print(
                            f'      向向左第{i}个段中枢：id = {pivot.id}，'
                            f'idx（普通K线）= {pivot.left_ordinary_id} ~ {pivot.right_ordinary_id}，'
                            f'price = {pivot.high} ~ {pivot.low}。'
                        )
                    else:
                        print(f'      向向左第{i}个段中枢：不存在。')

    def plot(self,
             df: pd.DataFrame,
             count: int,
             show_ordinary_id: bool = False,
             show_merged_id: bool = False,
             show_fractal: bool = False,
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
        if show_fractal:
            fractal_t: list = []
            fractal_b: list = []
            previous_fractal_ordinary_id: int = 0

            for i in range(self.fractals_count):
                fractal = self._fractals[i]

                # idx from previous fractal.ordinary_id to current fractal.ordinary_id
                for j in range(previous_fractal_ordinary_id, fractal.ordinary_id):
                    fractal_t.append(np.nan)
                    fractal_b.append(np.nan)

                if fractal.pattern == FractalPattern.Top:
                    fractal_t.append(fractal.middle_candle.high + fractal_marker_offset)
                    fractal_b.append(np.nan)
                else:
                    fractal_t.append(np.nan)
                    fractal_b.append(fractal.middle_candle.low - fractal_marker_offset)
                previous_fractal_ordinary_id = fractal.ordinary_id + 1

            for i in range(previous_fractal_ordinary_id, count):
                fractal_t.append(np.nan)
                fractal_b.append(np.nan)

            additional_plot.append(
                mpf.make_addplot(
                    fractal_t,
                    type='scatter',
                    markersize=fractal_marker_size,
                    marker='v'
                )
            )
            additional_plot.append(
                mpf.make_addplot(
                    fractal_b,
                    type='scatter',
                    markersize=fractal_marker_size,
                    marker='^'
                )
            )

        # 笔
        plot_stroke: List[Tuple[str, float]] = []
        if self.strokes_count > 0:

            for stroke in self._strokes:
                plot_stroke.append(
                    (
                        df.index[stroke.left_ordinary_id],
                        stroke.left_price
                    )
                )
                # print(stroke.id, stroke.left_candle)
            plot_stroke.append(
                (
                    df.index[self._strokes[-1].right_ordinary_id],
                    self._strokes[-1].right_price
                )
            )
            # print(self._strokes[-1].id, self._strokes[-1].right_candle)

        # 线段
        plot_segment: List[Tuple[str, float]] = []
        if self.segments_count > 0:
            for segment in self._segments:
                plot_segment.append(
                    (
                        df.index[segment.left_ordinary_id],
                        segment.left_price
                    )
                )
            plot_segment.append(
                (
                    df.index[self._segments[-1].right_ordinary_id],
                    self._segments[-1].right_price
                )
            )

        # 同级别分解线
        plot_isolation: List[str] = []
        for isolation in self._isolation_lines:
            plot_isolation.append(
                df.index[isolation.candle.right_ordinary_id]
            )

        # 线
        al = plot_stroke if len(plot_segment) == 0 else [plot_stroke, plot_segment]
        co = 'k' if len(plot_segment) == 0 else ['k', 'r']

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
                'alines': al,
                'colors': co,
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

        if self._log_level >= LogLevel.Normal.value:
            for k, v in mpf_config.items():
                print(k, ': ', v)

        candle_width = mpf_config['candle_width']
        line_width = mpf_config['line_width']

        # 额外的元素。
        patches = []

        # 生成合并K线元素。
        for idx in range(self.merged_candles_count):
            candle = self._merged_candles[idx]

            if candle.left_ordinary_id > count:
                break

            if not show_all_merged and candle.period == 1:
                continue
            patches.append(
                Rectangle(
                    xy=(
                        candle.left_ordinary_id - candle_width / 2,
                        candle.low
                    ),
                    width=candle.period - 1 + candle_width,
                    height=candle.high - candle.low,
                    angle=0,
                    linewidth=line_width * merged_candle_edge_width,
                    edgecolor='black',
                    facecolor='gray' if hatch_merged else 'none',

                )
            )

        # 生成笔中枢元素。
        for pivot in self._stroke_pivots:
            if pivot.left_ordinary_id > count:
                break
            patches.append(
                Rectangle(
                    xy=(
                        pivot.left_ordinary_id - candle_width / 2,
                        pivot.low
                    ),
                    width=pivot.right_ordinary_id - pivot.left_ordinary_id,
                    height=pivot.high - pivot.low,
                    angle=0,
                    linewidth=line_width * merged_candle_edge_width * 2,
                    edgecolor='red',
                    facecolor='none',
                    fill=False,
                )
            )

        # 生成 patch。
        patch_collection: PatchCollection = PatchCollection(
            patches,
            alpha=0.35
        )

        # 添加 patch 到 axis。
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

            for i in range(self.merged_candles_count):
                candle = self._merged_candles[i]
                idx_chan_x.append(candle.right_ordinary_id - candle_width / 2)
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
