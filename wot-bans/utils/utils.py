#!/usr/bin/env python3
#-*- coding: utf-8 -*-
'''utils.py: Some functions used in both globalmap.py and ranked.py

The MIT License (MIT)

Copyright (c) 2021-present Buster

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
'''

import json
import os
import re
import time
from abc import ABC, abstractmethod
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union

import requests
from colorama import Fore, init
from dotenv import load_dotenv
from humanize import precisedelta

from .enums import *

load_dotenv()
init(autoreset=True)
__author__ = 'Buster#5741'
__license__ = 'MIT'
__all__ = (
    # Classes
    'BanEvaluator',

    # Variables
    'YES',

    # Functions
    'print_message',
    'file_operation',
    'escape_md',
    'get_difference',
    'upload_as_gist',
    'stats_link',
    'get_description'
)
YES = {'yes', 'y', 'true', 't', '1', 'enable', 'on'}
GM_ENGLISH = '''
# Player bans for the {logo} {title} campaign ({region})

*Made by {author}*

## General
The raw data and the code used is available in the GitHub repo [here](https://github.com/Buster-2002/wot-bans/).

Below follows a list of the names and related statistics of **{amount_banned}** players in the {region} region that were disqualified from the leaderboard. They will not receive any rewards, and depending on previous offenses might be permanently banned from playing.

> Using prohibited modifications or violating the game or [{title} rules]({regulations}) in any way leads to exclusion from the Alley of Fame, thereby preventing violators from receiving rewards.
>
> \- *World of Tanks Fair Play Policy*

Also check out:  
- [Global Map Legend badge receivers]({gbadges_url})  
- [Clan ranking by reward tanks]({tankranking_url})  

Note that I am only able to know the banned players who were on the leaderboard at the time of the event ending.
'''.strip()
GM_RUSSIAN = '''
# Блокировка игроков в кампании {logo} {title} ({region})

*Сделано {author}*

## Общий
Необработанные данные для этой кампании и используемый код доступны в репозитории GitHub [здесь](https://github.com/Buster-2002/wot-bans/).

Ниже приводится список имен и связанная с ними статистика **{amount_banned}** игроков в регионе {region}, которые были дисквалифицированы из таблицы лидеров. Они не получат никаких наград, и в зависимости от предыдущих нарушений могут быть навсегда заблокированы от игры.

> Использование запрещенных модификаций или нарушение игры или [{title} события]({regulations}) каким-либо образом влечет за собой исключение из Аллеи славы, тем самым лишая нарушителей возможности получения наград.
>
> \- *Политика честной игры в World of Tanks*

Также проверьте:  
- [получатели значков Global Map Legend]({gbadges_url})  
- [Рейтинг клана по призовым танкам]({tankranking_url})  

Обратите внимание, что я могу узнать только тех забаненных игроков, которые были в таблице лидеров на момент окончания события.
'''.strip()
GM_MANDARIN = '''
# {logo} {title} 活动 ({region}) 的玩家禁令

*由{author}制作*

## 一般的
此活动的原始数据和使用的代码可在 GitHub 存储库 [此处](https://github.com/Buster-2002/wot-bans/) 上找到。

以下是 {region} 地区被取消排行榜资格的 **{amount_banned}** 玩家的姓名和相关统计数据列表。 他们将不会获得任何奖励，并且根据之前的违规行为可能会被永久禁止参加比赛。

> 以任何方式使用禁止的修改或违反游戏或[{title}规则]({regulations})导致被排除在名人堂之外，从而阻止违反者获得奖励。
>
> \- *坦克世界公平竞赛政策*

另请查看:  
- [全球地图图例徽章接收器]({gbadges_url})  
- [战队奖励坦克排名]({tankranking_url})  

请注意，我只能知道活动结束时在排行榜上的被禁玩家。
'''.strip()
RANKED_ENGLISH = '''
# Player bans for season {season} of ranked ({region})

*Made by {author}*

## General
The raw data and the code used is available in the GitHub repo [here](https://github.com/Buster-2002/wot-bans/).

Below follows a list of the names and related statistics of **{amount_banned}** players in the {region} region that were disqualified from the leaderboard. They will not receive any rewards, and depending on previous offenses might be permanently banned from playing.

Note that I am only able to know the banned players who were on the leaderboard at the time of the event ending.

## Top 5 clans with most members banned
{most_banned_clans}
'''.strip()
RANKED_RUSSIAN = '''
# Блокировка игроков на сезон {season} в рейтинге ({region})

*Сделано {author}*

## Общий
Необработанные данные и используемый код доступны в репозитории GitHub [здесь] (https://github.com/Buster-2002/wot-bans/).

Ниже приводится список имен и связанная с ними статистика **{amount_banned}** игроков в регионе {region}, которые были дисквалифицированы из таблицы лидеров. Они не получат никаких наград, и в зависимости от предыдущих нарушений могут быть навсегда заблокированы от игры.

Обратите внимание, что я могу узнать только тех забаненных игроков, которые были в таблице лидеров на момент окончания события.

## Топ 5 кланов с большинством забаненных членов
{most_banned_clans}
'''.strip()
RANKED_MANDARIN = '''
# 排名第 {season} 赛季的玩家封禁（{region}）

*由{author}制作*

＃＃ 一般的
原始数据和使用的代码可在 GitHub 存储库 [此处](https://github.com/Buster-2002/wot-bans/) 中找到。

以下是 {region} 地区被取消排行榜资格的 **{amount_banned}** 玩家的姓名和相关统计数据列表。 他们将不会获得任何奖励，并且根据之前的违规行为可能会被永久禁止参加比赛。

请注意，我只能知道活动结束时在排行榜上的被禁玩家。

## 被禁止成员最多的前 5 个部落
{most_banned_clans}
'''.strip()

TRANSLATIONS = {
    BanType.GLOBALMAP: {
        Region.RUSSIA: (GM_RUSSIAN, 'русский'),
        Region.ASIA: (GM_MANDARIN, '中文')
    },
    BanType.RANKED: {
        Region.RUSSIA: (RANKED_RUSSIAN, 'русский'),
        Region.ASIA: (RANKED_MANDARIN, '中文')
    }
}


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
    colour: Fore = Fore.CYAN
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
    with suppress(FileExistsError):
        Path(file).parents[0].mkdir(parents=True, exist_ok=True)

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


def get_difference(before: Path, after: Path, *, include_new_receivers: bool) -> Dict[str, str]:
    '''Gets the difference between 2 json files by dict keys

    Args:
        before (str, optional): The file to check against
        after (str, optional): The file to check with
        include_new_receivers (bool, optional): Whether to also return players
                                                who receive a tank due to bans
                                                (only applies to globalmap.py)
    Returns:
        Dict[str, str]: A list of all the removed dicts
    '''
    start_time = time.perf_counter()
    before = file_operation(file=before, op=FileOp.READ)
    after = file_operation(file=after, op=FileOp.READ)
    diff = {k: before.get(k) for k in list(set(before.keys()) - set(after.keys()))}
    assert len(diff) > 0 # No difference between file keys

    if include_new_receivers:
        new_receivers = {}
        for player_id, old_data in before.items():
            if new_data := after[player_id] if player_id in after.keys() else None:
                if old_data['receives_tank'] == False and new_data['receives_tank'] == True:
                    new_receivers[player_id] = {
                        'player_name': old_data['player_name'],
                        'old_rank': old_data['player_rank'],
                        'new_rank': new_data['player_rank']
                    }

        print_message('getting banned players and new tank receivers', start_time)
        return diff, new_receivers

    print_message('getting banned players', start_time)
    return diff


def upload_as_gist(file: Path, description: str):
    """Uploads a files content to your Github Gists using the GITHUB_TOKEN found in .env file

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


def stats_link(player_or_clan_name: Optional[str], region: Region, *, is_clan: bool = False) -> str:
    """Generates markdown link with escaped name to stats of clan or player

    Args:
        player_or_clan_name (str): The name of the player or clan you want to link
        region (Region): The region in which the player or clan is active
        is_clan (bool): Whether it is a clan you want to link
    Returns:
        str: The stats link appropriate for region
    """
    domain = 'player'
    if is_clan is True:
        domain = 'clan'

    if player_or_clan_name is None and is_clan is True:
        return 'No Clan'

    # Wot-life doesn't do asia region stats
    if region is Region.ASIA:
        return f'[{escape_md(player_or_clan_name)}](https://wotlabs.net/sea/{domain}/{player_or_clan_name})'

    return f'[{escape_md(player_or_clan_name)}](https://wot-life.com/{region}/{domain}/{player_or_clan_name}/)'


def get_description(region: Region, ban_type: BanType) -> str:
    """Gets the description for ranked or clanwars formatted markdown list

    Always includes English text, but for Russia and Asia includes a collapsed translation

    Args:
        region (Region): The region to get text for
        ban_type (BanType): GLOBALMAP or RANKED

    Returns:
        str: The description for this list
    """
    if ban_type is BanType.GLOBALMAP:
        english = GM_ENGLISH
    elif ban_type is BanType.RANKED:
        english = RANKED_ENGLISH

    if region in (Region.NORTH_AMERICA, region.EUROPE):
        return english

    else:
        translated_text, summary = TRANSLATIONS[ban_type][region]
        return f'''
<details open>
<summary>English</summary>

{english}

</details>

<details>
<summary>{summary}</summary>

{translated_text}

</details>
        '''.strip()

