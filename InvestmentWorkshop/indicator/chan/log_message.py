# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List

from .definition import (
    LogLevel,
    RelationshipInNumbers,
    Trend,
    FractalPattern,

    MergedCandle,
    Fractal,
    Stroke,
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
            f'\n  ● 生成笔：\n    第 {new_stroke.id} 个笔，趋势 = {new_stroke.trend}，'
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
            f'\n  ● 修正笔：\n    第 {old_stroke.id} 个笔，趋势 = {old_stroke.trend}，'
            f'位置由（合并K线id）= {old_stroke.right_merged_id}、'
            f'（普通K线）= {old_stroke.right_ordinary_id}，'
            f'修正至（合并K线id）= {new_candle.id}、（普通K线）= {new_candle.ordinary_id}。'
        )


def log_event_segment_generated(log_level: LogLevel,
                                element_id: int,
                                trend: Trend,
                                left_mc_id: int,
                                right_mc_id: int,
                                left_oc_id: int,
                                right_oc_id: int,
                                strokes: List[int]
                                ):
    if log_level.value >= LogLevel.Normal.value:
        print(
            f'\n  ● 生成线段：\n    第 {element_id} 个线段，趋势 = {trend}，'
            f'起点id（合并K线 ）= {left_mc_id}，终点id（合并K线）= {right_mc_id}，'
            f'起点id（普通K线 ）= {left_oc_id}，终点id（普通K线）= {right_oc_id}，'
            f'容纳的笔 = {strokes}。'
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


def log_try_to_generate_stroke(log_level: LogLevel) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print('\n  ○ 尝试生成笔：')


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


def log_show_candles(log_level: LogLevel,
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


def log_failed_in_not_enough_merged_candles(log_level: LogLevel,
                                            count: int
                                            ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print(f'\n    合并K线数量不足，仅有 {count} 个，至少需要 3 个。')


def log_passed_in_enough_distance(log_level: LogLevel,
                                  distance: int,
                                  minimum_distance: int
                                  ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print(' ' * 8, f'新老分型的距离 = {distance}，>= {minimum_distance}，满足。')


def log_failed_in_enough_distance(log_level: LogLevel,
                                  distance: int,
                                  minimum_distance: int
                                  ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print(' ' * 8, f'新老分型的距离 = {distance}，< {minimum_distance}，不满足。')


def _log_determine_fractal_passed(log_level: LogLevel,
                                  r: RelationshipInNumbers
                                  ) -> None:
    if log_level.value >= LogLevel.Detailed.value:
        print(' ' * 8, f'中间合并K线的最高价 {str(r)} 左右两侧合并K线的最高价，满足。')


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
