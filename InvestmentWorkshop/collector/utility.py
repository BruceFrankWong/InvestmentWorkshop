# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Any, Dict, List
from pathlib import Path
import zipfile

from ..utility import CONFIGS


QUOTE = Dict[str, Any]


def make_directory_existed(directory: Path) -> None:
    """
    Make sure <directory> is existed.
    :param directory: a Path-like object.
    :return: None
    """
    if not directory.exists():
        directory.mkdir()


def unzip_file(zip_file: Path) -> List[Path]:
    """
    Unzip a zip file to ten temporary directory defined in <CONFIGS>, and return the unzipped file path.
    :param zip_file:
    :return: a generator.
    """
    result: List[Path] = []
    if not zip_file.exists():
        raise FileNotFoundError('<f> not found.')

    unzip_directory: Path = Path(CONFIGS['path']['temp'])
    make_directory_existed(unzip_directory)

    # Unzip files.
    zip_file = zipfile.ZipFile(zip_file, 'r')
    zip_file.extractall(unzip_directory)

    # Change names with corrected coding.
    unzipped_file: Path
    correct_filename: Path
    for filename in zip_file.namelist():
        unzipped_file = unzip_directory.joinpath(filename)
        correct_filename = unzip_directory.joinpath(filename.encode('CP437').decode('GBK'))
        unzipped_file.rename(correct_filename)
        result.append(correct_filename)

    return result
