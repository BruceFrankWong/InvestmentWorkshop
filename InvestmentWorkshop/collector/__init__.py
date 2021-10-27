# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


# CFFEX
from .cffex import (
    download_cffex_history_data,
    read_cffex_history_data,
)

# SHFE
from .shfe import (
    download_shfe_history_data,
    read_shfe_history_data,
)

# CZCE
from .czce import (
    fetch_czce_history_index,
    download_czce_history_data,
    read_czce_history_data,
)

# DCE
from .dce import (
    fetch_dce_history_index,
    download_dce_history_data,
    download_dce_history_data_all,
    correct_format,
    read_dce_history_data_csv,
    read_dce_history_data_xls,
    read_dce_history_data_xlsx,
    read_dce_history_data,
)

# Utility
from .utility import (
    uncompress_zip_file,
    split_symbol,
    QuoteDaily,
)
