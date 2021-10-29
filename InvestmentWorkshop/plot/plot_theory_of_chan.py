# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import mplfinance as mpf


def plot_merged_candlestick(df_price: pd.DataFrame,
                            df_merged: pd.DataFrame,
                            file_path: Path,
                            merged_line_width: int = 3,
                            x: int = 32000,
                            y: int = 18000,
                            dpi: int = 72,
                            debug: bool = False):
    """
    绘制合并后的K线。

    :param df_price:
    :param df_merged:
    :param file_path:
    :param merged_line_width:
    :param x:
    :param y:
    :param dpi:
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

    # fig = mpf.figure(style=mpf_style, figsize=(x, y))
    # ax1 = fig.add_subplot(1, 1, 1)
    mpf_config = {}

    fig, ax_list = mpf.plot(
        df_price,
        # ax=ax1,
        # title='AL2111',
        type='candle',
        volume=False,
        show_nontrading=False,
        figsize=(x/dpi, y/dpi),
        figscale=0.9,             # NO effect in External Axes Mode.
        # scale_padding=0.2,
        style=mpf_style,
        fontscale=2,
        tight_layout=True,
        returnfig=True,
        return_width_config=mpf_config,
        warn_too_much_data=1000
    )

    candle_width = mpf_config['candle_width']
    line_width = mpf_config['line_width']

    if debug:
        print(df_price.info())
        print(len(df_price))
        for k, v in mpf_config.items():
            print(k, v)

    # 整理合并元素。
    merged_rectangle = []

    for idx in range(1, min(len(df_price), len(df_merged))):
        if pd.isna(df_merged.iloc[idx].at['合并后周期']):
            break
        if df_merged.iloc[idx].at['合并后周期'] == 1 and df_merged.iloc[idx - 1].at['合并后周期'] > 1:
            x0 = idx - df_merged.iloc[idx - 1].at['合并后周期'] - candle_width / 2
            y0 = df_merged.iloc[idx - 1].at['合并后低点']
            w = df_merged.iloc[idx - 1].at['合并后周期'] - 1 + candle_width
            h = df_merged.iloc[idx - 1].at['合并后高点'] - df_merged.iloc[idx - 1].at['合并后低点']
            merged_rectangle.append(
                Rectangle(
                    xy=(x0, y0),
                    width=w,
                    height=h,
                    angle=0,
                    linewidth=line_width * merged_line_width
                )
            )

    # 生成矩形。
    patch_collection = PatchCollection(
        merged_rectangle,
        edgecolor='black',
        # facecolor='none',
        facecolor='gray',
        alpha=0.6
    )

    ax1 = ax_list[0]
    ax1.add_collection(patch_collection)
    ax1.autoscale_view()

    fig.savefig(file_path, dpi=dpi)

    plt.close(fig)


def plot_merged_candlestick2(df_price: pd.DataFrame,
                             df_merged: pd.DataFrame,
                             file_path: Path,
                             merged_line_width: int = 3,
                             x: int = 32000,
                             y: int = 18000,
                             dpi: int = 72,
                             debug: bool = False):
    """
    绘制合并后的K线。

    :param df_price:
    :param df_merged:
    :param file_path:
    :param merged_line_width:
    :param x:
    :param y:
    :param dpi:
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

    fig = mpf.figure(style=mpf_style, figsize=(x, y))
    ax1 = fig.add_subplot(1, 1, 1)
    mpf_config = {}

    mpf.plot(
        df_price,
        ax=ax1,
        # title='AL2111',
        type='candle',
        volume=False,
        show_nontrading=False,
        # figsize=(x/dpi, y/dpi),
        # figscale=0.9,             # NO effect in External Axes Mode.
        # scale_padding=0.2,
        # style=mpf_style,
        fontscale=1.4,
        tight_layout=True,
        # returnfig=True,
        return_width_config=mpf_config,
        warn_too_much_data=1000
    )

    candle_width = mpf_config['candle_width']
    line_width = mpf_config['line_width']

    if debug:
        print(df_price.info())
        print(len(df_price))
        for k, v in mpf_config.items():
            print(k, v)

    # 整理合并元素。
    merged_rectangle = []

    for idx in range(1, min(len(df_price), len(df_merged))):
        if pd.isna(df_merged.iloc[idx].at['合并后周期']):
            break
        if df_merged.iloc[idx].at['合并后周期'] == 1 and df_merged.iloc[idx - 1].at['合并后周期'] > 1:
            x0 = idx - df_merged.iloc[idx - 1].at['合并后周期'] - candle_width / 2
            y0 = df_merged.iloc[idx - 1].at['合并后低点']
            w = df_merged.iloc[idx - 1].at['合并后周期'] - 1 + candle_width
            h = df_merged.iloc[idx - 1].at['合并后高点'] - df_merged.iloc[idx - 1].at['合并后低点']
            merged_rectangle.append(
                Rectangle(xy=(x0, y0), width=w, height=h, angle=0, linewidth=line_width*merged_line_width)
            )

    # 生成矩形。
    patch_collection = PatchCollection(
        merged_rectangle,
        edgecolor='black',
        facecolor='none'
    )

    ax1.add_collection(patch_collection)
    ax1.autoscale_view()

    fig.savefig(file_path, dpi=dpi)

    plt.close(fig)
