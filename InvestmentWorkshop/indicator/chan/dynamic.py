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
    LOG_CANDLE_GENERATED,
    LOG_CANDLE_UPDATED,
    LOG_FRACTAL_GENERATED,
    LOG_STROKE_GENERATED,
    LOG_STROKE_EXTENDED,
    LOG_SEGMENT_GENERATED,
    LOG_SEGMENT_EXTENDED,
    LOG_SEGMENT_EXPANDED,
    LOG_ISOLATION_LINE_GENERATED,
    LOG_STROKE_PIVOT_GENERATED,
)
from .utility import (
    is_regular_fractal,
    is_potential_fractal,
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
    缠论。
    """

    _log: bool
    _verbose: bool
    _potential_fractal: PotentialFractal

    def __init__(self, strict_mode: bool = True, log: bool = False, verbose: bool = False):
        """
        Initialize the object.

        :param strict_mode:
        :param log:
        :param verbose:
        """
        super().__init__(strict_mode)
        self._log = log
        self._verbose = verbose

    def is_fractal(self, merged_candle_id: int) -> Tuple[bool, Optional[FractalPattern]]:
        if merged_candle_id <= 0:
            return False, None
        left_candle: MergedCandle = self._merged_candles[merged_candle_id - 1]
        middle_candle: MergedCandle = self._merged_candles[merged_candle_id]
        right_candle: MergedCandle = self._merged_candles[merged_candle_id + 1]
        if middle_candle.high > left_candle.high and \
                middle_candle.high > right_candle.high:
            return True, FractalPattern.Top
        elif middle_candle.low < left_candle.low and \
                middle_candle.low < right_candle.low:
            return True, FractalPattern.Bottom
        else:
            return False, None

    def get_ordinary_candle_id(self, merged_candle_id: int) -> Optional[int]:
        return self._merged_candles[merged_candle_id].right_ordinary_id

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

    def update_merged_candle(self, ordinary_candle: OrdinaryCandle) -> Action:
        """
        Update the merged candles。

        :param ordinary_candle:
        :return: Action. If new merged candle was generated, return <Action.MergedCandleGenerated>.
                 If last merged candle was updated, return <Action.MergedCandleUpdated>.
        """

        # 合并K线列表长度 == 0：
        #     直接加入。
        if self.merged_candles_count == 0:
            new_merged_candle: MergedCandle = MergedCandle(
                    id=self.merged_candles_count,
                    high=ordinary_candle.high,
                    low=ordinary_candle.low,
                    period=1,
                    left_ordinary_id=0
                )

            self._merged_candles.append(new_merged_candle)

            if self._log:
                print(
                    LOG_CANDLE_GENERATED.format(
                        id=new_merged_candle.id + 1,
                        ordinary_id=new_merged_candle.ordinary_id,
                        period=new_merged_candle.period,
                        high=new_merged_candle.high,
                        low=new_merged_candle.low
                    )
                )

            return Action.MergedCandleGenerated

        # 合并K线列表长度 > 0：
        merged_candle_p1: MergedCandle = self._merged_candles[-1]  # 前1合并K线。

        # 如果没有包含关系：
        #     加入。
        if not self.is_inclusive(merged_candle_p1, ordinary_candle):
            new_merged_candle: MergedCandle = MergedCandle(
                id=self.merged_candles_count,
                high=ordinary_candle.high,
                low=ordinary_candle.low,
                period=1,
                left_ordinary_id=merged_candle_p1.right_ordinary_id + 1
            )

            self._merged_candles.append(new_merged_candle)

            if self._log:
                print(
                    LOG_CANDLE_GENERATED.format(
                        id=new_merged_candle.id + 1,
                        ordinary_id=new_merged_candle.ordinary_id,
                        period=new_merged_candle.period,
                        high=new_merged_candle.high,
                        low=new_merged_candle.low
                    )
                )

            return Action.MergedCandleGenerated

        # 如果有包含关系：
        else:

            # 如果前合并K线是第一根合并K线：
            #     取前合并K线和新普通K线的最大范围。
            if self.merged_candles_count == 1:
                merged_candle_p1.high = max(
                        merged_candle_p1.high,
                        ordinary_candle.high
                    )
                merged_candle_p1.low = min(
                    merged_candle_p1.low,
                    ordinary_candle.low
                )
                merged_candle_p1.period += 1

                if self._log:
                    print(
                        LOG_CANDLE_UPDATED.format(
                            id=merged_candle_p1.id + 1,
                            ordinary_id=merged_candle_p1.ordinary_id,
                            period=merged_candle_p1.period,
                            high=merged_candle_p1.high,
                            low=merged_candle_p1.low
                        )
                    )

                return Action.MergedCandleUpdated

            # 前合并K线不是第一根合并K线：
            #     判断前1缠论K线和前2缠论K线的方向。
            else:
                merged_candle_p2: MergedCandle = self._merged_candles[-2]   # 前2合并K线。

                # 如果 前1缠论K线 与 前2缠论K线： 高点 > 高点 且 低点 > 低点：
                #     合并取 高-高。
                if (
                        merged_candle_p1.high > merged_candle_p2.high and
                        merged_candle_p1.low > merged_candle_p2.low
                ):
                    merged_candle_p1.high = max(
                        merged_candle_p1.high,
                        ordinary_candle.high
                    )
                    merged_candle_p1.low = max(
                        merged_candle_p1.low,
                        ordinary_candle.low
                    )
                    merged_candle_p1.period += 1

                    if self._log:
                        print(
                            LOG_CANDLE_UPDATED.format(
                                id=merged_candle_p1.id + 1,
                                ordinary_id=merged_candle_p1.ordinary_id,
                                period=merged_candle_p1.period,
                                high=merged_candle_p1.high,
                                low=merged_candle_p1.low
                            )
                        )

                    return Action.MergedCandleUpdated

                # 如果 前1缠论K线 与 前2缠论K线： 高点 > 高点 且 低点 > 低点：
                #     合并取 低-低。
                elif (
                        merged_candle_p1.high < merged_candle_p2.high and
                        merged_candle_p1.low < merged_candle_p2.low
                ):
                    merged_candle_p1.high = min(
                        merged_candle_p1.high,
                        ordinary_candle.high
                    )
                    merged_candle_p1.low = min(
                        merged_candle_p1.low,
                        ordinary_candle.low
                    )
                    merged_candle_p1.period += 1

                    if self._log:
                        print(
                            LOG_CANDLE_UPDATED.format(
                                id=merged_candle_p1.id + 1,
                                ordinary_id=merged_candle_p1.ordinary_id,
                                period=merged_candle_p1.period,
                                high=merged_candle_p1.high,
                                low=merged_candle_p1.low
                            )
                        )

                    return Action.MergedCandleUpdated

                # 其它情况：
                #     判定为出错。
                else:
                    print(
                        f'【ERROR】在合并K线时发生错误——未知的前K与前前K高低关系。\n'
                        f'前1高：{merged_candle_p1.high}，前2高：{merged_candle_p1.high}；\n'
                        f'前1低：{merged_candle_p1.low}，前2低：{merged_candle_p1.low}。'
                    )

        return Action.NothingChanged

    def generate_potential_fractal(self) -> None:
        magic_number: int = 5
        print(0, None, '跳过')
        for i in range(1, magic_number):
            b, f = self.is_fractal(i)
            print(i, b, f)

    def update_fractals(self) -> Action:
        """
        Update the fractals and/or strokes.

        :return: Action.
                 Return <Action.FractalGenerated> if a new fractal was generated.
                 Return <Action.FractalConfirmed> if a existed fractal was confirmed.
                 Return <Action.FractalDropped> if a existed fractal was dropped.
                 Return <Action.NothingChanged> if nothing was changed.
        """
        # 如果 合并K线数量 < 3：退出，返回 <Action.NothingChanged>。
        if self.merged_candles_count < 3:
            if self._verbose:
                print(
                    f'\n  ○ 尝试生成分型：目前共有合并K线 {self.merged_candles_count} 个，最少需要 3 个。'
                )
            return Action.NothingChanged

        # 如果 分型数量 > 0：
        #     1. 尝试生成笔；
        #     2. 替代潜在分型；
        #     3. 生成新分型
        if self.fractals_count >= 1:
            # 如果 合并K线的数量 < 最小距离 + 1： 退出。
            if self.merged_candles_count < self._minimum_distance + 1:
                if self._verbose:
                    print(
                        f'\n  ○ 尝试生成笔：目前共有合并K线 {self.merged_candles_count} 根，'
                        f'最少需要 {self._minimum_distance + 1} 根。'
                    )
            else:
                last_candle: MergedCandle = self._merged_candles[-1]
                succeed: bool
                potential_fractal: FractalPattern
                succeed, potential_fractal, _ = is_potential_fractal(
                    FirstOrLast.Last, self._merged_candles
                )
                if self._verbose:
                    print(
                        f'\n  ○ 尝试生成笔：\n    最新合并K线，'
                        f'merged id（合并K线）= {last_candle.id}，'
                        f'ordinary id（普通K线）= {last_candle.ordinary_id}，'
                        f'潜在分型 = {potential_fractal}。'
                    )

            if self._merged_candles[-1].id == self._fractals[-1].id - 1:
                return Action.NothingChanged

        # 如果 分型数量 == 0：尽可能生成分型。
        if self.fractals_count == 0:
            # 声明变量类型且赋值。
            left_candle: MergedCandle = self._merged_candles[-3]
            middle_candle: MergedCandle = self._merged_candles[-2]
            right_candle: MergedCandle = self._merged_candles[-1]

            succeed: bool
            pattern: FractalPattern
            succeed, pattern = is_regular_fractal(left_candle, middle_candle, right_candle)
            if succeed:
                new_fractal: Fractal = Fractal(
                    id=self.fractals_count,
                    pattern=pattern,
                    left_candle=left_candle,
                    middle_candle=middle_candle,
                    right_candle=right_candle,
                    is_confirmed=False
                )

                self._fractals.append(new_fractal)

                if self._log:
                    print(
                        LOG_FRACTAL_GENERATED.format(
                            id=new_fractal.id + 1,
                            pattern=new_fractal.pattern.value,
                            merged_id=new_fractal.merged_id,
                            ordinary_id=new_fractal.ordinary_id
                        )
                    )

            return Action.FractalGenerated

    def generate_first_stroke(self) -> Action:
        """
        Generate the first stroke.

        :return:
        """
        # Define verbose message.
        verbose_message: Dict[str, str] = {
            'not_enough_merged_candle':
                '\n  ○ 尝试生成笔：目前共有合并K线 {count} 根，最少需要 {minimum} 根。',
            'right_merged_candle':
                '\n  ○ 尝试生成笔：\n'
                '    最新合并K线，merged id（合并K线）= {mc_id}，ordinary id（普通K线）= {oc_id}，'
                '潜在分型 = {potential_fractal}。',
            'left_merged_candle':
                '    左合并K线，merged id（合并K线）= {mc_id}，ordinary id（普通K线）= {oc_id}',
            'fractal':
                '        潜在分型 = {fractal}，{result}',
            'distance':
                '        距离 = {distance}，{result}',
        }

        # 如果 合并K线的数量 < 最小距离 + 1： 退出。
        if self.merged_candles_count < self._minimum_distance + 1:
            if self._verbose:
                print(
                    verbose_message['not_enough_merged_candle'].format(
                        count=self.merged_candles_count,
                        minimum=self._minimum_distance + 1
                    )
                )
            return Action.NothingChanged

        # 申明变量类型并赋值。
        right_merged_candle: MergedCandle = self._merged_candles[-1]
        succeed: bool
        right_fractal_pattern: FractalPattern
        succeed, right_fractal_pattern, _ = is_potential_fractal(
            FirstOrLast.Last, self._merged_candles
        )
        # valid_fractal: bool

        left_merged_candle: MergedCandle
        left_fractal_pattern: FractalPattern
        distance: int

        new_stroke: Stroke

        # Print verbose message.
        if self._verbose:
            print(
                verbose_message['right_merged_candle'].format(
                    mc_id=right_merged_candle.id,
                    oc_id=right_merged_candle.ordinary_id,
                    potential_fractal=right_fractal_pattern.value
                )
            )

        # 自前向后穷举 left_merged_candle，如果：
        #     1. left_merged_candle 和 right_merged_candle 的距离满足最小要求，且
        #     2. left_merged_candle 和 right_merged_candle 类型不同
        # 生成笔。
        for i in range(0, right_merged_candle.id):
            # 取得 left_merged_candle。
            left_merged_candle = self._merged_candles[i]
            if self._verbose:
                print(
                    verbose_message['left_merged_candle'].format(
                        mc_id=left_merged_candle.id,
                        oc_id=left_merged_candle.ordinary_id
                    )
                )

            # 测试距离。
            distance = right_merged_candle.id - left_merged_candle.id
            if self._verbose:
                print(
                    verbose_message['distance'].format(
                        distance=distance,
                        result='满足' if distance >= self._minimum_distance else '不满足'
                    )
                )
            # 如果：
            #     left_merged_candle 与 right_merged_candle 之间的距离不满足最小要求
            # 退出循环。
            if distance < self._minimum_distance:
                break

            # 测试分型。
            valid_fractal, left_fractal_pattern = self.is_fractal(left_merged_candle.id)
            # left_fractal_pattern = self.is_potential_fractal(left_merged_candle.id)
            if self._verbose:
                print(
                    verbose_message['fractal'].format(
                        fractal='非分型' if left_fractal_pattern is None
                        else left_fractal_pattern.value,
                        result='不满足'
                        if left_fractal_pattern is None or
                                left_fractal_pattern == right_fractal_pattern
                        else '满足'
                    )
                )
                # print(
                #     verbose_message['fractal'].format(
                #         fractal='非分型' if left_fractal_pattern is None
                #         else left_fractal_pattern.value,
                #         result='不满足'
                #         if left_fractal_pattern is None or
                #            left_fractal_pattern == right_fractal_pattern
                #         else '满足'
                #     )
                # )

            # 如果：
            #     1. left_merged_candle 不能形成分型，或
            #     1. left_merged_candle 形成的分型与 right_merged_candle 形成的潜在分型同类
            # 下一次循环。
            if not left_fractal_pattern or left_fractal_pattern == right_fractal_pattern:
                continue

            new_stroke = Stroke(
                id=self.strokes_count,
                trend=Trend.Bullish if left_fractal_pattern == FractalPattern.Bottom
                else Trend.Bearish,
                left_candle=left_merged_candle,
                right_candle=right_merged_candle
            )
            self._strokes.append(new_stroke)

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

            return Action.StrokeGenerated

        return Action.NothingChanged

    def extend_stroke(self) -> Action:
        """
        Extend an existed stroke.

        :return:
        """
        verbose_message: Dict[str, str] = {
            'extend_stroke':
                '\n  ○ 尝试顺向延伸笔：\n    最新笔 id = {stroke_id}，{stroke_trend}，'
                '右侧合并K线 id = {right_candle_id}，右侧价 = {right_price}，'
                '\n    最新合并K线 id = {merged_candle_id}，潜在分型 = {potential_fractal}，'
                '最高价 = {high}，最低价 = {low}'
        }

        # 申明变量类型并赋值。
        last_stroke: Stroke = self._strokes[-1]
        last_merged_candle: MergedCandle = self._merged_candles[-1]
        succeed: bool
        potential_fractal: Optional[FractalPattern] = None
        succeed, pattern, _ = is_potential_fractal(FirstOrLast.Last, self._merged_candles)

        # 如果：
        #     A1. last_stroke 的 trend 是 上升，且
        #     A3. last_merged_candle 的最高价 >= last_stroke 的右侧价 （顺向超越或达到）：
        #   或
        #     B1. last_stroke 的 trend 是 下降，且
        #     B3. last_merged_candle 的最低价 <= last_stroke 的右侧价 （顺向超越或达到）：
        # 延伸（调整）笔。

        if self._verbose:
            print(
                verbose_message['extend_stroke'].format(
                    stroke_id=last_stroke.id,
                    stroke_trend=last_stroke.trend.value,
                    right_candle_id=last_stroke.right_candle.id,
                    right_price=last_stroke.right_price,
                    merged_candle_id=last_merged_candle.id,
                    potential_fractal=potential_fractal.value if potential_fractal else '不存在',
                    high=last_merged_candle.high,
                    low=last_merged_candle.low
                )
            )

        if (
                last_stroke.trend == Trend.Bullish and
                # potential_fractal == FractalPattern.Top and
                last_merged_candle.high >= last_stroke.right_price
        ) or (
                last_stroke.trend == Trend.Bearish and
                # potential_fractal == FractalPattern.Bottom and
                last_merged_candle.low <= last_stroke.right_price
        ):

            if self._log:
                print(
                    LOG_STROKE_EXTENDED.format(
                        id=last_stroke.id + 1,
                        trend=last_stroke.trend,
                        old_mc_id=last_stroke.right_candle.id,
                        new_mc_id=last_merged_candle.id,
                        old_oc_id=last_stroke.right_candle.ordinary_id,
                        new_oc_id=last_merged_candle.ordinary_id
                    )
                )

            last_stroke.right_candle = last_merged_candle

            return Action.StrokeExtended
        else:
            return Action.NothingChanged

    def generate_following_stroke(self) -> Action:
        """
        Generate reversal stroke.
        :return:
        """

        last_merged_candle: MergedCandle = self._merged_candles[-1]
        last_stroke: Stroke = self._strokes[-1]

        distance = last_merged_candle.id - last_stroke.right_candle.id
        succeed: bool
        potential_fractal: Optional[FractalPattern]
        succeed, potential_fractal, _ = is_potential_fractal(
            FirstOrLast.Last,
            self._merged_candles
        )

        if self._verbose:
            print(
                f'\n  ○ 尝试反向生成笔：'
                f'\n    最新笔 id = {last_stroke.id}，{last_stroke.trend}，'
                f'右侧合并K线 id= {last_stroke.right_candle.id}，'
                f'idx = {last_stroke.right_ordinary_id}'
                f'\n    最新合并K线 id = {last_merged_candle.id}，'
                f'潜在分型 = {potential_fractal.value if potential_fractal else "不存在"}，'
                f'idx = {last_merged_candle.ordinary_id}，距离 = {distance}'
            )

        # 如果：
        #     A1. last_stroke 的 trend 是 上升，且
        #     A2. last_merged_candle 是 潜在底分型，且
        #     A3. last_merged_candle 的最高价 < last_stroke 的 右侧价，且？
        #   或
        #     B1. last_stroke 的 trend 是 下降，且
        #     B2. last_merged_candle 是 潜在顶分型，且
        #     B3. fractal_p1 的3根 merged candle 的最低价 > last_stroke 的 右侧价，且？
        #   且
        #     3. last_merged_candle 和 last_stroke 的右分型的距离满足要求，且
        # 生成（反向）笔。
        # TODO: 需要检查潜在分型。
        if (
                (
                        last_stroke.trend == Trend.Bullish and
                        potential_fractal == FractalPattern.Bottom and
                        max(
                            self._merged_candles[last_merged_candle.id - 1].high,
                            last_merged_candle.high
                        ) < last_stroke.right_price
                ) or (
                        last_stroke.trend == Trend.Bearish and
                        potential_fractal == FractalPattern.Top and
                        min(
                            self._merged_candles[last_merged_candle.id - 1].low,
                            last_merged_candle.low
                        ) > last_stroke.right_price
                )
        ) and distance >= self._minimum_distance:

            new_stroke: Stroke = Stroke(
                id=self.strokes_count,
                trend=Trend.Bullish if last_stroke.trend == Trend.Bearish
                else Trend.Bearish,
                left_candle=last_stroke.right_candle,
                right_candle=last_merged_candle,
            )
            self._strokes.append(new_stroke)

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

            return Action.StrokeGenerated
        else:
            return Action.NothingChanged

    def generate_first_segment(self) -> Action:
        """
        Generate the first segments.
        :return: None.
        """
        # 如果 笔数量 < 3： 退出。
        if self.strokes_count < 3:
            if self._verbose:
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

        if self._verbose:
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
            if self._verbose:
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

        if self._verbose:
            print(
                f'        重叠区间 high = {overlap_high}，low = {overlap_low}，通过。'
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
                '        笔 id（stroke_id） > 线段的右侧笔 id（segment_stroke_id），退出。',
            'pass':
                '        笔 id 相同，趋势相同，笔右侧价 达到或超越 线段右侧价，通过。',
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

        if self._verbose:
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
            if self._verbose:
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
            if self._verbose:
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
                '        最新笔的趋势 与 线段右侧笔的趋势 不同，退出。',
            'same_trend':
                '        最新笔的趋势 与 线段右侧笔的趋势 相同，通过。',
            'not_achieve_or_beyond':
                '        最新笔的右侧价 没有达到或超越 线段的右侧价，退出。',
            'achieve_or_beyond':
                '        最新笔的右侧价 达到或超越 线段的右侧价，通过。',
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

        if self._verbose:
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
            if self._verbose:
                print(verbose_message['not_same_trend'])
            return Action.NothingChanged
        else:
            if self._verbose:
                print(verbose_message['same_trend'])

        if (
                last_stroke.trend == Trend.Bullish and
                last_stroke.right_price >= right_stroke_in_last_segment.right_price
        ) or (
                last_stroke.trend == Trend.Bearish and
                last_stroke.right_price <= right_stroke_in_last_segment.right_price
        ):

            if self._verbose:
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

        if self._verbose:
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

        if self._verbose:
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

        if self._verbose:
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
            if self._verbose:
                print(f'\n  ○ 尝试生成笔中枢：目前尚无线段。')
            return False

        last_segment: Segment = self._segments[-1]
        if last_segment.strokes_count <= 3:
            if self._verbose:
                print(f'\n  ○ 尝试生成笔中枢：当前线段仅包含3根笔。')
            return False

        stroke_2_id: int = last_segment.stroke_id_list[1]
        stroke_2: Stroke = self._strokes[stroke_2_id]
        stroke_3_id: int = last_segment.stroke_id_list[2]
        stroke_3: Stroke = self._strokes[stroke_3_id]
        stroke_4_id: int = last_segment.stroke_id_list[3]
        stroke_4: Stroke = self._strokes[stroke_4_id]
        
        if self._verbose:
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
                    if self._verbose:
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
                if self._verbose:
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
                    if self._verbose:
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
                if self._verbose:
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
            if self._verbose:
                print(
                    f'第2笔的趋势（{stroke_2.trend.value}）和第4笔的趋势（{stroke_4.trend.value}）不同。'
                )
            return False

        if self._verbose:
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
        # 关于 分型
        # --------------------
        if self.merged_candles_count > 0:
            self.update_fractals_and_strokes()

        # --------------------
        # 关于 笔
        # --------------------
        # 如果 笔的数量 == 0：
        if self.strokes_count == 0:
            # 尝试生成首根笔。
            self.generate_first_stroke()

            # 即使生成了新的笔，笔的数量也就是1根，不足以进一步计算。
            # 返回。
            return

        # 如果 笔的数量 > 0，尝试延伸笔。
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

    def run_with_dataframe(self, df: pd.DataFrame, count: int = 0) -> None:
        """
        Run with lots of data in pandas DataFrame format.

        :param df:    pandas DataFrame. A series of bar data, the index should be DatetimeIndex,
                      and the columns should contains open, high, low, close and volume.
        :param count: int. How many rows of df should be calculate.
        :return: None.
        """
        working_count: int = len(df) if count == 0 else count
        width: int = len(str(working_count - 1)) + 1

        for idx in range(working_count):

            if self._log:
                print(f'\n【第 {idx:>{width}} / {working_count - 1:>{width}} 轮】（按普通K线编号）')

            self.run_step_by_step(
                high=df.iloc[idx].at['high'].copy(),
                low=df.iloc[idx].at['low'].copy()
            )

            if self._log:
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

        if self._verbose:
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
