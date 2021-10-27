# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


"""

    Chan Theory
    
        Record data with object, not pandas.DataFrame.

"""


from typing import Dict, List, Tuple, Any
import datetime as dt

import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import mplfinance as mpf

from .utility import is_inclusive


def is_fractal(chan_k0: Dict[str, Any],
               chan_k1: Dict[str, Any],
               chan_k2: Dict[str, Any]) -> int:
    if chan_k0['low'] > chan_k1['low'] and chan_k2['low'] > chan_k1['low']:
        return -1
    elif chan_k0['high'] < chan_k1['high'] and chan_k2['high'] < chan_k1['high']:
        return 1
    else:
        return 0


def chan_on_bar(df_source: pd.DataFrame,
                start: int = None,
                end: int = None,
                debug: bool = False
                ):
    """

    :param df_source:
    :param start:
    :param end:
    :param debug:
    :return:
    """

    chan_candlestick: List[Dict[str, Any]] = []
    chan_fractal: List[Dict[str, Any]] = []
    df_chan_stroke: pd.DataFrame = pd.DataFrame(columns=['index_chan', 'trend'])

    # Declare variable type.
    idx_source: int             # 普通K线（时间序列）的序号
    idx_candlestick: int = 0    # 缠论K线的序号
    idx_fractal: int = -1       # 缠论分型的序号
    current_high: float
    current_low: float

    # Initial.
    chan_candlestick.append(
        {
            'index_data': 0,
            'period': 1,
            'high': df_source.iloc[0].at['high'],
            'low': df_source.iloc[0].at['low'],
        }
    )
    if debug:
        print(
            f"第 0 根普通K线： "
            f"H={df_source.iloc[0].at['high']}, "
            f"L={df_source.iloc[0].at['low']}； "
            f"前缠论K线： 序号={idx_candlestick}, "
            f"周期={chan_candlestick[idx_candlestick]['period']}, "
            f"H={chan_candlestick[idx_candlestick]['high']}, "
            f"L={chan_candlestick[idx_candlestick]['low']}"
        )

    # Loop.
    for idx_source in range(1, len(df_source)):
        current_high = df_source.iloc[idx_source].at['high']
        current_low = df_source.iloc[idx_source].at['low']
        previous_high = chan_candlestick[idx_candlestick]['high']
        previous_low = chan_candlestick[idx_candlestick]['low']

        if debug:
            print(
                f'第 {idx_source} 根普通K线： '
                f'H={current_high}, '
                f'L={current_low}； '
                f"前缠论K线： 序号={idx_candlestick}, "
                f"周期={chan_candlestick[idx_candlestick]['period']}, "
                f'H={previous_high}, '
                f'L={previous_low}'
            )

        # ----------------------------------------
        # Merge candlestick.
        # ----------------------------------------

        # 如果存在包含关系：
        if is_inclusive(current_high, current_low, previous_high, previous_low):
            if debug:
                print('\t包含')

            # 本缠论K线的周期 + 1。
            chan_candlestick[idx_candlestick]['period'] += 1

            # 如果这是第1根缠论K线，无法向前搜索2根，直接取最大区间合并。
            if idx_candlestick == 0:
                chan_candlestick[idx_candlestick]['high'] = max(current_high, previous_high)
                chan_candlestick[idx_candlestick]['low'] = min(current_low, previous_low)

            # 如果 本缠论K线的高点 > 前缠论K线的高点，那么 向上合并，取 高-高：
            elif chan_candlestick[idx_candlestick]['high'] > chan_candlestick[idx_candlestick-1]['high']:
                chan_candlestick[idx_candlestick]['high'] = max(current_high, previous_high)
                chan_candlestick[idx_candlestick]['low'] = max(current_low, previous_low)

            # 如果 本缠论K线的低点 < 前缠论K线的低点，那么 向下合并，取 低-低：
            elif chan_candlestick[idx_candlestick]['low'] < chan_candlestick[idx_candlestick-1]['low']:
                chan_candlestick[idx_candlestick]['high'] = min(current_high, previous_high)
                chan_candlestick[idx_candlestick]['low'] = min(current_low, previous_low)

            # 其它情况，出错？
            else:
                print(f'ERROR! idx_source = {idx_source}, idx_candlestick = {idx_candlestick}')

        # 如果不存在包含关系：
        else:
            if debug:
                print('\t否')

            # 缠论K线的序号 + 1。
            idx_candlestick += 1

            # 新的缠论K线。
            chan_candlestick.append(
                {
                    'index_data': idx_source,
                    'period': 1,
                    'high': current_high,
                    'low': current_low,
                }
            )

        # ----------------------------------------
        # Fractal.
        # ----------------------------------------

        if idx_candlestick >= 2:
            # 如果不存在包含关系，检查是否有分型。
            if not is_inclusive(current_high, current_low, previous_high, previous_low):
                result = is_fractal(
                    chan_candlestick[idx_candlestick],
                    chan_candlestick[idx_candlestick-1],
                    chan_candlestick[idx_candlestick-2],
                )

                # 存在分型：
                if result != 0:
                    # 如果这是第1根缠论分型，直接加入。
                    if idx_fractal == -1:
                        idx_fractal += 1
                        chan_fractal.append(
                            {
                                'idx_candlestick': idx_candlestick - 1,
                                'type': result,
                            }
                        )
                    # 如果距离前一个分型够远，新增分型。
                    if idx_candlestick - chan_fractal[idx_fractal]['idx_candlestick'] >= 4:
                        idx_fractal += 1
                        chan_fractal.append(
                            {
                                'idx_candlestick': idx_candlestick - 1,
                                'type': result,
                            }
                        )
                    # 如果距离前一个分型不够远：
                    else:
                        # 如果与前一个分型同类型，修正：放弃前分型，用现在的。
                        if result == chan_fractal[idx_fractal]:
                            chan_fractal[idx_fractal]['idx_candlestick'] = idx_candlestick - 1

    return pd.DataFrame(chan_candlestick), pd.DataFrame(chan_fractal)


def plot_chan(df_data: pd.DataFrame,
              df_chan: pd.DataFrame,
              df_fractal: pd.DataFrame,
              merged_line_width: int = 3,
              debug: bool = False):
    """
    绘制合并后的K线。

    :param df_data:
    :param df_chan:
    :param df_fractal:
    :param merged_line_width:
    :param debug:

    ----
    :return:
    """
    mpf_color = mpf.make_marketcolors(
        up='red',  # 上涨K线的颜色
        down='green',  # 下跌K线的颜色
        inherit=True
    )

    mpf_style = mpf.make_mpf_style(
        marketcolors=mpf_color,
        rc={
            'font.family': 'SimHei',  # 指定默认字体：解决plot不能显示中文问题
            'axes.unicode_minus': False,  # 解决保存图像是负号'-'显示为方块的问题
        }
    )

    # --------------------
    # 缠论的分型
    # --------------------

    fractal_b = [np.nan for _, _ in df_data.iteritems()]
    fractal_t = [np.nan for _, _ in df_data.iteritems()]

    def fractal_b(percentB, price) -> list:
        """
        底分型。
        """
        signal = []
        previous = -1.0
        for date, value in percentB.iteritems():
            if value < 0 and previous >= 0:
                signal.append(price[date] * 0.99)
            else:
                signal.append(np.nan)
            previous = value
        return signal

    for idx, val in df_fractal.iteritems():
        data_index = df_data.index[int(df_chan.iloc[val['idx_candlestick']].at['index_data'])]
        if val['type'] == 1:
            price = df_chan.iloc[val['idx_candlestick']].at['high']
            fractal_t[data_index] = price * 1.1
        elif val['type'] == -1:
            price = df_chan.iloc[val['idx_candlestick']].at['low']
            fractal_t[data_index] = price * 0.9

    fractal = [
        mpf.make_addplot(fractal_b, type='scatter', markersize=200, marker='^'),
        mpf.make_addplot(fractal_t, type='scatter', markersize=200, marker='V'),
    ]

    mpf_config = {}

    fig, ax_list = mpf.plot(
        df_data,
        title='AL2111',
        type='candle',
        addplot=fractal,
        volume=False,
        show_nontrading=False,
        figratio=(800, 300),
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

    for idx, val in df_chan.iterrows():
        x0 = val['index_data'] - candle_width / 2
        y0 = val['low']
        w = val['period'] - 1 + candle_width
        h = val['high'] - val['low']
        merged_rectangle.append(
            Rectangle(xy=(x0, y0), width=w, height=h, angle=0, linewidth=line_width * merged_line_width)
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
