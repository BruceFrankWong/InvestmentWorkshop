# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import mplfinance as mpf


# matplotlib.use('agg')


def plot_merged_candlestick(df_candle: pd.DataFrame,
                            # information: dict
                            ):
    """
    绘制合并后的K线。

    :param df_candle:
    :param chan:
    :param information:
    :param file_path:
    :param merged_line_width:
    :param x:
    :param y:
    :param dpi:
    :param debug:

    ----
    :return:
    """

    # Get current backend.
    backend: str = matplotlib.get_backend()

    # Change backend.
    # plt.switch_backend('qtAgg')

    mpf_color = mpf.make_marketcolors(
        up='red',       # 上涨K线的颜色
        down='green',   # 下跌K线的颜色
        inherit=True
    )

    mpf_style = mpf.make_mpf_style(
        marketcolors=mpf_color,
        figcolor='(0.82, 0.83, 0.85)',      # 设置图表的背景色
        gridcolor='(0.82, 0.83, 0.85)',     # 设置格栅的颜色
        rc={
            'font.family': 'SimHei',        # 指定默认字体：解决plot不能显示中文问题
            'axes.unicode_minus': False,    # 解决保存图像是负号'-'显示为方块的问题
        }
    )

    # 使用mpf.figure()函数可以返回一个figure对象，从而进入External Axes Mode，从而实现对Axes对象和figure对象的自由控制
    figure = mpf.figure(
        style=mpf_style,
        figsize=(32, 24),
        facecolor=(0.82, 0.83, 0.85)
    )

    # 图表设定
    figure_x: float = 0.03
    figure_width: float = 0.90
    figure_height: float = 0.60

    # 添加三个图表，四个数字分别代表图表左下角在figure中的坐标，以及图表的宽（0.88）、高（0.60）
    main_axes = figure.add_axes([figure_x, 0.25, figure_width, figure_height])

    # 添加第二、三张图表时，使用sharex关键字指明与ax1在x轴上对齐，且共用x轴
    ax2 = figure.add_axes([figure_x, 0.15, figure_width, 0.10], sharex=main_axes)
    ax3 = figure.add_axes([figure_x, 0.05, figure_width, 0.10], sharex=main_axes)

    # 设置三张图表的Y轴标签
    # main_axes.set_ylabel('')
    # ax2.set_ylabel('')
    # ax3.set_ylabel('')

    last_data = df_candle.iloc[-1]
    # 在figure对象上添加文本对象，用于显示各种价格和标题
    figure.text(0.50, 0.94, '513100.SH - 纳指ETF:')
    figure.text(0.12, 0.90, '开/收: ')
    figure.text(0.14, 0.89, f'{np.round(last_data["open"], 3)} / {np.round(last_data["close"], 3)}')
    # fig.text(0.14, 0.86, f'{last_data["change"]}')
    # fig.text(0.22, 0.86, f'[{np.round(last_data["pct_change"], 2)}%]')
    # fig.text(0.12, 0.86, f'{last_data.name.date()}')
    figure.text(0.40, 0.90, '高: ')
    figure.text(0.40, 0.90, f'{last_data["high"]}')
    figure.text(0.40, 0.86, '低: ')
    figure.text(0.40, 0.86, f'{last_data["low"]}')
    figure.text(0.55, 0.90, '量(万手): ')
    # fig.text(0.55, 0.90, f'{np.round(last_data["volume"] / 10000, 3)}')
    figure.text(0.55, 0.86, '额(亿元): ')
    # fig.text(0.55, 0.86, f'{last_data["value"]}')
    figure.text(0.70, 0.90, '涨停: ')
    # fig.text(0.70, 0.90, f'{last_data["upper_lim"]}')
    figure.text(0.70, 0.86, '跌停: ')
    # fig.text(0.70, 0.86, f'{last_data["lower_lim"]}')
    figure.text(0.85, 0.90, '均价: ')
    # fig.text(0.85, 0.90, f'{np.round(last_data["average"], 3)}')
    figure.text(0.85, 0.86, '昨收: ')
    # fig.text(0.85, 0.86, f'{last_data["last_close"]}')

    # 调用mpf.plot()函数，注意调用的方式跟上一节不同，这里需要指定ax=ax1，volume=ax2，将K线图显示在ax1中，交易量显示在ax2中
    mpf.plot(
        df_candle,
        ax=main_axes,
        volume=ax2,
        type='candle',
        style=mpf_style,
        ylabel='',
        ylabel_lower='',
        scale_width_adjustment=dict(volume=0.8, candle=1.35),
        warn_too_much_data=800
    )

    # Settings.
    figure_manager = plt.get_current_fig_manager()
    if backend == 'TkAgg':
        figure_manager.set_window_title('InvestmentWorkshop')
    figure_manager.window.state('zoomed')

    # Show plot.
    plt.show()

#     # fig = mpf.figure(style=mpf_style, figsize=(x, y))
#     # ax1 = fig.add_subplot(1, 1, 1)
#     mpf_config = {}
#
#     fig, ax_list = mpf.plot(
#         df_price,
#         # ax=ax1,
#         # title='AL2111',
#         type='candle',
#         volume=False,
#         show_nontrading=False,
#         figsize=(x/dpi, y/dpi),
#         figscale=0.9,             # NO effect in External Axes Mode.
#         # scale_padding=0.2,
#         style=mpf_style,
#         fontscale=2,
#         tight_layout=True,
#         returnfig=True,
#         return_width_config=mpf_config,
#         warn_too_much_data=1000
#     )
#
#     candle_width = mpf_config['candle_width']
#     line_width = mpf_config['line_width']
#
#     if debug:
#         print(df_price.info())
#         print(len(df_price))
#         for k, v in mpf_config.items():
#             print(k, v)
#
#     # 整理合并元素。
#     merged_rectangle = []
#
#     for idx in range(1, min(len(df_price), len(df_merged))):
#         if pd.isna(df_merged.iloc[idx].at['合并后周期']):
#             break
#         if df_merged.iloc[idx].at['合并后周期'] == 1 and df_merged.iloc[idx - 1].at['合并后周期'] > 1:
#             x0 = idx - df_merged.iloc[idx - 1].at['合并后周期'] - candle_width / 2
#             y0 = df_merged.iloc[idx - 1].at['合并后低点']
#             w = df_merged.iloc[idx - 1].at['合并后周期'] - 1 + candle_width
#             h = df_merged.iloc[idx - 1].at['合并后高点'] - df_merged.iloc[idx - 1].at['合并后低点']
#             merged_rectangle.append(
#                 Rectangle(
#                     xy=(x0, y0),
#                     width=w,
#                     height=h,
#                     angle=0,
#                     linewidth=line_width * merged_line_width
#                 )
#             )
#
#     # 生成矩形。
#     patch_collection = PatchCollection(
#         merged_rectangle,
#         edgecolor='black',
#         # facecolor='none',
#         facecolor='gray',
#         alpha=0.6
#     )
#
#     ax1 = ax_list[0]
#     ax1.add_collection(patch_collection)
#     ax1.autoscale_view()
#
#     fig.savefig(file_path, dpi=dpi)
#
#     plt.close(fig)
#
#
# def plot_merged_candlestick2(df_price: pd.DataFrame,
#                              df_merged: pd.DataFrame,
#                              file_path: Path,
#                              merged_line_width: int = 3,
#                              x: int = 32000,
#                              y: int = 18000,
#                              dpi: int = 72,
#                              debug: bool = False):
#     """
#     绘制合并后的K线。
#
#     :param df_price:
#     :param df_merged:
#     :param file_path:
#     :param merged_line_width:
#     :param x:
#     :param y:
#     :param dpi:
#     :param debug:
#
#     ----
#     :return:
#     """
#     mpf_color = mpf.make_marketcolors(
#         up='red',       # 上涨K线的颜色
#         down='green',   # 下跌K线的颜色
#         inherit=True
#     )
#
#     mpf_style = mpf.make_mpf_style(
#         marketcolors=mpf_color,
#         rc={
#             'font.family': 'SimHei',        # 指定默认字体：解决plot不能显示中文问题
#             'axes.unicode_minus': False,    # 解决保存图像是负号'-'显示为方块的问题
#         }
#     )
#
#     fig = mpf.figure(style=mpf_style, figsize=(x, y))
#     ax1 = fig.add_subplot(1, 1, 1)
#     mpf_config = {}
#
#     mpf.plot(
#         df_price,
#         ax=ax1,
#         # title='AL2111',
#         type='candle',
#         volume=False,
#         show_nontrading=False,
#         # figsize=(x/dpi, y/dpi),
#         # figscale=0.9,             # NO effect in External Axes Mode.
#         # scale_padding=0.2,
#         # style=mpf_style,
#         fontscale=1.4,
#         tight_layout=True,
#         # returnfig=True,
#         return_width_config=mpf_config,
#         warn_too_much_data=1000
#     )
#
#     candle_width = mpf_config['candle_width']
#     line_width = mpf_config['line_width']
#
#     if debug:
#         print(df_price.info())
#         print(len(df_price))
#         for k, v in mpf_config.items():
#             print(k, v)
#
#     # 整理合并元素。
#     merged_rectangle = []
#
#     for idx in range(1, min(len(df_price), len(df_merged))):
#         if pd.isna(df_merged.iloc[idx].at['合并后周期']):
#             break
#         if df_merged.iloc[idx].at['合并后周期'] == 1 and df_merged.iloc[idx - 1].at['合并后周期'] > 1:
#             x0 = idx - df_merged.iloc[idx - 1].at['合并后周期'] - candle_width / 2
#             y0 = df_merged.iloc[idx - 1].at['合并后低点']
#             w = df_merged.iloc[idx - 1].at['合并后周期'] - 1 + candle_width
#             h = df_merged.iloc[idx - 1].at['合并后高点'] - df_merged.iloc[idx - 1].at['合并后低点']
#             merged_rectangle.append(
#                 Rectangle(xy=(x0, y0), width=w, height=h, angle=0, linewidth=line_width*merged_line_width)
#             )
#
#     # 生成矩形。
#     patch_collection = PatchCollection(
#         merged_rectangle,
#         edgecolor='black',
#         facecolor='none'
#     )
#
#     ax1.add_collection(patch_collection)
#     ax1.autoscale_view()
#
#     fig.savefig(file_path, dpi=dpi)
#
#     plt.close(fig)
