# -*- coding: UTF-8 -*-

__author__ = 'Bruce Frank Wong'


from typing import Any, Dict, List
from pathlib import Path
import zipfile


QUOTE = Dict[str, Any]


def make_directory_existed(directory: Path) -> None:
    """
    Make sure <directory> is existed.
    :param directory: a Path-like object.
    :return: None
    """
    if not directory.exists():
        directory.mkdir()


def unzip_quote_file(quote_zip: Path) -> List[Path]:
    """
    Unzip a zip file to a directory, and return the unzipped file path.
    :param quote_zip:
    :return: a generator.
    """
    result: List[Path] = []
    if not quote_zip.exists():
        raise FileNotFoundError('<f> not found.')

    unzip_directory: Path = quote_zip.parent.joinpath('unzip')
    make_directory_existed(unzip_directory)

    # Unzip files.
    zip_file = zipfile.ZipFile(quote_zip, 'r')
    zip_file.extractall(unzip_directory)

    # Change names with corrected coding.
    unzip_file: Path
    correct_filename: Path
    for filename in zip_file.namelist():
        unzip_file = unzip_directory.joinpath(filename)
        correct_filename = unzip_directory.joinpath(filename.encode('CP437').decode('GBK'))
        unzip_file.rename(correct_filename)
        result.append(correct_filename)

    return result
