# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List, Optional

from .definition import (
    LogLevel,
    RelationshipInNumbers,
    Trend,
    FractalPattern,

    MergedCandle,
    Fractal,
    Stroke,
    Segment,
)


def log_event_new_turn(log_level: LogLevel,
                       idx: int,
                       count: int
                       ) -> None:
    """
    Log message for a new turn.
    
    :param log_level: enum type LogLevel. 
    :param idx: int. The serials number of the turn. Start from 0.
    :param count: int. The total number of the turns. Start from 0.
    :return: 
    """
    if log_level.value >= LogLevel.Simple.value:
        width: int = len(str(count - 1)) + 1
        print(f'\n【第 {idx:>{width}} / {count - 1:>{width}} 轮】')


def log_event_candle_generated(log_level: LogLevel,
                               new_merged_candle: MergedCandle
                               ) -> None:
    """
    Log message when a new merged candle was generated.
    
    :param log_level: 
    :param new_merged_candle:
    :return: 
    """
    if log_level.value >= LogLevel.Normal.value:
        print(
            f'\n  ● 生成合并K线：\n    第 {new_merged_candle.id + 1} 根合并K线，'
            f'起始id（普通K线）= {new_merged_candle.left_ordinary_id}，'
            f'周期 = {new_merged_candle.period}，'
            f'high = {new_merged_candle.high}，low = {new_merged_candle.low}。'
        )


def log_event_candle_updated(log_level: LogLevel,
                             merged_candle: MergedCandle
                             ) -> None:
    if log_level.value >= LogLevel.Normal.value:
        print(
            f'\n  ● 修正合并K线：\n    第 {merged_candle.id + 1} 根合并K线，'
            f'起始id（普通K线）= {merged_candle.left_ordinary_id}，'
            f'周期 = {merged_candle.period}，'
            f'high = {merged_candle.high}，low = {merged_candle.low}。'
        )


def log_event_fractal_generated(log_level: LogLevel,
                                new_fractal: Fractal
                                ) -> None:
    if log_level.value >= LogLevel.Normal.value:
        print(
            f'\n  ● 生成分型：\n    第 {new_fractal.id + 1} 个分型，模式 = {new_fractal.pattern.value}，'
            f'位置id（合并K线）= {new_fractal.merged_id}，位置id（普通K线）= {new_fractal.ordinary_id}。'
        )


def log_event_fractal_updated(log_level: LogLevel,
                              old_fractal: Fractal,
                              new_candle: MergedCandle,
                              ) -> None:
    if log_level.value >= LogLevel.Normal.value:
        print(
            f'\n  ● 修正分型：\n    第 {old_fractal.id + 1} 个分型，模式= {old_fractal.pattern.value}，'
            f'位置由（合并K线id）= {old_fractal.merged_id}、（普通K线）= {old_fractal.ordinary_id}，'
            f'修正至（合并K线id）= {new_candle.id}、（普通K线）= {new_candle.ordinary_id}。'
        )


def log_event_fractal_dropped(log_level: LogLevel,
                              element_id: int,
                              pattern: FractalPattern,
                              mc_id: int,
                              oc_id: int
                              ) -> None:
    if log_level.value >= LogLevel.Normal.value:
        print(
            f'\n  ● 丢弃分型：'
            f'\n    第 {element_id} 个分型，模式 = {pattern.value}，'
            f'位置id（合并K线）= {mc_id}，位置id（普通K线）= {oc_id}。'
        )


def log_event_stroke_generated(log_level: LogLevel,
                               new_stroke: Stroke
                               ) -> None:
    if log_level.value >= LogLevel.Normal.value:
        print(
            f'\n  ● 生成笔：\n    第 {new_stroke.id + 1} 个笔，趋势 = {new_stroke.trend}，'
            f'起点（合并K线 id）= {new_stroke.left_merged_id}、'
            f'（普通K线 id）= {new_stroke.left_ordinary_id}，'
            f'终点（合并K线 id）= {new_stroke.right_merged_id}、'
            f'（普通K线 id）= {new_stroke.right_ordinary_id}。'
        )


def log_event_stroke_updated(log_level: LogLevel,
                             old_stroke: Stroke,
                             new_candle: MergedCandle
                             ) -> None:
    if log_level.value >= LogLevel.Normal.value:
        print(
            f'\n  ● 修正笔：\n    第 {old_stroke.id + 1} 个笔，趋势 = {old_stroke.trend}，'
            f'终点由（合并K线id）= {old_stroke.right_merged_id}、'
            f'（普通K线）= {old_stroke.right_ordinary_id}，'
            f'修正至（合并K线id）= {new_candle.id}、（普通K线）= {new_candle.ordinary_id}。'
        )


def log_event_segment_generated(log_level: LogLevel,
                                new_segment: Segment
                                ):
    if log_level.value >= LogLevel.Normal.value:
        print(
            f'\n  ● 生成线段：\n    第 {new_segment.id + 1} 个线段，趋势 = {new_segment.trend}，'
            f'起点id：合并K线 = {new_segment.left_merged_id}，'
            f'普通K线 = {new_segment.left_ordinary_id}，'
            f'终点id：合并K线 = {new_segment.right_merged_id}，'
            f'普通K线 = {new_segment.right_ordinary_id}，'
            f'容纳的笔 = {new_segment.stroke_id_list}。'
        )


def log_event_segment_extended(log_level: LogLevel,
                               element_id: int,
                               trend: Trend,
                               old_mc_id: int,
                               new_mc_id: int,
                               old_oc_id: int,
                               new_oc_id: int
                               ):
    if log_level.value >= LogLevel.Normal.value:
        print(
            f'\n  ● 延伸线段：\n    第 {element_id} 个线段，趋势 = {trend}，'
            f'原终点id（合并K线）= {old_mc_id}，现终点id（合并K线）= {new_mc_id}，'
            f'原终点id（普通K线）= {old_oc_id}，现终点id（普通K线）= {new_oc_id}。'
        )


def log_event_segment_expanded(log_level: LogLevel,
                               element_id: int,
                               trend: Trend,
                               old_mc_id: int,
                               new_mc_id: int,
                               old_oc_id: int,
                               new_oc_id: int,
                               strokes_changed: List[int]
                               ):
    if log_level.value >= LogLevel.Normal.value:
        print(
            f'\n  ● 扩展线段：\n    第 {element_id} 个线段，趋势 = {trend}，'
            f'原终点id（合并K线）= {old_mc_id}，现终点id（合并K线）= {new_mc_id}，'
            f'原终点id（普通K线）= {old_oc_id}，现终点id（普通K线）= {new_oc_id}，'
            f'新增笔 = {strokes_changed}。'
        )


def log_event_isolation_line_generated(log_level: LogLevel,
                                       element_id: int,
                                       mc_id: int,
                                       oc_id: int
                                       ):
    if log_level.value >= LogLevel.Normal.value:
        print(
            f'\n  ● 生成同级别分解线：\n    第 {element_id} 个同级别分解线，'
            f'位置（合并K线） = {mc_id}，位置（普通K线） = {oc_id}。'
        )


def log_event_stroke_pivot_generated(log_level: LogLevel,
                                     element_id: int,
                                     left_mc_id: int,
                                     right_mc_id: int,
                                     left_oc_id: int,
                                     right_oc_id: int,
                                     high: float,
                                     low: float
                                     ):
    if log_level.value >= LogLevel.Normal.value:
        print(
            f'\n  ● 生成笔中枢：\n    第 {element_id} 个笔中枢，'
            f'起点id（合并K线） = {left_mc_id}，终点id（合并K线） = {right_mc_id}，'
            f'起点id（普通K线） = {left_oc_id}，终点id（普通K线） = {right_oc_id}，'
            f'high = {high}，low = {low}。'
        )


def log_event_stroke_pivot_extended(log_level: LogLevel,
                                    element_id: int,
                                    old_oc_id: int,
                                    new_oc_id: int
                                    ):
    if log_level.value >= LogLevel.Normal.value:
        print(
            f'\n  ● 延伸笔中枢：\n    第 {element_id} 个笔中枢，'
            f'原终点id（普通K线） = {old_oc_id}，现终点id（普通K线） = {new_oc_id}。'
        )


def log_try_to_generate_merged_candle(log_level: LogLevel) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print('\n  ○ 尝试生成合并K线：')


def log_try_to_generate_fractal(log_level: LogLevel) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print(f'\n  ○ 尝试生成分型：')


def log_try_to_update_fractal(log_level: LogLevel,
                              last_fractal: Fractal,
                              last_candle: MergedCandle
                              ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print(
            f'\n  ○ 尝试修正分型：'
            f'\n    最新分型 id = {last_fractal.id}，模式 = {last_fractal.pattern.value}，'
            f'极值 = {last_fractal.extreme_price}。'
            f'\n    最新合并K线 id = {last_candle.id}，'
            f'high = {last_candle.high}，low = {last_candle.low}。'
        )


def log_try_to_generate_first_stroke(log_level: LogLevel) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print('\n  ○ 尝试生成笔：')


def log_try_to_generate_stroke(log_level: LogLevel,
                               stroke: Stroke,
                               candle: MergedCandle) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print(
            f'\n  ○ 尝试生成后续笔：'
            f'\n    最新笔 id = {stroke.id}，趋势 = {stroke.trend}，'
            f'右侧 id（合并K线）= {stroke.right_merged_id}，右侧价 = {stroke.right_price}'
            f'\n    最新合并K线 id = {candle.id}，'
            f'最高价 = {candle.high}，最低价 = {candle.low}'
        )


def log_try_to_update_stroke(log_level: LogLevel) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print('\n  ○ 尝试修正笔：')


def log_try_to_generate_segment(log_level: LogLevel) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print('\n  ○ 尝试生成线段：')


def log_try_to_generate_isolation_line(log_level: LogLevel) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print('\n  ○ 尝试生成同级别分解线：')


def log_try_to_generate_stroke_pivot(log_level: LogLevel) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print('\n  ○ 尝试生成笔中枢：')


def log_try_to_generate_segment_pivot(log_level: LogLevel) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print('\n  ○ 尝试生成段中枢：')


def log_show_2_candles(log_level: LogLevel,
                       left_candle: MergedCandle,
                       right_candle: MergedCandle
                       ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print(
            f'    左侧合并K线 id（合并K线）= {left_candle.id}，'
            f'id（普通K线）= {left_candle.ordinary_id}，'
            f'最高价 = {left_candle.high}，最低价 = {left_candle.low}'
        )
        print(
            f'    右侧合并K线 id（合并K线）= {right_candle.id}，'
            f'id（普通K线）= {right_candle.ordinary_id}，'
            f'最高价 = {right_candle.high}，最低价 = {right_candle.low}'
        )


def log_show_3_candles(log_level: LogLevel,
                       left_candle: MergedCandle,
                       middle_candle: MergedCandle,
                       right_candle: MergedCandle
                       ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print(
            f'\n    左侧合并K线 id（合并K线）= {left_candle.id}，'
            f'id（普通K线）= {left_candle.ordinary_id}，'
            f'最高价 = {left_candle.high}，最低价 = {left_candle.low}'
            f'\n    中间合并K线 id（合并K线）= {middle_candle.id}，'
            f'id（普通K线）= {middle_candle.ordinary_id}，'
            f'最高价 = {middle_candle.high}，最低价 = {middle_candle.low}'
            f'\n    右侧合并K线 id（合并K线）= {right_candle.id}，'
            f'id（普通K线）= {right_candle.ordinary_id}，'
            f'最高价 = {right_candle.high}，最低价 = {right_candle.low}'
        )


def log_show_left_side_info_in_generating_stroke(log_level: LogLevel,
                                                 left_candle: Optional[MergedCandle],
                                                 middle_candle: MergedCandle,
                                                 right_candle: MergedCandle
                                                 ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print(f'    左侧：')
        if left_candle is None:
            print(
                f'        合并K线1 id（合并K线）= {middle_candle.id}，'
                f'id（普通K线）= {middle_candle.ordinary_id}，'
                f'最高价 = {middle_candle.high}，最低价 = {middle_candle.low}\n'
                f'        合并K线2 id（合并K线）= {right_candle.id}，'
                f'id（普通K线）= {right_candle.ordinary_id}，'
                f'最高价 = {right_candle.high}，最低价 = {right_candle.low}'
            )
        else:
            print(
                f'        合并K线1 id（合并K线）= {left_candle.id}，'
                f'id（普通K线）= {left_candle.ordinary_id}，'
                f'最高价 = {left_candle.high}，最低价 = {left_candle.low}\n'
                f'        合并K线2 id（合并K线）= {middle_candle.id}，'
                f'id（普通K线）= {middle_candle.ordinary_id}，'
                f'最高价 = {middle_candle.high}，最低价 = {middle_candle.low}\n'
                f'        合并K线3 id（合并K线）= {right_candle.id}，'
                f'id（普通K线）= {right_candle.ordinary_id}，'
                f'最高价 = {right_candle.high}，最低价 = {right_candle.low}'
            )


def log_show_right_side_info_in_generating_stroke(log_level: LogLevel,
                                                  left_candle: MergedCandle,
                                                  middle_candle: MergedCandle,
                                                  fractal_pattern: Optional[FractalPattern]
                                                  ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print(
            f'    右侧：\n'
            f'        最新合并K线 id（合并K线）= {left_candle.id}，'
            f'id（普通K线）= {left_candle.ordinary_id}，'
            f'最高价 = {left_candle.high}，最低价 = {left_candle.low}\n'
            f'        次新合并K线 id（合并K线）= {middle_candle.id}，'
            f'id（普通K线）= {middle_candle.ordinary_id}，'
            f'最高价 = {middle_candle.high}，最低价 = {middle_candle.low}'
        )
        if fractal_pattern is None:
            print(f'        分型不存在。')
        else:
            print(f'        分型 pattern = {fractal_pattern.value}。')


def log_not_enough_merged_candles(log_level: LogLevel,
                                  count: int,
                                  required: int
                                  ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print(f'    合并K线数量不足，仅有 {count} 个，至少需要 {required} 个。')


def log_test_result_distance(log_level: LogLevel,
                             distance: int,
                             minimum_distance: int
                             ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print('      测试是否满足最小距离要求：')
        if distance >= minimum_distance:
            print(
                f'          通过。\n'
                f'              两个分型之间的距离 = {distance}，>= 最小距离要求（{minimum_distance}）。'
            )
        else:
            print(
                f'          不通过。\n'
                f'              两个分型之间的距离 = {distance}，< 最小距离要求（{minimum_distance}）。'
            )


def log_test_result_fractal(log_level: LogLevel,
                            fractal_pattern: Optional[FractalPattern]
                            ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print('      测试是否能够构成分型：')
        if fractal_pattern is None:
            print(
                f'          不通过。\n'
                f'              左侧合并K线不能构成分型。'
            )
        else:
            print(
                f'          通过。\n'
                f'              左侧合并K线可以构成 {fractal_pattern.value}。'
            )


def log_test_result_fractal_pattern(log_level: LogLevel,
                                    left_fractal_pattern: FractalPattern,
                                    right_fractal_pattern: FractalPattern,
                                    ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print('      测试两个分型的类型是否不同：')
        if left_fractal_pattern == right_fractal_pattern:
            print(
                f'          不通过。\n'
                f'              '
                f'左侧分型 {left_fractal_pattern.value}，'
                f'右侧分型 {right_fractal_pattern.value}，'
                f'两者相同。'
            )
        else:
            print(
                f'          通过。\n'
                f'              '
                f'左侧分型 {left_fractal_pattern.value}，'
                f'右侧分型 {right_fractal_pattern.value}，'
                f'两者不同。'
            )


def log_test_result_price_range(log_level: LogLevel,
                                break_high: bool,
                                break_low: bool,
                                candle: MergedCandle
                                ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print('      测试两个分型的类型是否不同：')
        if break_high is False and break_low is False:
            print(
                f'          通过。\n'
                f'              两个分型之间的合并K线均没有超越分型的最高价或者最低价。'
            )
        elif break_high:
            print(
                f'          不通过。\n'
                f'              '
                f'id = {candle.id} 的合并K线，其最高价 = {candle.high}，超越了分型的最高价。'
            )
        elif break_low:
            print(
                f'          不通过。\n'
                f'              '
                f'id = {candle.id} 的合并K线，其最低价 = {candle.low}，超越了分型的最低价。'
            )


def log_test_result_price_break(log_level: LogLevel,
                                stroke: Stroke,
                                candle: MergedCandle
                                ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print('    测试合并K线的价格是否达到或突破笔的右侧价：')
        if stroke.trend == Trend.Bullish:
            if candle.high >= stroke.right_price:
                print(
                    f'        通过。\n'
                    f'            最新合并K线的最高价 >= 最新笔的右侧价。'
                )
            else:
                print(
                    f'        不通过。\n'
                    f'            最新合并K线的最高价 < 最新笔的右侧价。'
                )
        else:
            if candle.low <= stroke.right_price:
                print(
                    f'        通过。\n'
                    f'            最新合并K线的最低价 <= 最新笔的右侧价。'
                )
            else:
                print(
                    f'        不通过。\n'
                    f'            最新合并K线的最低价 > 最新笔的右侧价。'
                )


def log_failed_in_be_the_extreme_price(log_level: LogLevel,
                                       r: RelationshipInNumbers
                                       ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print(
            ' ' * 8,
            f'左侧合并K线的最高价 < {str(r)} 中间合并K线的最高价 {str(r)} 右侧合并K线的最高价，不满足。'
        )


def log_passed_in_pattern_type(log_level: LogLevel,
                               pattern: FractalPattern
                               ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print(' ' * 8, f'新分型的模式 = {pattern}，与前分型不同，满足。')


def log_failed_in_pattern_type(log_level: LogLevel,
                               pattern: FractalPattern
                               ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print(' ' * 8, f'新分型的模式 = {pattern}，与前分型相同，不满足。')


def log_failed_in_price(log_level: LogLevel,
                        r: RelationshipInNumbers
                        ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print(
            ' ' * 8, f'最新合并K线的最高价 {r} 最新笔的右侧价，不满足。'
        )
