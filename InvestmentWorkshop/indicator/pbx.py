# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Sequence

import pandas as pd


def pbx(df: pd.DataFrame, parameters: Sequence[int] = (4, 6, 24)) -> pd.DataFrame:
    """
    Indicator PBX.

    :param df: pandas DataFrame type, the origin data.
    :param parameters: sequence of int, the period of PBX.
                       Default value is (4, 6, 24).
    :return: pandas DataFrame type, only indicator data.
    """
    result: pd.DataFrame = pd.DataFrame(
        columns=[f'pbx{str(period)}' for period in parameters],
        index=df.index
    )

    for period in parameters:
        result[f'pbx{str(period)}'] = (
            df['close'].ewm(span=period, adjust=False).mean() +
            df['close'].rolling(period * 2).mean() +
            df['close'].rolling(period * 4).mean()
        ) / 3
    return result
