# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Tuple, Optional
from copy import deepcopy

from .definition import (
    Action,

    FractalPattern,
    Trend,

    OrdinaryCandle,
    MergedCandle,
    Fractal,
    Stroke,
    Segment,

    MergedCandleList,
    FractalList,
    StrokeList,
    SegmentList,
    IsolationLineList,
    StrokePivotList,
    SegmentPivotList,

    Chan,
)


def is_inclusive_number(h1: float,
                        l1: float,
                        h2: float,
                        l2: float) -> bool:
    """
    判断两根K线是否存在包含关系。两根K线的关系有以下九种：
        1. H1 > H2 & L1 > L2, 非包含，下降。
        2. H1 > H2 & L1 = L2, 包含, K1包含K2, 下降。
        3. H1 > H2 & L1 < L2, 包含。
        4. H1 = H2 & L1 > L2, 包含。
        5. H1 = H2 & L1 = L2, 包含。
        6. H1 = H2 & L1 < L2, 包含。
        7. H1 < H2 & L1 > L2, 包含。
        8. H1 < H2 & L1 = L2, 包含。
        9. H1 < H2 & L1 < L2, 非包含, 。

    :param h1: float, HIGH price of current candlestick.
    :param l1: float, LOW price of current candlestick.
    :param h2: float, HIGH price of previous candlestick.
    :param l2: float, LOW price of previous candlestick.

    ----
    :return: bool, if
    """
    if (h1 > h2 and l1 > l2) or (h1 < h2 and l1 < l2):
        return False
    else:
        return True


def is_inclusive_candle(candle_1: OrdinaryCandle,
                        candle_2: OrdinaryCandle
                        ) -> bool:
    """
    判断两根K线是否存在包含关系。两根K线的关系有以下九种：

    :param candle_1: OrdinaryCandle, candlestick 1.
    :param candle_2: OrdinaryCandle, candlestick 2.

    ----
    :return: bool, if
    """

    return is_inclusive_number(
        candle_1.high,
        candle_1.low,
        candle_2.high,
        candle_2.low
    )


def is_overlap(
        left_stroke: Stroke,
        right_stroke: Stroke
) -> Tuple[bool, Optional[float], Optional[float]]:
    """
    Determine whether an overlap range exists between 2 strokes, and return high and low of
    the range if existed.

    :param left_stroke:
    :param right_stroke:
    :return: a 3-element tuple.
             The first is bool, True if the overlap range exists.
             The second is float, high of the overlap range. Return None if the range not exists.
             The second is float, low of the overlap range. Return None if the range not exists.
    """
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
        return False, None, None

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

    return True, overlap_high, overlap_low


def get_trend(left_candle: MergedCandle,
              right_candle: OrdinaryCandle
              ) -> Trend:
    if right_candle.high > left_candle.high and right_candle.low > left_candle.low:
        return Trend.Bullish
    elif right_candle.high < left_candle.high and right_candle.low < left_candle.low:
        return Trend.Bearish
    else:
        raise RuntimeError('缠论K线不应存在包含关系。')


def get_merged_candle_idx(merged_candle: MergedCandle,
                          merged_candle_list: MergedCandleList
                          ) -> int:
    return merged_candle_list.index(merged_candle)


def get_fractal_distance(left_fractal: Fractal,
                         right_fractal: Fractal,
                         merged_candle_list: MergedCandleList) -> int:
    """
    两个分型之间的距离（取分型中间那根K线）。

    :param left_fractal:
    :param right_fractal:
    :param merged_candle_list:

    :return:
    """
    return get_merged_candle_idx(right_fractal.middle_candle, merged_candle_list) - \
        get_merged_candle_idx(left_fractal.middle_candle, merged_candle_list)


def generate_segment(
        segment_list: SegmentList,
        stroke: Stroke,
        log: bool = False,
        verbose: bool = False
) -> Tuple[Action, Optional[SegmentList]]:
    """
    Generate the segments list.

    :param segment_list:
    :param stroke:
    :param log:
    :param verbose:
    :return:
    """
    # 如果 笔数量 < 3： 退出。
    if len(stroke_list) < 3:
        return Action.Nothing, segment_list

    result: SegmentList = deepcopy(segment_list)
    segments_count = len(result)
    strokes_count = len(stroke_list)

    # 如果 线段的数量 == 0：
    #     向前穷举 stroke_p3，如果：
    #         stroke_p3 和 stroke_p1 有重叠：
    #   生成线段。
    if segments_count == 0:

        # 申明变量类型并赋值。
        stroke_p1: Stroke = stroke_list[-1]
        stroke_p2: Stroke
        stroke_p3: Stroke
        overlap_high: float = 0.0  # 重叠区间高值
        overlap_low: float = 0.0  # 重叠区间低值

        if log:
            print(
                f'\n  ○ 尝试生成首根线段：'
                f'目前共有线段 {segments_count} 根，笔 {strokes_count} 根。\n'
                f'    向前（左）第1根笔，id = {stroke_p1.id}，'
                f'high = {max(stroke_p1.left_price, stroke_p1.right_price)}，'
                f'low = {min(stroke_p1.left_price, stroke_p1.right_price)}'
            )
        for i in range(0, stroke_p1.id - 1):
            stroke_p3 = stroke_list[i]
            stroke_p2 = stroke_list[i + 1]

            # 如果 前1笔 的趋势与 前3笔 不一致，重新循环。
            # （理论上不可能，但是留做保险。）
            if stroke_p3.trend != stroke_p1.trend:
                continue

            # 上升笔
            if stroke_p1.trend == Trend.Bullish:
                # 前1笔的左侧价 >= 前3笔的左侧价（前1笔的左侧价必须 < 前3笔的右侧价）
                if stroke_p1.left_price >= stroke_p3.left_price:
                    overlap_low = stroke_p1.left_price
                    if stroke_p1.right_price >= stroke_p3.right_price:
                        overlap_high = stroke_p3.right_price
                    else:
                        overlap_high = stroke_p1.right_price

                # 前1笔的左侧价 < 前3笔的左侧价
                else:
                    overlap_low = stroke_p3.left_price
                    if stroke_p1.right_price >= stroke_p3.right_price:
                        overlap_high = stroke_p3.right_price
                    elif stroke_p3.left_price <= stroke_p1.right_price < stroke_p3.right_price:
                        overlap_high = stroke_p3.left_price
                    elif stroke_p1.right_price < stroke_p3.left_price:
                        return Action.Nothing, segment_list

            # 下降笔
            else:
                # 前1笔的左侧价 <= 前3笔的左侧价（前1笔的左侧价必须 > 前3笔的右侧价）
                if stroke_p1.left_price <= stroke_p3.left_price:
                    overlap_low = stroke_p1.right_price
                    if stroke_p1.right_price <= stroke_p3.right_price:
                        overlap_high = stroke_p3.right_price
                    else:
                        overlap_high = stroke_p1.right_price

                # 前1笔的左侧价 > 前3笔的左侧价
                else:
                    overlap_high = stroke_p3.left_price
                    if stroke_p1.right_price <= stroke_p3.right_price:
                        overlap_low = stroke_p3.right_price
                    elif stroke_p3.right_price <= stroke_p1.right_price < stroke_p3.left_price:
                        overlap_low = stroke_p1.right_price
                    elif stroke_p1.right_price > stroke_p3.left_price:
                        return Action.Nothing, segment_list

            if log:
                print(
                    f'    向前（左）第{stroke_p1.id - stroke_p3.id + 1}根笔，id = {stroke_p3.id}，'
                    f'high = {max(stroke_p3.left_price, stroke_p3.right_price)}，'
                    f'low = {min(stroke_p3.left_price, stroke_p3.right_price)}，'
                    f'overlap high = {overlap_high}，overlap low = {overlap_low}'
                )

            if overlap_high > overlap_low:

                new_segment: Segment = Segment(
                    id=segments_count,
                    trend=Trend.Bullish if stroke_p1.trend == Trend.Bullish else Trend.Bearish,
                    left_stroke=stroke_p3,
                    right_stroke=stroke_p1,
                    strokes=[stroke_p3.id, stroke_p2.id, stroke_p1.id]
                )
                result.append(new_segment)

                if log:
                    print(
                        LOG_MESSAGE['segment_generated'].format(
                            id=new_segment.id + 1,
                            trend=new_segment.trend,
                            left=new_segment.left_ordinary_id,
                            right=new_segment.right_ordinary_id
                        )
                    )

                return Action.Generated, result

    # 如果 线段数量 >= 1：
    else:
        last_segment: Segment = self._segments[-1]
        last_stroke: Stroke = self._strokes[-1]

        if last_stroke.id - last_segment.right_stroke.id < 2:
            pass

        # 在 最新笔的 id - 最新线段的右侧笔的 id == 2 时：
        elif last_stroke.id - last_segment.right_stroke.id == 2:

            if log:
                print(
                    f'\n  ○ 尝试顺向延伸线段：'
                    f'目前共有线段 {segments_count} 根，笔 {strokes_count} 根。\n'
                    f'    最新线段的最新笔 id = {last_segment.right_stroke.id}，'
                    f'trend = {last_segment.right_stroke.trend}，'
                    f'price left = {last_segment.left_price}，'
                    f'price right = {last_segment.right_price}\n'
                    f'    最新          笔 id = {last_stroke.id}，'
                    f'trend = {last_stroke.trend}，'
                    f'price left = {last_stroke.left_price}，'
                    f'price right = {last_stroke.right_price}'
                )

            # 如果：
            #     A1. 上升线段，且
            #     A2. 线段后第2笔 是 上升笔，且
            #     A3. 线段后第2笔的右侧价 >= 线段右侧价
            #   或
            #     B1. 下降线段，且
            #     B2. 线段后第2笔 是 下降笔，且
            #     B3. 线段后第2笔的右侧价 <= 线段右侧价
            # 延伸线段。
            if (
                    last_segment.trend == Trend.Bullish and
                    last_stroke.trend == Trend.Bullish and
                    last_stroke.right_price >= last_segment.right_price
            ) or (
                    last_segment.trend == Trend.Bearish and
                    last_stroke.trend == Trend.Bearish and
                    last_stroke.right_price <= last_segment.right_price
            ):

                if log:
                    print(
                        msg_extend.format(
                            id=last_segment.id + 1,
                            trend=last_segment.trend,
                            old=last_segment.right_ordinary_id,
                            new=last_stroke.right_ordinary_id
                        )
                    )
                for i in range(last_segment.right_stroke.id + 1, last_stroke.id + 1):
                    last_segment.strokes.append(i)
                last_segment.right_stroke = last_stroke

                return True

        # 在 最新笔的 id - 最新线段的右侧笔的 id == 3 时：
        elif last_stroke.id - last_segment.right_stroke.id == 3:
            stroke_n1: Stroke = self._strokes[-3]
            stroke_n2: Stroke = self._strokes[-2]
            stroke_n3: Stroke = self._strokes[-1]

            if verbose:
                print(
                    f'\n  ○ 尝试生成反向线段：'
                    f'目前共有线段 {self.segments_count} 根，笔 {self.strokes_count} 根。\n'
                    f'    最新线段的最新笔 id = {last_segment.right_stroke.id}，'
                    f'trend = {last_segment.right_stroke.trend}，'
                    f'price left = {last_segment.left_price}，'
                    f'price right = {last_segment.right_price}\n'
                    f'    最新线段的右侧第1笔 id = {stroke_n1.id}，'
                    f'trend = {stroke_n1.trend}，'
                    f'price left = {stroke_n1.left_price}，'
                    f'price right = {stroke_n1.right_price}\n'
                    f'    最新线段的右侧第3笔 id = {stroke_n3.id}，'
                    f'trend = {stroke_n3.trend}，'
                    f'price left = {stroke_n3.left_price}，'
                    f'price right = {stroke_n3.right_price}'
                )

            # 如果：
            #     A1. 上升线段，且
            #         A2A. 线段后第1笔的右侧价 <= 线段右侧笔的左侧价，且
            #         A2B. 线段后第3笔的右侧价 <  线段右侧笔的左侧价
            #       或
            #         A3. 线段后第3笔的右侧价 <=  线段后第1笔的右侧价
            #   或
            #     B1. 下降线段，且
            #         B2A. 线段后第1笔的右侧价 >= 线段右侧笔的左侧价，且
            #         B2B. 线段后第3笔的右侧价 >  线段右侧笔的左侧价
            #       或
            #         B3. 线段后第2笔的右侧价 >= 线段后第1笔的右侧价
            # 生成反向线段。
            if (
                    last_segment.trend == Trend.Bullish and
                    stroke_n3.trend == Trend.Bearish and
                    (
                            stroke_n3.right_price <= stroke_n1.right_price or
                            (
                                    stroke_n1.right_price
                                    <= last_segment.right_stroke.left_price
                                    and
                                    stroke_n3.right_price
                                    < last_segment.right_stroke.left_price
                            )
                    )
            ) or (
                    last_segment.trend == Trend.Bearish and
                    stroke_n3.trend == Trend.Bullish and
                    (
                            stroke_n3.right_price >= stroke_n1.right_price or
                            (
                                    stroke_n1.right_price
                                    >= last_segment.right_stroke.left_price
                                    and
                                    stroke_n3.right_price
                                    > last_segment.right_stroke.left_price
                            )
                    )
            ):
                new_segment = Segment(
                    id=self.segments_count,
                    trend=Trend.Bullish
                    if stroke_n3.trend == Trend.Bullish else Trend.Bearish,
                    left_stroke=stroke_n1,
                    right_stroke=stroke_n3,
                    strokes=[stroke_n1.id, stroke_n2.id, stroke_n3.id]
                )
                result.append(new_segment)

                if log:
                    print(
                        msg_generate.format(
                            id=new_segment.id + 1,
                            trend=new_segment.trend,
                            left=new_segment.left_ordinary_id,
                            right=new_segment.right_ordinary_id
                        )
                    )
                # last_segment.right_stroke = self._strokes[stroke_n1.id - 1]

                return True

        # 在 最新笔的 id - 最新线段的右侧笔的 id > 3 时：
        #     既不能顺向突破（id差 == 2）
        #     又不能反向突破（id差 == 3）
        # 跳空。
        else:

            stroke_p1: Stroke = self._strokes[-1]
            stroke_p3: Stroke = self._strokes[-3]

            if log:
                print(
                    f'\n  ○ 尝试生成跳空线段：'
                    f'目前共有线段 {segments_count} 根，笔 {strokes_count} 根。\n'
                    f'    最新线段的最新笔 id = {last_segment.right_stroke.id}，'
                    f'trend = {last_segment.right_stroke.trend}，'
                    f'price left = {last_segment.left_price}，'
                    f'price right = {last_segment.right_price}\n'
                    f'    向前（左）第1笔 id = {stroke_p1.id}，'
                    f'trend = {stroke_p1.trend}，'
                    f'price left = {stroke_p1.left_price}，'
                    f'price right = {stroke_p1.right_price}\n'
                    f'    向前（左）第3笔 id = {stroke_p3.id}，'
                    f'trend = {stroke_p3.trend}，'
                    f'price left = {stroke_p3.left_price}，'
                    f'price right = {stroke_p3.right_price}'
                )

            # 如果：
            #     A1. stroke_p1 是 上升笔，且
            #     A2. stroke_p3 的 左侧价 <= stroke_p1 的 左侧价 < stroke_p3 的 右侧价，且
            #     A3. stroke_p1 的 右侧价 > stroke_p3 的 右侧价
            #   或
            #     B1. stroke_p1 是 下降笔，且
            #     B2. stroke_p3 的 左侧价 <= stroke_p1 的 左侧价 < stroke_p3 的 右侧价，且
            #     B3. stroke_p1 的 右侧价 < stroke_p3 的 右侧价
            # 生成跳空线段。
            if (
                    stroke_p1.trend == Trend.Bullish and
                    stroke_p3.left_price <= stroke_p1.left_price < stroke_p3.right_price
                    < stroke_p1.right_price
            ) or (
                    stroke_p1.trend == Trend.Bearish and
                    stroke_p1.right_price < stroke_p3.right_price <= stroke_p1.left_price
                    < stroke_p3.left_price
            ):
                new_segment: Segment

                # 如果 stroke_p1 与 last_segment 同向：
                if stroke_p1.trend == last_segment.trend:
                    # 如果 stroke_p3 的 id 与 last_segment 的右侧笔的 id 相差 2：
                    # 延伸 last_segment
                    if stroke_p3.id - last_segment.right_stroke.id == 2:
                        if log:
                            print(
                                msg_extend.format(
                                    id=last_segment.id + 1,
                                    trend=last_segment.trend,
                                    old=last_segment.right_ordinary_id,
                                    new=stroke_p1.right_ordinary_id
                                )
                            )
                        for i in range(last_segment.right_stroke.id + 1, stroke_p1.id + 1):
                            last_segment.strokes.append(i)
                        last_segment.right_stroke = stroke_p1

                        return True

                    # 其他情况（ stroke_p3 的 id 与 last_segment 的右侧笔的 id 相差 4 以上）：
                    # 补一根反向线段，起点是 last_segment 的右端点，终点是 stroke_p3 的左端点。
                    else:
                        new_segment = Segment(
                            id=self.segments_count,
                            trend=Trend.Bearish
                            if stroke_p1.trend == Trend.Bullish else Trend.Bullish,
                            left_stroke=self._strokes[last_segment.right_stroke.id + 1],
                            right_stroke=self._strokes[stroke_p3.id - 1],
                            strokes=[
                                i for i in range(last_segment.right_stroke.id + 1, stroke_p3.id)
                            ]
                        )
                        self._segments.append(new_segment)

                        if log:
                            print(
                                msg_generate.format(
                                    id=new_segment.id + 1,
                                    trend=new_segment.trend,
                                    left=new_segment.left_ordinary_id,
                                    right=new_segment.right_ordinary_id
                                )
                            )
                        return True
                # 如果 stroke_p1 与 last_segment 反向：
                else:
                    new_segment = Segment(
                        id=self.segments_count,
                        trend=Trend.Bullish
                        if stroke_p1.trend == Trend.Bullish else Trend.Bearish,
                        left_stroke=self._strokes[last_segment.right_stroke.id + 1],
                        right_stroke=stroke_p1,
                        strokes=[
                            i for i in range(last_segment.right_stroke.id + 1, stroke_p1.id + 1)
                        ]
                    )
                    self._segments.append(new_segment)

                    if log:
                        print(
                            msg_generate.format(
                                id=new_segment.id + 1,
                                trend=new_segment.trend,
                                left=new_segment.left_ordinary_id,
                                right=new_segment.right_ordinary_id
                            )
                        )

                    return True

    return False


def generate_isolation_line(
        isolation_line_list: IsolationLineList,
        segment: Segment,
        log: bool = False,
        verbose: bool = False
):
    pass


def generate_stroke_pivot(
        stroke_pivot_list: StrokePivotList,
        stroke: Stroke,
        log: bool = False,
        verbose: bool = False
):
    pass


def generate_segment_pivot(
        segment_pivot_list: SegmentPivotList,
        segment: Segment,
        log: bool = False,
        verbose: bool = False
):
    pass
