# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


def is_inclusive(c_h: float,
                 c_l: float,
                 p_h: float,
                 p_l: float) -> bool:
    """
    判断两根K线是否存在包含关系。两根K线的关系有以下九种：
        1. H1 > H2 & L1 > L2, 非包含，下降。
        2. H1 > H2 & L1 = L2, 包含, K1包含K2, 下降。
        3. H1 > H2 & L1 < L2, 包含。
        4. H1 = H2 & L1 > L2, 包含。
        5. H1 = H2 & L1 = L2, 包含。
        6. H1 = H2 & L1 < L2, 包含。
        7. H1 < H2 & L1 > L2, 包含。
        8. H1 < H2 & L1 = L2, 包含。
        9. H1 < H2 & L1 < L2, 非包含, 。

    :param c_h: float, HIGH price of current candlestick.
    :param c_l: float, LOW price of current candlestick.
    :param p_h: float, HIGH price of previous candlestick.
    :param p_l: float, LOW price of previous candlestick.

    ----
    :return: bool, if
    """
    if (c_h > p_h and c_l > p_l) or (c_h < p_h and c_l < p_l):
        return False
    else:
        return True
