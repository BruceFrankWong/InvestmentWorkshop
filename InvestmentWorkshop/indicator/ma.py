# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Sequence

import pandas as pd


def ma(df: pd.DataFrame, parameters: Sequence[int] = (5, 10, 20, 60, 120)) -> pd.DataFrame:
    """
    Indicator MA (Moving Average).

    :param df: pandas DataFrame type, the origin data.
    :param parameters: sequence of int, the period of MA.
                       Default value is (5, 10, 20, 60, 120).
    :return: pandas DataFrame type, only indicator data.
    """
    result: pd.DataFrame = pd.DataFrame(
        columns=[f'pbx{str(period)}' for period in parameters],
        index=df.index
    )
    for period in parameters:
        result[f'ma{str(period)}'] = df['close'].rolling(period, min_periods=5).mean()
    return result


def ema(df: pd.DataFrame, parameters: Sequence[int]) -> pd.DataFrame:
    result: pd.DataFrame = pd.DataFrame(
        columns=[f'ema{str(parameter)}' for parameter in parameters],
        index=df.index
    )

    for period in parameters:
        result[f'ema{str(period)}'] = pd.ewma(df['close'], span=ma)
    return result
