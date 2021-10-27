# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


"""

    Chan Theory
    
        Record data with pandas DataFrame, and align with common candlestick DataFrame.

"""


from typing import Dict, List, Tuple, Any
import datetime as dt

import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import mplfinance as mpf

from .utility import is_inclusive


def chan_on_bar_dataframe(df_origin: pd.DataFrame,
                          count: int = None,
                          debug: bool = False) -> pd.DataFrame:
    """
    处理K线合并。

    :param df_origin:
    :param count:
    :param debug:

    ----
    :return:
    """

    def print_debug_before():
        """
        Print information before processing each turn.
        :return:
        """
        print(
            f"第 {idx:>4} / {count:>4} （普通K线）轮：\n"
            f"    前K线（缠论K线）：idx = {idx - 1}, "
            f"高点 = {chan_p1_h}, "
            f"低点 = {chan_p1_l}\n"
            f"    本K线（普通K线）：idx = {idx}, "
            f"高点 = {current_h}, "
            f"低点 = {current_l}\n"
        )

    def print_debug_after():
        """
        Print information after processing each turn.
        :return:
        """
        time_current: dt.datetime = dt.datetime.now()
        if idx_chan_p2_last == -1:
            period_p2 = '不存在'
        else:
            period_p2 = df_chan.loc[idx_chan_p2_last, '缠论周期']

        relation = '包含' if df_chan.loc[idx, '包含？'] else '非'
        print(
            f"    【本轮处理完毕】，费时 {time_current - time_start}。\n\n"
            f"    K线关系：{relation}\n"
            f"    缠论K线数量：{df_chan.loc[idx, '缠论K线数量']}，"
            f"缠论高点：{df_chan.loc[idx, '缠论高点']}，"
            f"缠论低点：{df_chan.loc[idx, '缠论低点']}，\n"
            f"    前1缠论K线：（首根）{idx_chan_p1_first} ～ （末根）{idx_chan_p1_last}，"
            f"周期：{df_chan.loc[idx_chan_p1_last, '缠论周期']}；\n"
            f"    前2缠论K线：（首根）{idx_chan_p2_first} ～ （末根）{idx_chan_p2_last}，"
            f"周期：{period_p2}；\n"
            f"    前3缠论K线：（首根）{idx_chan_p3_first} ～ （末根）{idx_chan_p3_last}。\n"
        )

    def calculate_idx_chan(p1_last: int) -> Tuple[int, int, int, int, int]:
        """
        计算缠论K线与普通K线的 idx 折算。
        :return:
        """
        # 前1缠论K线合并的普通K线，其首根的 idx。
        p1_first: int = p1_last - (df_chan.loc[p1_last, '缠论周期'] - 1)

        # 前2缠论K线合并的普通K线，其末根的 idx。
        p2_last: int = p1_first - 1

        # 前2缠论K线合并的普通K线，其首根的 idx。
        p2_first: int = p2_last - (df_chan.loc[p2_last, '缠论周期'] - 1) if p2_last > -1 else -1

        # 前3缠论K线合并的普通K线，其末根的 idx。
        p3_last: int = p2_first - 1

        # 前3缠论K线合并的普通K线，其末根的 idx。
        p3_first: int = p3_last - (df_chan.loc[p3_last, '缠论周期'] - 1) if p3_last > -1 else -1

        return p1_first, p2_last, p2_first, p3_last, p3_first

    # 计时
    time_start: dt.datetime = dt.datetime.now()

    # ----------------------------------------
    # 检验参数有效性。
    # ----------------------------------------
    assert isinstance(df_origin, pd.DataFrame)
    if count is None or count > len(df_origin):
        count = len(df_origin)

    # ----------------------------------------
    # 声明变量类型。
    # ----------------------------------------
    idx: int
    idx_chan_p1_last: int = 0
    idx_chan_p1_first: int = 0
    idx_chan_p2_last: int = -1
    idx_chan_p2_first: int = -1
    idx_chan_p3_last: int = -1
    idx_chan_p3_first: int = -1

    # ----------------------------------------
    # 转化化 df_origin。
    # ----------------------------------------
    df_data: pd.DataFrame = df_origin.reset_index()

    # ----------------------------------------
    # 初始化 df_chan。
    # ----------------------------------------
    df_chan: pd.DataFrame = pd.DataFrame(
        {
            '包含？': False,
            '缠论K线数量': 1,
            '缠论周期': 1,
            '缠论高点': 0.0,
            '缠论低点': 0.0,
            '分型类型': '-',
            '分型性质': '-',
        },
        index=df_data.index
    )

    df_chan.loc[0, '缠论高点'] = df_data.loc[0, 'high']
    df_chan.loc[0, '缠论低点'] = df_data.loc[0, 'low']

    if debug:
        print(
            f"第 {0:>4} / {count:>4} （普通K线）轮：\n"
            f"    前K线（缠论K线）：idx = {0}, "
            f"高点 = {df_chan.loc[0, '缠论高点']}, "
            f"低点 = {df_chan.loc[0, '缠论低点']}\n"
            f"    本K线（普通K线）：idx = {0}, "
            f"高点 = {df_data.loc[0, 'high']}, "
            f"低点 = {df_data.loc[0, 'low']}\n"
        )

    # ----------------------------------------
    # 常规处理。
    # ----------------------------------------
    for idx in range(1, count):
        # ----------------------------------------
        # 转写变量。
        # ----------------------------------------

        # 本普通K线的高点
        current_h: float = df_data.loc[idx, 'high']

        # 本普通K线的低点
        current_l: float = df_data.loc[idx, 'low']

        # 前1缠论K线的高点
        chan_p1_h: float = df_chan.loc[idx_chan_p1_last, '缠论高点']

        # 前1缠论K线的低点
        chan_p1_l: float = df_chan.loc[idx_chan_p1_last, '缠论低点']

        if debug:
            print_debug_before()

        # ----------------------------------------
        # 如果没有成交/只有一个价位，忽略。
        # ----------------------------------------
        if df_data.loc[idx, 'high'] == df_data.loc[idx, 'low']:
            df_chan.loc[idx, '包含？'] = False

        # ----------------------------------------
        # 处理：普通K线合并为缠论K线。
        # ----------------------------------------

        # 本普通K线与前缠论K线是否存在包含关系？
        df_chan.loc[idx, '包含？'] = is_inclusive(
            current_h,
            current_l,
            chan_p1_h,
            chan_p1_l
        )

        # 如果没有包含：
        if not df_chan.loc[idx, '包含？']:

            # 新的缠论K线，周期 = 1，高点 = 普通K线高点，低点 = 普通K线低点。
            df_chan.loc[idx, '缠论周期'] = 1
            df_chan.loc[idx, '缠论高点'] = df_data.loc[idx, 'high']
            df_chan.loc[idx, '缠论低点'] = df_data.loc[idx, 'low']

            # 缠论K线数量 + 1。
            df_chan.loc[idx, '缠论K线数量'] = df_chan.loc[idx_chan_p1_last, '缠论K线数量'] + 1

            # 前1缠论K线所合并的普通K线，其末根的 idx。
            idx_chan_p1_last = idx
            # 其它缠论K线的特征 idx。
            idx_chan_p1_first, idx_chan_p2_last, idx_chan_p2_first, idx_chan_p3_last, idx_chan_p3_first = \
                calculate_idx_chan(idx_chan_p1_last)

        # 如果存在包含：
        else:
            # 缠论K线数量不变。
            df_chan.loc[idx, '缠论K线数量'] = df_chan.loc[idx_chan_p1_last, '缠论K线数量']

            # 前缠论K线所合并的普通K线，其末根的 idx。
            idx_chan_p1_last += 1

            # 前缠论K线的周期 + 1。
            df_chan.loc[idx, '缠论周期'] = df_chan.loc[idx - 1, '缠论周期'] + 1

            # 前缠论K线所合并的普通K线，其第一根的序号为0（从序号 0 开始的普通K线都被合并了），取前缠论K线和本普通K线的最大范围。
            if idx_chan_p1_first == 0:
                df_chan.loc[idx, '缠论高点'] = max(
                    df_chan.loc[idx - 1, '缠论高点'],
                    df_data.loc[idx, 'high']
                )
                df_chan.loc[idx, '缠论低点'] = min(
                    df_chan.loc[idx - 1, '缠论低点'],
                    df_data.loc[idx, 'low']
                )
            # 前缠论K线不是第一根缠论K线，判断前缠论K线和前前缠论K线的方向。
            else:
                # 前2缠论K线的高低点
                chan_p2_h = df_chan.loc[idx_chan_p2_last, '缠论高点']
                chan_p2_l = df_chan.loc[idx_chan_p2_last, '缠论低点']

                if (
                    (chan_p1_h > chan_p2_h and chan_p1_l <= chan_p2_l) or
                    (chan_p1_h < chan_p2_h and chan_p1_l >= chan_p2_l)
                ):
                    r_h = '>' if chan_p1_h > chan_p2_h else '<'
                    r_l = '>' if chan_p1_l > chan_p2_l else '<'

                    print(
                        f'【ERROR】在合并K线时发生错误——未知的前K与前前K高低关系。\n'
                        f'前1高：{chan_p1_h}，前2高：{chan_p2_h}，{r_h}；\n'
                        f'前1低：{chan_p1_l}，前2低：{chan_p2_l}，{r_l}。'
                    )
                # 前1缠论K线的高点 > 前2缠论K线的高点，合并取 高-高。
                elif chan_p1_h > chan_p2_h and chan_p1_l > chan_p2_l:
                    df_chan.loc[idx, '缠论高点'] = max(
                        df_chan.loc[idx - 1, '缠论高点'],
                        df_data.loc[idx, 'high']
                    )
                    df_chan.loc[idx, '缠论低点'] = max(
                        df_chan.loc[idx - 1, '缠论低点'],
                        df_data.loc[idx, 'low']
                    )
                # 前1缠论K线的低点 < 前2缠论K线的低点，合并取 低-低。
                # elif chan_p1_h < chan_p2_h and chan_p1_l < chan_p2_l:
                else:
                    df_chan.loc[idx, '缠论高点'] = min(
                        df_chan.loc[idx - 1, '缠论高点'],
                        df_data.loc[idx, 'high']
                    )
                    df_chan.loc[idx, '缠论低点'] = min(
                        df_chan.loc[idx - 1, '缠论低点'],
                        df_data.loc[idx, 'low']
                    )

        # ----------------------------------------
        # 处理：分型。
        # ----------------------------------------

        # 如果缠论K线数量 == 2，作为跳开处理。
        if df_chan.loc[idx, '缠论K线数量'] == 2:
            if debug:
                print(f'    处理分型（缠论K线数量=2）：')
            if df_chan.loc[idx_chan_p2_last, '缠论高点'] > df_chan.loc[idx_chan_p1_last, '缠论高点']:
                df_chan.loc[idx_chan_p2_last, '分型类型'] = '顶'
                df_chan.loc[idx_chan_p2_last, '分型性质'] = '临时'
                if debug:
                    print(f"        前2缠论K线视作【顶分型】。\n")
            elif df_chan.loc[idx_chan_p2_last, '缠论低点'] < df_chan.loc[idx_chan_p1_last, '缠论低点']:
                df_chan.loc[idx_chan_p2_last, '分型类型'] = '底'
                df_chan.loc[idx_chan_p2_last, '分型性质'] = '临时'
                if debug:
                    print(f"        前2缠论K线视作【底分型】。\n")
            else:
                pass

        # 如果缠论K线数量 > 2，正常处理。
        elif df_chan.loc[idx, '缠论K线数量'] > 2:
            if debug:
                print(f'    处理分型（缠论K线数量>2）：')
            if df_chan.loc[idx_chan_p2_last, '缠论高点'] == max(
                    df_chan.loc[idx_chan_p1_last, '缠论高点'],
                    df_chan.loc[idx_chan_p2_last, '缠论高点'],
                    df_chan.loc[idx_chan_p3_last, '缠论高点']
            ):
                df_chan.loc[idx_chan_p2_last, '分型类型'] = '顶'
                df_chan.loc[idx_chan_p2_last, '分型性质'] = '临时'
                if debug:
                    print(f"        前2缠论K线视作【顶分型】。\n")
            elif df_chan.loc[idx_chan_p2_last, '缠论低点'] == min(
                    df_chan.loc[idx_chan_p1_last, '缠论低点'],
                    df_chan.loc[idx_chan_p2_last, '缠论低点'],
                    df_chan.loc[idx_chan_p3_last, '缠论低点']
            ):
                df_chan.loc[idx_chan_p2_last, '分型类型'] = '底'
                df_chan.loc[idx_chan_p2_last, '分型性质'] = '临时'
                if debug:
                    print(f"        前2缠论K线视作【底分型】。\n")
            else:
                pass

        # 如果缠论K线数量 == 1，不做处理。
        else:
            if debug:
                print(f'    处理分型（缠论K线数量<2）：略过。\n')

        # ----------------------------------------
        # 打印 debug 信息。
        # ----------------------------------------
        if debug:
            print_debug_after()

    time_end: dt.datetime = dt.datetime.now()

    if debug:
        print(f'\n计算完成！\n总计花费： {time_end - time_start}')

    return df_chan


def plot_chan_dataframe(df_origin: pd.DataFrame,
                        df_chan: pd.DataFrame,
                        count: int,
                        merged_line_width: int = 3,
                        debug: bool = False):
    """
    绘制合并后的K线。

    :param df_origin:
    :param df_chan:
    :param count:
    :param merged_line_width:
    :param debug:

    ----
    :return:
    """
    mpf_color = mpf.make_marketcolors(
        up='red',       # 上涨K线的颜色
        down='green',   # 下跌K线的颜色
        inherit=True
    )

    mpf_style = mpf.make_mpf_style(
        marketcolors=mpf_color,
        rc={
            'font.family': 'SimHei',        # 指定默认字体：解决plot不能显示中文问题
            'axes.unicode_minus': False,    # 解决保存图像是负号'-'显示为方块的问题
        }
    )

    mpf_config = {}

    fig, ax_list = mpf.plot(
        df_origin.iloc[:count],
        title='AL2111',
        type='candle',
        volume=False,
        show_nontrading=False,
        figratio=(40, 20),
        figscale=2,
        style=mpf_style,
        tight_layout=True,
        returnfig=True,
        return_width_config=mpf_config,
        warn_too_much_data=1000
    )

    candle_width = mpf_config['candle_width']
    line_width = mpf_config['line_width']

    if debug:
        for k, v in mpf_config.items():
            print(k, v)

    # 整理合并元素。
    merged_rectangle = []

    for idx in range(1, count):
        if pd.isna(df_chan.iloc[idx].at['缠论周期']):
            break
        if df_chan.iloc[idx].at['缠论周期'] == 1 and df_chan.iloc[idx - 1].at['缠论周期'] > 1:
            x0 = idx - df_chan.iloc[idx - 1].at['缠论周期'] - candle_width / 2
            y0 = df_chan.iloc[idx - 1].at['缠论低点']
            w = df_chan.iloc[idx - 1].at['缠论周期'] - 1 + candle_width
            h = df_chan.iloc[idx - 1].at['缠论高点'] - df_chan.iloc[idx - 1].at['缠论低点']
            merged_rectangle.append(
                Rectangle(xy=(x0, y0), width=w, height=h, angle=0, linewidth=line_width*merged_line_width)
            )

    # 生成矩形。
    patch_collection = PatchCollection(
        merged_rectangle,
        edgecolor='black',
        facecolor='none'
    )

    ax1 = ax_list[0]
    ax1.add_collection(patch_collection)
    ax1.autoscale_view()

    print('Done.')
