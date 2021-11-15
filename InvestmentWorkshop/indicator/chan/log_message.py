# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


LOG_CANDLE_GENERATED: str = '\n  ● 生成K线：\n    第 {id} 根合并K线，' \
                            '起始id（普通K线）= {ordinary_id}，周期 = {period}，' \
                            'high = {high}，low = {low}。'

LOG_CANDLE_UPDATED: str = '\n  ● 合并K线：\n    第 {id} 根合并K线，' \
                          '起始id（普通K线）= {ordinary_id}，周期 = {period}，' \
                          'high = {high}，low = {low}。'

LOG_FRACTAL_GENERATED: str = '\n  ● 生成分型：\n    第 {id} 个分型，模式 = {pattern}，' \
                             '位置id（合并K线）= {merged_id}，位置id（普通K线）= {ordinary_id}。'

LOG_FRACTAL_DROPPED: str = '\n  ● 丢弃分型：\n    当前合并K线的 {extreme_type}({price}) 达到或超越了' \
                           '第 {id} 个分型（{pattern}）的极值（{extreme_price}），丢弃该分型。'

LOG_STROKE_GENERATED: str = '\n  ● 生成笔：\n    第 {id} 个笔，趋势 = {trend}，' \
                            '起点id（合并K线 ）= {left_mc_id}，终点id（合并K线）= {right_mc_id}，' \
                            '起点id（普通K线 ）= {left_oc_id}，终点id（普通K线）= {right_oc_id}。'

LOG_STROKE_EXTENDED: str = '\n  ● 延伸笔：\n    第 {id} 个笔，趋势 = {trend}，' \
                           '原终点id（合并K线）= {old_mc_id}，现终点id（合并K线）= {new_mc_id}，' \
                           '原终点id（普通K线）= {old_oc_id}，现终点id（普通K线）= {new_oc_id}。'

LOG_SEGMENT_GENERATED: str = '\n  ● 生成线段：\n    第 {id} 个线段，趋势 = {trend}，' \
                             '起点id（合并K线 ）= {left_mc_id}，终点id（合并K线）= {right_mc_id}，' \
                             '起点id（普通K线 ）= {left_oc_id}，终点id（普通K线）= {right_oc_id}，' \
                             '容纳的笔 = {strokes}。'

LOG_SEGMENT_EXTENDED: str = '\n  ● 延伸线段：\n    第 {id} 个线段，趋势 = {trend}，' \
                            '原终点id（合并K线）= {old_mc_id}，现终点id（合并K线）= {new_mc_id}，' \
                            '原终点id（普通K线）= {old_oc_id}，现终点id（普通K线）= {new_oc_id}。'

LOG_SEGMENT_EXPANDED: str = '\n  ● 扩展线段：\n    第 {id} 个线段，趋势 = {trend}，' \
                            '原终点id（合并K线）= {old_mc_id}，现终点id（合并K线）= {new_mc_id}，' \
                            '原终点id（普通K线）= {old_oc_id}，现终点id（普通K线）= {new_oc_id}，' \
                            '新增笔 = {new_strokes}。'

LOG_ISOLATION_LINE_GENERATED: str = '\n  ● 生成同级别分解线：\n    第 {id} 个同级别分解线，' \
                                    '位置（合并K线） = {merged_candle}，' \
                                    '位置（普通K线） = {ordinary_candle}。'

LOG_STROKE_PIVOT_GENERATED: str = '\n  ● 生成笔中枢：\n    第 {id} 个笔中枢，' \
                                  '起点id（普通K线） = {left}，终点id（普通K线） = {right}，' \
                                  'high = {high}，low = {low}。'

LOG_STROKE_PIVOT_EXTENDED: str = '\n  ● 延伸笔中枢：\n    第 {id} 个笔中枢，' \
                                 '原终点id（普通K线） = {old}，现终点id（普通K线） = {new}。'
