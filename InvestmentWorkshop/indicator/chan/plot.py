# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import List, Tuple

import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import mplfinance as mpf

from .definition import (
    MergedCandle,
    FractalPattern,
    Fractal,
    Stroke,
    Segment,
    ChanTheory
)


def get_plot_style():
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
    return mpf_style


def plot_chan_theory(df: pd.DataFrame,
                     chan: ChanTheory,
                     count: int,
                     title: str = '',
                     tight_layout: bool = False,
                     show_ordinary_id: bool = False,
                     show_merged_id: bool = False,
                     merged_candle_edge_width: int = 3,
                     show_all_merged: bool = False,
                     hatch_merged: bool = False,
                     fractal_marker_size: int = 100,
                     fractal_marker_offset: int = 50,
                     debug: bool = False):
    """
    绘制合并后的K线。

    :param df:
    :param chan:
    :param count:
    :param title:
    :param tight_layout:
    :param show_ordinary_id:
    :param show_merged_id:
    :param merged_candle_edge_width:
    :param show_all_merged:
    :param hatch_merged:
    :param fractal_marker_size:
    :param fractal_marker_offset:
    :param debug:

    ----
    :return:
    """

    style = get_plot_style()

    # 最大日期
    max_date = df.index[count]
    print(max_date)

    # 附加元素
    additional_plot: list = []

    # 分型 和 笔
    fractal: Fractal
    fractal_t: list = []
    fractal_b: list = []
    idx_fractal_to_ordinary: int
    idx_ordinary_candle: int = 0

    for i in range(chan.fractals_count):
        fractal = chan.fractals[i]

        for j in range(idx_ordinary_candle, fractal.ordinary_id):
            fractal_t.append(np.nan)
            fractal_b.append(np.nan)
        if fractal.pattern == FractalPattern.Top:
            fractal_t.append(fractal.middle_candle.high + fractal_marker_offset)
            fractal_b.append(np.nan)
        if fractal.pattern == FractalPattern.Bottom:
            fractal_t.append(np.nan)
            fractal_b.append(fractal.middle_candle.low - fractal_marker_offset)
        idx_ordinary_candle = fractal.ordinary_id + 1
    for i in range(idx_ordinary_candle, count):
        fractal_t.append(np.nan)
        fractal_b.append(np.nan)

    additional_plot.append(
        mpf.make_addplot(fractal_t, type='scatter', markersize=fractal_marker_size, marker='v')
    )
    additional_plot.append(
        mpf.make_addplot(fractal_b, type='scatter', markersize=fractal_marker_size, marker='^')
    )

    # 笔
    plot_stroke: List[Tuple[str, float]] = []
    stroke: Stroke
    if chan.strokes_count > 0:

        for stroke in chan.strokes:
            if df.index[stroke.left_ordinary_id] > max_date:
                break
            plot_stroke.append(
                (
                    df.index[stroke.left_ordinary_id],
                    stroke.left_price
                )
            )
            # print(stroke.id, stroke.left_candle)
        # plot_stroke.append(
        #     (
        #         df.index[chan.strokes[-1].right_ordinary_id],
        #         chan.strokes[-1].right_price
        #     )
        # )

    # 线段
    segment: Segment
    plot_segment: List[Tuple[str, float]] = []
    # if chan.segments_count > 0:
    #     for segment in chan.segments:
    #         if df.index[segment.left_ordinary_id] >= max_date:
    #             break
    #         plot_segment.append(
    #             (
    #                 df.index[segment.left_ordinary_id],
    #                 segment.left_price
    #             )
    #         )
    #     # plot_segment.append(
    #     #     (
    #     #         df.index[chan.segments[-1].right_ordinary_id],
    #     #         chan.segments[-1].right_price
    #     #     )
    #     # )

    # 线
    al = plot_stroke if len(plot_segment) == 0 else [plot_stroke, plot_segment]
    co = 'k' if len(plot_segment) == 0 else ['k', 'r']

    # mplfinance 的配置
    mpf_config = {}

    fig, ax_list = mpf.plot(
        df.iloc[:count],
        title=title,
        type='candle',
        volume=False,
        addplot=additional_plot,
        alines=dict(alines=al,
                    colors=co,
                    linestyle='--',
                    linewidths=0.05
                    ),
        show_nontrading=False,
        figratio=(40, 20),
        figscale=2,
        style=style,
        ylabel='',
        tight_layout=tight_layout,
        returnfig=True,
        return_width_config=mpf_config,
        warn_too_much_data=1000
    )

    candle_width = mpf_config['candle_width']
    line_width = mpf_config['line_width']

    if debug:
        for k, v in mpf_config.items():
            print(k, v)

    # 额外的元素。
    patches = []

    # 生成合并K线元素。
    for idx in range(chan.merged_candles_count):
        candle = chan.merged_candles[idx]

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

        for i in range(chan.merged_candles_count):
            candle = chan.merged_candles[i]
            idx_chan_x.append(candle.right_ordinary_id - candle_width / 2)
            idx_chan_y.append(candle.high + 14)
            idx_chan_value.append(str(chan.merged_candles.index(candle)))

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


def plot_pure_merged_candle(merged_candle_list: List[MergedCandle],
                            count: int):
    style = get_plot_style()

    df: pd.DataFrame = pd.DataFrame(
        {
            'open': 0.0,
            'high': 0.0,
            'low': 0.0,
            'close': 0.0,
        },
        index=pd.Series(
            range(
                min(
                    len(merged_candle_list),
                    count
                )
            )
        )
    )
    for idx in range(len(merged_candle_list)):
        df.iloc[idx].at['open'] = merged_candle_list[idx].low
        df.iloc[idx].at['low'] = merged_candle_list[idx].low
        df.iloc[idx].at['high'] = merged_candle_list[idx].high
        df.iloc[idx].at['close'] = merged_candle_list[idx].high

    mpf.plot(
        df,
        type='candle',
        volume=False,
        show_nontrading=False,
        figratio=(40, 20),
        figscale=2,
        style=style,
        warn_too_much_data=1000
    )
