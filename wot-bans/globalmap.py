#!/usr/bin/env python3
#-*- coding: utf-8 -*-
'''gm_bans.py: Gets global map player leaderboards and formats final data to applicable markdown'''

import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union

import requests
from colorama import Fore, init
from humanize import intcomma

from utils import *

__author__ = 'Buster#5741'
__license__ = 'MIT'

init(autoreset=True)
SESSION = requests.Session()
SESSION.headers = {'x-requested-with': 'XMLHttpRequest'}
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
NEW_RECEIVERS_HEADER = '''
## Players that now get a tank due to bans

| Index | Player | Player Rank |
|:--------------:|:--------------:|:--------------:|
'''.strip()
ENGLISH_TEXT = '''
# Player bans for the {logo} {title} campaign ({region})
*Made by {author}*

## General

If you wish to check out the code that I made to generate this, do so [here](https://github.com/Buster-2002/wot-bans/blob/master/wot-bans/globalmap.py).

Below follows a list of the names and related statistics of **{amount_banned}** players in the {region} region that were disqualified from the leaderboard. They will not receive any rewards, and depending on previous offenses might be permanently banned from playing. 

> Using prohibited modifications or violating the game or [event rules]({regulations}) in any way leads to exclusion from the Alley of Fame, thereby preventing violators from receiving rewards.
> 
> \- *World of Tanks Fair Play Policy*

Note that I am only able to know the banned players who were on the leaderboard at the time of the event ending.
'''.strip()
RUSSIAN_TEXT = '''
# Блокировка игроков в кампании {logo} {title} ({region})
*Сделано {author}*

## Общий

Если вы хотите проверить код, который я сделал для его создания, сделайте это [здесь](https://github.com/Buster-2002/wot-bans/blob/master/wot-bans/globalmap.py).

Ниже приводится список имен и связанная с ними статистика **{amount_banned}** игроков в регионе {region}, которые были дисквалифицированы из таблицы лидеров. Они не получат никаких наград, и в зависимости от предыдущих нарушений могут быть навсегда заблокированы от игры.

> Использование запрещенных модификаций или нарушение игры или [правил события]({regulations}) каким-либо образом влечет за собой исключение из Аллеи славы, тем самым лишая нарушителей возможности получить награды.
>
> \- *Политика честной игры в World of Tanks*

Обратите внимание, что я могу узнать только тех забаненных игроков, которые были в таблице лидеров на момент окончания события.
'''.strip()
MANDARIN_TEXT = '''
# {logo} {title} 活动 ({region}) 的玩家禁令
*由{author}制作*

## 一般的

如果您想查看我为生成此代码而编写的代码，请在 [此处](https://github.com/Buster-2002/wot-bans/blob/master/wot-bans/globalmap.py) 进行。

以下是 {region} 地区被取消排行榜资格的 **{amount_banned}** 玩家的姓名和相关统计数据列表。他们将不会获得任何奖励，并且根据之前的违规行为可能会被永久禁止参加比赛。

> 以任何方式使用禁止的修改或违反游戏或[活动规则]({regulations})导致被排除在名人堂之外，从而阻止违反者获得奖励。
>
> \- *坦克世界公平竞赛政策*

请注意，我只能知道活动结束时在排行榜上的被禁玩家。
'''.strip()
REGION_TRANSLATIONS = {
    Region.asia: MANDARIN_TEXT + '\n\n' + ENGLISH_TEXT,
    Region.russia: RUSSIAN_TEXT + '\n\n' + ENGLISH_TEXT,
    Region.europe: ENGLISH_TEXT,
    Region.north_america: ENGLISH_TEXT
}


class GmBans(BanEvaluator):
    def __init__(self, region: Region, front_id: str, event_id: str):
        self.region = region
        self.link_region = 'com' if region is Region.north_america else str(region)
        self.leaderboard_url = f"https://worldoftanks.{self.link_region}/en/clanwars/rating/alley/users/?event_id={{0}}&front_id={{1}}&page_size=100&page={{2}}"

        self.front_id = front_id
        self.event_id = event_id
        self.new_receivers: Optional[dict] = None


    def format_to_md(self, filename: Path) -> str:
        '''Formats finalized data to text using MarkDown. Suitable
        for uploading to a Github Gist or other MarkDown sharing system

        Args:
            filename: The file including the finalized data
        Returns:
            str: The formatted data
        '''
        formatted, start_time = [], time.perf_counter()
        data = file_operation(file=filename, op=FileOp.READ)

        # Sort banned players by their rank respectively
        data = dict(sorted(
            data.items(),
            key=lambda item: item[1]['player_rank'],
            reverse=False
        ))

        # Get clans that have 10 + of their members banned
        clans_with_10plus_bans = list(sorted([
                (f'[{escape_md(clan_tag)}]({stats_link(clan_tag, self.region, is_clan=True)})', ban_amount)
                for clan_tag, ban_amount in Counter([v['clan_tag']
                for v in data.values() if v['clan_tag'] is not None
                ]).items() if ban_amount >= 10
            ],
            key=lambda item: item[1],
            reverse=True
        ))

        # Format the markdown with translation
        formatted.append(REGION_TRANSLATIONS[self.region].format(
            title=self.event_id.title(),
            region=str(self.region).upper(),
            author=f'[{__author__}](https://discord.com/users/764584777642672160)',
            amount_banned=len(data.keys()),
            logo=f'<img src="https://eu.wargaming.net/globalmap/images/app/features/events/images/{self.event_id}/promo_logo.png" alt="logo" width="30"/>',
            regulations=f'https://worldoftanks.{self.link_region}/en/content/confrontation-regulations/'
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
            formatted.append(f'''| {i} | [{escape_md(v['player_name'])}]({stats_link(v['player_name'], self.region)}) | {intcomma(v['player_rank'])} | {f"[{escape_md(v['clan_tag'])}]({stats_link(v['clan_tag'], self.region, is_clan=True)})" if v['clan_tag'] else 'No Clan'} | {intcomma(v['clan_rank']) or 'N/A'} | {intcomma(v['player_fame_points'])} | {v['player_battles_count']} |''')

        formatted.append('\n')

        # Add new receivers rows
        formatted.append(NEW_RECEIVERS_HEADER)
        for i, v in enumerate(self.new_receivers.values(), 1):
            formatted.append(f'''| {i} | [{escape_md(v['player_name'])}]({stats_link(v['player_name'], self.region)}) | from {v['old_rank']} to {v['new_rank']} | ''')

        print_message('formatting to MarkDown', start_time)
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
                print_message(f'Received page {current_page + 1}/{r["pages_count"]}', colour=Fore.CYAN)

                for entry in r['accounts_ratings']:
                    leaderboard[entry['id']] = ({ # Key is player ID
                        'clan_tag': entry.get('clan', {}).get('tag'),
                        'clan_rank': entry.get('clan_rank'),
                        'player_name': entry.get('name'),
                        'player_rank': entry.get('rank'),
                        'player_fame_points': entry.get('fame_points'),
                        'player_battles_count': entry.get('battles_count'),
                        'receives_tank': bool([reward['value'] for reward in entry.get('rewards') if reward['reward_type'] == 'tank_availability'])
                    })

                current_page += 1

            elif r.get('code') == 'RATING_NOT_FOUND':
                break

            else:
                print_message(f'API error (HTTP {r["error"]["code"]}), trying again in 5s...', colour=Fore.RED)
                time.sleep(5)

        print_message('getting leaderboard pages', start_time)
        return leaderboard


def main():
    '''Determining what to do and putting the GmBans class to work
    '''
    event = input('What is the events name? \n> ').lower()

    while True:
        try:
            region: str = input('What region do you want to check for? \n> ').lower()
            region: Region = Region(region)
        except ValueError:
            print_message('Invalid region', colour=Fore.RED)
        else:
            break

    evaluator = GmBans(
        region=region,
        front_id=event + '_bg',
        event_id=event
    )

    answer = input('Do you want to get the current leaderboard data? \ny/n > ').strip()
    if answer.lower() in YES:
        data = evaluator.get_leaderboard()
        file_operation(
            data=data,
            file=Path(f'globalmap_data/{region}/{event}_{datetime.now().strftime("%m-%d_%H-%M")}_data.json'),
            op=FileOp.WRITE
        )

    answer = input('Do you want to compare data and get banned players? \ny/n > ').strip()
    if answer.lower() in YES:
        filename1, filename2 = input('Which JSON files do you want to compare? \nAnswer <filename1> <filename2> > ').split()
        banned, new_receivers = get_difference(
            Path(f'globalmap_data/{region}/{filename1}.json'),
            Path(f'globalmap_data/{region}/{filename2}.json'),
            include_new_receivers=True
        )
        evaluator.new_receivers = new_receivers
        file_operation(
            data=banned,
            file=Path(f'globalmap_data/{region}/{event}_banned.json'),
            op=FileOp.WRITE
        )

    answer = input('Do you want to format finalized data using MarkDown? \ny/n > ').strip()
    if answer.lower() in YES:
        file = input('What JSON file do you want to format? \nAnswer <filename> > ').strip()
        formatted = evaluator.format_to_md(
            Path(f'globalmap_data/{region}/{file}.json')
        )
        file_operation(
            data=formatted,
            file=Path(f'globalmap_data/{region}/{event}_formatted.md'),
            op=FileOp.WRITE
        )

    answer = input('Do you want to upload formatted data to a Github Gist? \ny/n ').strip()
    if answer.lower() in YES:
        file = input('What MD file do you want to upload? \nAnswer <filename> > ').strip()
        upload_as_gist(
            Path(f'globalmap_data/{region}/{event}_formatted.md'),
            f'Player bans for the {event.title()} campaign ({str(region).upper()})'
        )

if __name__ == '__main__':
    main()
