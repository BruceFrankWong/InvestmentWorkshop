# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


import pandas as pd


def macd(df: pd.DataFrame,
         fast: int = 12,
         slow: int = 26,
         signal: int = 9
         ) -> pd.DataFrame:
    """
    Indicator MACD (Moving Average Convergence / Divergence).

    :param df: pandas DataFrame type, the origin data.
    :param fast: int, the period of fast ema.
    :param slow: int, the period of slow ema.
    :param signal: int, the period of signal ema.
    :return: pandas DataFrame type, only indicator data.
    """
    result: pd.DataFrame = pd.DataFrame(
        columns=['diff', 'dea', 'macd'],
        index=df.index
    )
    fast_ema: pd.DataFrame = df['close'].ewm(span=fast, adjust=False).mean()
    slow_ema: pd.DataFrame = df['close'].ewm(span=slow, adjust=False).mean()
    result['diff'] = fast_ema - slow_ema
    result['dea'] = result['diff'].ewm(span=signal, adjust=False).mean()
    result['macd'] = 2 * result['diff'] - result['dea']

    return result
