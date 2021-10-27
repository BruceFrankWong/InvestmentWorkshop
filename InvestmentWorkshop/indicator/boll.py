# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import pandas as pd


def boll(df: pd.DataFrame, n: int, m: int) -> pd.DataFrame:
    """
    Indicator BOLL.

    :param df: pandas DataFrame type, the origin data.
    :param n:
    :param m:

    :return: pandas DataFrame type, only indicator data.
    """
    result: pd.DataFrame = pd.DataFrame(
        columns=['std', 'median', 'upper', 'lower'],
        index=df.index
    )
    # 标准差
    result['std'] = df['close'].rolling(n, min_periods=1).std(ddof=0)
    # 中轨
    result['median'] = df['close'].rolling(n, min_periods=1).mean()
    # 上下轨
    result['upper'] = result['median'] + result['std'] * m
    result['lower'] = result['median'] - result['std'] * m
    return result
