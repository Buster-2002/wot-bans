#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import json
import os
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Union

import requests
from colorama import Fore, init
from dotenv import load_dotenv
from humanize import precisedelta

load_dotenv()
init(autoreset=True)
__author__ = 'Buster#5741'
__license__ = 'MIT'
__all__ = (
    # Classes
    'BanEvaluator',
    'FileOp',
    'Region',

    # Functions
    'print_message',
    'file_operation',
    'escape_md',
    'get_difference',
    'upload_as_gist'
)


class Region(Enum):
    '''Enumeration for WoT regions
    '''
    europe        = 'eu'
    north_america = 'na'
    russia        = 'ru'
    asia          = 'asia'

    def __str__(self) -> str:
        return self.value


class FileOp(Enum):
    '''Enumeration for file operations
    '''
    WRITE = 'w'
    READ  = 'r'


class BanEvaluator(ABC):
    @abstractmethod
    def __init__(self, region: Region, *args, **kwargs):
        self.region = region


    @abstractmethod
    def format_to_md(self, filename: Path):
        raise NotImplementedError()


    @abstractmethod
    def get_leaderboard(self):
        raise NotImplementedError()


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
    *,
    data: Optional[Union[dict, str]] = None,
    file: Optional[Path] = None,
    op: Optional[FileOp] = FileOp.WRITE,
    as_json: Optional[bool] = True
) -> Optional[dict]:
    '''Writes resulting data to file or reads data from file

    Args:
        data (Optional[Union[dict, str]], optional): The data that should be written to the file. Defaults to None.
        filename (Optional[Path], optional): The file to write the data to. Defaults to None.
        op (Optional[FileOp], optional): The file operation. Defaults to FileOp.WRITE.
    Returns:
        Optional[dict]: The file contents in json form
    '''
    with open(file, op.value, encoding='utf-8') as f:
        if op == FileOp.READ:
            if as_json:
                return json.load(f)
            return f.read()

        if op == FileOp.WRITE:
            if isinstance(data, dict):
                json.dump(data, f)

            elif isinstance(data, str):
                f.write(data)

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
    before = file_operation(file=before, op=FileOp.READ)
    after = file_operation(file=after, op=FileOp.READ)
    diff = {k: before.get(k) for k in list(set(before.keys()) - set(after.keys()))}

    assert len(diff) > 0 # Assert that there are actually banned people, if not - something went wrong
    print_message('getting banned players', start_time)
    return diff


def upload_as_gist(file: Path, description: str):
    """Uploads a files content to your Github Gists with GITHUB_TOKEN found in .env file

    Args:
        file (Path): The file to upload
        description (str): The description to give the gist
    """    
    start_time = time.perf_counter()
    token = os.getenv('GITHUB_TOKEN')
    data = file_operation(file=file, op=FileOp.READ, as_json=False)
    r = requests.post(
        'https://api.github.com/gists',
        headers={'Authorization': 'token {}'.format(token)},
        params={'scope': 'gist'},
        data=json.dumps({
            'public': True,
            'description': description,
            'files': {
                file.name: {
                    'content': data
                }
            }
        })
    )
    url = r.json()['html_url']
    print_message(f'uploading to gist ({url})', start_time)
