#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import json
import re
import time
from collections import Counter
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Union

import requests
from colorama import Fore, init
from humanize import intcomma, precisedelta

__author__ = 'Buster#5741'
__license__ = 'MIT'

init(autoreset=True)
SESSION = requests.Session()
SESSION.headers ={
    'x-requested-with': 'XMLHttpRequest'
}
YES = {'yes', 'y', 'true', 't', '1', 'enable', 'on'}
PLAYER_BAN_HEADER = '''
## Banned Players

| Index | Player | Player Rank | Clan | Clan Rank | Fame Points | Battles Played |
|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|
'''.strip()
CLAN_BAN_HEADER = '''
## Clans with 10+ members banned

| Index | Clan | Ban Amount |
|:--------------:|:--------------:|:--------------:|
'''.strip()
ENGLISH_TEXT = '''
# Player bans for the {logo} {title} campaign ({region})

This list was made by {author}.    
If you wish to check out the code that I made to generate this, do so [here](https://gist.github.com/Buster-2002/6237393150cc371066b684183e1a95c6).    

This list contains a total of **{amount_banned}** banned players. Note that I am only able to know the banned players who were on the leaderboard at the time of the event ending.  
'''.strip()
RUSSIAN_TEXT = '''
# Забаненные игроков в кампании {logo} {title} ({region})  

Этот список был составлен {author}.  
Если вы хотите проверить код, который я сделал для его создания, сделайте это [здесь](https://gist.github.com/Buster-2002/6237393150cc371066b684183e1a95c6).  

Всего в этом списке **{amount_banned}** забаненных игроков. Обратите внимание, что я могу узнать только забаненных игроков, которые были в таблице лидеров на момент окончания мероприятия.  
'''.strip()
MANDARIN_TEXT = '''
# {logo} {title} 广告系列 ({region}) 的玩家禁令  

此列表由 {author} 制作。  
如果您想查看我为生成此代码而编写的代码，请在 [此处](https://gist.github.com/Buster-2002/6237393150cc371066b684183e1a95c6) 进行操作。  

此列表包含总共 **{amount_banned}** 被禁玩家。请注意，我只能知道排行榜上的被禁玩家 在活动结束时。  
'''.strip()
REGION_TRANSLATIONS = {
    'asia': MANDARIN_TEXT + '\n\n' + ENGLISH_TEXT,
    'ru': RUSSIAN_TEXT + '\n\n' + ENGLISH_TEXT,
    'en': ENGLISH_TEXT,
    'na': ENGLISH_TEXT
}


class FileOp(Enum):
    '''Enumeration for file operations
    '''
    WRITE = 'w'
    READ  = 'r'


class Evaluate:
    '''Program to get the banned users in any World of Tanks campaign by comparing data
    '''

    def __init__(self, front_id: str, event_id: str, region: str):
        self.region = region
        self.leaderboard_url = f"https://worldoftanks.{'com' if region == 'na' else region}/en/clanwars/rating/alley/users/?event_id={{0}}&front_id={{1}}&page_size=100&page={{2}}"
        self.front_id = front_id
        self.event_id = event_id


    @staticmethod
    def file_op(
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


    @staticmethod
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


    @staticmethod
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


    def get_difference(
        self,
        before: Path,
        after: Path
    ) -> Dict[str, str]:
        '''Gets the difference between 2 json files by dict keys

        Args:
            before (str, optional): The file to check against
            after (str, optional): The file to check with
        Returns:
            Dict[str, str]: A list of all the removed dicts
        '''
        start_time = time.perf_counter()
        before = self.file_op(filename=before, op=FileOp.READ)
        after = self.file_op(filename=after, op=FileOp.READ)
        diff = {k: before.get(k) for k in list(set(before.keys()) - set(after.keys()))}

        assert len(diff) > 0 # Assert that there are actually banned people, if not - something went wrong
        self.print_message('getting banned players', start_time)
        return diff


    def format_to_md(
        self,
        filename: Path
    ) -> str:
        '''Formats finalized data to text using MarkDown. Suitable
        for uploading to a Github Gist or other MarkDown sharing system

        Args:
            filename: The file including the finalized data
        Returns:
            str: The formatted data
        '''
        formatted, start_time = [], time.perf_counter()
        data = self.file_op(filename=filename, op=FileOp.READ)

        # Sort banned players by their rank respectively
        data = dict(sorted(
            data.items(),
            key=lambda item: item[1]['player_rank'],
            reverse=False
        ))

        # Get clans that have 10 + of their members banned
        clans_with_10plus_bans = list(sorted([
                (f'[{c}](https://wot-life.com/eu/clan/{c}/)', b)
                for c, b in Counter([v['clan_tag']
                for v in data.values() if v['clan_tag'] is not None
                ]).items() if b >= 10
            ],
            key=lambda item: item[1],
            reverse=True
        ))

        # Format the markdown with translation
        formatted.append(REGION_TRANSLATIONS[self.region].format(
            title=self.event_id.title(),
            region=self.region.upper(),
            author=f'[{__author__}](https://discord.com/users/764584777642672160)',
            amount_banned=len(data.keys()),
            logo=f'<img src="https://eu.wargaming.net/globalmap/images/app/features/events/images/{self.event_id}/promo_logo.png" alt="logo" width="30"/>'
        ))

        formatted.append('\n')

        # Add the most clan ban rows
        formatted.append(CLAN_BAN_HEADER)
        for i, (clan_name, ban_amount) in enumerate(clans_with_10plus_bans, 1):
            formatted.append(f'| {i} | {clan_name} | {ban_amount} |')

        formatted.append('\n')

        # Add the player ban rows
        formatted.append(PLAYER_BAN_HEADER)
        for i, v in enumerate(data.values(), 1):
            formatted.append(f'''| {i} | [{self.escape_md(v['player_name'])}](https://en.wot-life.com/eu/player/{v['player_name']}/) | {intcomma(v['player_rank'])} | {f"[{self.escape_md(v['clan_tag'])}](https://wot-life.com/eu/clan/{v['clan_tag']}/)"  if v['clan_tag'] else 'No Clan'} | {intcomma(v['clan_rank']) or 'N/A'} | {intcomma(v['player_fame_points'])} | {v['player_battles_count']} |''')

        self.print_message('formatting to MarkDown', start_time)
        return '\n'.join(formatted)


    def get_leaderboard(self) -> Dict[str, Dict[str, Union[str, int]]]:
        '''Gets data from event leaderboard using the Wargaming API

        Returns:
            Dict[str, Dict[str, int]]: A dict of player IDs with data currently participating in event
                                       Includes player id, clan id, fame points and battles
        '''
        leaderboard, start_time, current_page = dict(), time.perf_counter(), int()

        while True:
            r = SESSION.get(
                self.leaderboard_url.format(
                    self.event_id,
                    self.front_id,
                    current_page
                )
            ).json()

            if r.get('status') == 'ok':
                self.print_message(f'Received page no.{current_page}', colour=Fore.CYAN)

                for entry in r['accounts_ratings']:
                    leaderboard[entry['id']] = ({ # Key is player ID
                        'clan_tag': entry.get('clan', {}).get('tag'),
                        'clan_rank': entry.get('clan_rank'),
                        'player_name': entry.get('name'),
                        'player_rank': entry.get('rank'),
                        'player_fame_points': entry.get('fame_points'),
                        'player_battles_count': entry.get('battles_count')
                    })

                current_page += 1

            elif r.get('code') == 'RATING_NOT_FOUND':
                break

            else:
                self.print_message(f'API error (HTTP {r["error"]["code"]}), trying again in 5s...', colour=Fore.RED)
                time.sleep(5)

        self.print_message('getting leaderboard pages', start_time)
        return leaderboard


def main():
    '''Determining what to do and putting the Evaluate class to work
    '''
    event = input('What is the events name? \n> ').lower()
    region = input('What region do you want to check for? \n> ').lower()
    evaluator = Evaluate(
        front_id=event + '_bg',
        event_id=event,
        region=region
    )

    answer = input('Do you want to get the current leaderboard data? \ny/n > ').strip()
    if answer.lower() in YES:
        data = evaluator.get_leaderboard()
        evaluator.file_op(
            data,
            Path(f'globalmap_data/{region}/{event}_{datetime.now().strftime("%m-%d_%H-%M")}_data.json'),
            op=FileOp.WRITE
        )

    answer = input('Do you want to compare data and get banned players? \ny/n > ').strip()
    if answer.lower() in YES:
        filename1, filename2 = input('Which JSON files do you want to compare? \nAnswer <filename1> <filename2> > ').split()
        banned = evaluator.get_difference(
            Path(f'globalmap_data/{region}/{filename1}.json'),
            Path(f'globalmap_data/{region}/{filename2}.json')
        )
        evaluator.file_op(
            banned,
            Path(f'globalmap_data/{region}/{event}_banned.json'),
            op=FileOp.WRITE
        )

    answer = input('Do you want to format finalized data using MarkDown? \ny/n > ').strip()
    if answer.lower() in YES:
        file = input('What JSON file do you want to format? \nAnswer <filename> > ').strip()
        formatted = evaluator.format_to_md(
            Path(f'globalmap_data/{region}/{file}.json')
        )
        evaluator.file_op(
            formatted,
            Path(f'globalmap_data/{region}/{event}_formatted.md'),
            op=FileOp.WRITE
        )

if __name__ == '__main__':
    main()
