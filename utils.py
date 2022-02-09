#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import json
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Union

from colorama import Fore, init
from humanize import precisedelta

init(autoreset=True)
__author__ = 'Buster#5741'
__license__ = 'MIT'
__all__ = (
    'BanEvaluator',
    'FileOp',
    'print_message',
    'file_operation',
    'escape_md',
    'get_difference'
)


class BanEvaluator(ABC):

    @abstractmethod
    def format_to_md(self, filename: Path):
        raise NotImplementedError()


    @abstractmethod
    def get_leaderboard(self):
        raise NotImplementedError()


class FileOp(Enum):
    '''Enumeration for file operations
    '''
    WRITE = 'w'
    READ = 'r'


def print_message(
    message: str,
    start_time: float = None,
    colour: Fore = None
) -> None:
    '''Prints a message with colour and current time to console

    Args:
        message (str): The message you want to print
        start_time (float): Whether it is the result of an action that might've taken a long time,
                            and you want to include the time it took to complete it
        colour (Fore): The colour the message should be
    '''
    m = f'[{datetime.now().strftime("%H:%M:%S")}] '

    if start_time:
        m += Fore.GREEN + f'Finished {message} in {precisedelta(start_time - time.perf_counter(), minimum_unit="microseconds")}'
    else:
        m += colour + message

    print(m)


def file_operation(
    items: Optional[Union[dict, str]] = None,
    filename: Optional[Path] = None,
    op: Optional[FileOp] = FileOp.WRITE
) -> Optional[dict]:
    '''Writes resulting data to file or reads data from file

    Args:
        items (Optional[Union[dict, str]], optional): The data that should be written to the file. Defaults to None.
        filename (Optional[Path], optional): The file to write the data to. Defaults to None.
        op (Optional[FileOp], optional): The file operation. Defaults to FileOp.WRITE.
    Returns:
        Optional[dict]: The file contents in json form
    '''
    with open(filename, op.value, encoding='utf-8') as f:
        if op == FileOp.READ:
            return json.load(f)

        if op == FileOp.WRITE:
            if isinstance(items, dict):
                json.dump(items, f)

            elif isinstance(items, str):
                f.write(items)

    return None


def escape_md(text: str) -> str:
    '''Escapes markdown in a string

    This is used so that clan and player names don't for example
    go italics due to underscores in their names

    Args:
        text: The text to escape markdown in
    Returns:
        str: The text with it's markdown characters escaped using \
    '''
    markdown_regex = fr'(?P<markdown>[_\\~|\*`]|^>(?:>>)?\s|\[.+\]\(.+\))'

    def replacement(match):
        groupdict = match.groupdict()
        is_url = groupdict.get('url')
        if is_url:
            return is_url
        return '\\' + groupdict['markdown']

    return re.sub(markdown_regex, replacement, text, 0, re.MULTILINE)


def get_difference(before: Path, after: Path) -> Dict[str, str]:
    '''Gets the difference between 2 json files by dict keys

    Args:
        before (str, optional): The file to check against
        after (str, optional): The file to check with
    Returns:
        Dict[str, str]: A list of all the removed dicts
    '''
    start_time = time.perf_counter()
    before = file_operation(filename=before, op=FileOp.READ)
    after = file_operation(filename=after, op=FileOp.READ)
    diff = {k: before.get(k) for k in list(set(before.keys()) - set(after.keys()))}

    assert len(diff) > 0 # Assert that there are actually banned people, if not - something went wrong
    print_message('getting banned players', start_time)
    return diff
