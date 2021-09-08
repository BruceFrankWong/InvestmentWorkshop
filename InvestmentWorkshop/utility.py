# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Dict, Any
from pathlib import Path
import json


__all__ = ['PACKAGE_NAME', 'PACKAGE_PATH', 'CONFIG_PATH', 'CONFIGS']


def load_json(json_file: Path) -> dict:
    """
    Load a json file.
    :param json_file: a Path-like object.
    :return: a dict.
    """
    with open(json_file, mode='r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def save_json(data: dict, json_file: Path) -> None:
    """
    Save a dict object as json file.
    :param data: a dict object.
    :param json_file: a Path-like object.
    :return: None
    """
    with open(json_file, mode='w+', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def create_default_config() -> None:
    """
    Create a default config file in <CONFIG_PATH>.
    :return: None
    """
    default_config: Dict[str, Any] = {
        'path': {
            'temp': str(PACKAGE_PATH.joinpath('temp')),
            'download': str(PACKAGE_PATH.joinpath('downloaded')),
            'picture': str(PACKAGE_PATH.joinpath('picture')),
        },
        'http_header': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/avif,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.114 Safari/537.36',
        },
        'database': {
            'driver': 'PostgreSQL',
            'host': '127.0.0.1',
            'port': '5432',
            'database': 'investment',
            'user': 'user',
            'password': 'password',
        },
        'TQ': {
            'account': 'TQ_ACCOUNT',
            'password': 'TQ_PASSWORD',
        },
        'SSIC': {
            'access_key': 'SSIC_KEY',
            'access_secret': 'SSIC_SECRET',
        }
    }
    save_json(default_config, config_file)


# The package name.
PACKAGE_NAME: str = 'InvestmentWorkshop'


# The package path <InvestmentWorkshop>
PACKAGE_PATH: Path = Path(__file__).parent


# Tha path of the user custom config file.
CONFIG_PATH: Path = Path.home().joinpath(f'.{PACKAGE_NAME}')
if not CONFIG_PATH.exists():
    CONFIG_PATH.mkdir()


# Load <CONFIGS> from file.
config_file: Path = CONFIG_PATH.joinpath('config.json')
if not config_file.exists():
    create_default_config()
    print(
        f'Configure not found, and a default one is created in <{CONFIG_PATH}>. Modify it as your real config.'
    )
CONFIGS: Dict[str, Any] = load_json(config_file)
