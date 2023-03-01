#!/usr/bin/env python3
#-*- coding: utf-8 -*-
'''gm_bans.py: Gets global map player leaderboards and formats final data to applicable markdown

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
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import requests
from colorama import Fore, init
from humanize import intcomma

from utils import *

__author__ = 'Buster#5741'
__license__ = 'MIT'

init(autoreset=True)
SESSION = requests.Session()
SESSION.headers = {
    'x-requested-with': 'XMLHttpRequest',
    'Cache-Control': 'no-cache'
}
PLAYER_BAN_HEADER = '''
## Disqualified Players

| Index | Player | Player Rank | Clan | Clan Rank | Fame Points | Battles Played |
|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|
'''.strip()
CLAN_BAN_HEADER = '''
## Clans with 10+ members disqualified

| Index | Clan | Disqualify Amount |
|:--------------:|:--------------:|:--------------:|
'''.strip()
NEW_RECEIVERS_HEADER = '''
## Players that now get a tank due to disqualifications

| Index | Player | Player Rank |
|:--------------:|:--------------:|:--------------:|
'''.strip()


class GmBans(BanEvaluator):
    def __init__(self, region: Region, front_id: str, event_id: str):
        self.region = region
        self.link_region = 'com' if region is Region.NORTH_AMERICA else str(region)
        self.leaderboard_url = f"https://worldoftanks.{self.link_region}/en/clanwars/rating/alley/users/?event_id={{0}}&front_id={{1}}&page_size=100&page={{2}}"
        self.moderator_names = self.get_moderator_names(region)

        self.front_id = front_id
        self.event_id = event_id
        self.new_receivers: Optional[dict] = dict() # Only applies when assessing which players receive a tank after bans

    def get_moderator_names(self, region: Region) -> List[str]:
        """Returns the known moderator/employee in game WoT names for this region

        Args:
            region (Region): The region to get the moderator/employee names for

        Returns:
            List[str]: The moderator/employee WoT names
        """
        with open('employees.json', 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            return json_data[str(region)]

    def format_to_md(self, filename: Path) -> str:
        '''Formats finalized data to text using MarkDown. Suitable
        for uploading to a Github Gist or other MarkDown sharing system

        Args:
            filename: The file including the finalized data
        Returns:
            str: The formatted data
        '''
        formatted, is_employee_banned, start_time, nl = [], False, time.perf_counter(), '\n'
        data = file_operation(file=filename, op=FileOp.READ)

        # Sort banned players by their rank respectively
        data = dict(sorted(
            data.items(),
            key=lambda item: item[1]['player_rank'],
            reverse=False
        ))

        # Get clans that have 10 + of their members banned
        clans_with_10plus_bans = list(sorted([
                (stats_link(clan_tag, self.region, is_clan=True), ban_amount)
                for clan_tag, ban_amount in
                Counter([
                    v['clan_tag'] for v in data.values() if v['clan_tag'] is not None
                ]).items()
                if ban_amount >= 10
            ],
            key=lambda item: item[1],
            reverse=True
        ))

        # Format the markdown with translation
        base_data_url = f'https://github.com/Buster-2002/wot-bans/blob/master/wot-bans/globalmap_data/{self.region}/{self.event_id}/'
        formatted.append(get_description(self.region, BanType.GLOBALMAP).format(
            title=self.event_id.replace('_', ' ').title(),
            region=str(self.region).upper(),
            author=f'[{__author__}](https://discord.com/users/764584777642672160)',
            amount_banned=len(data.keys()),
            logo=f'<img src="https://eu.wargaming.net/globalmap/images/app/features/events/images/{self.event_id}/promo_logo.png" alt="logo" width="30"/>',
            gbadges_url=base_data_url + 'gbadges.txt',
            tankranking_url=base_data_url + 'tankranking.txt'
        ))

        formatted.append(nl)

        # Add the most clan ban rows
        formatted.append(CLAN_BAN_HEADER)
        for i, (clan_name, ban_amount) in enumerate(clans_with_10plus_bans, 1):
            entry = f'| {i} | {clan_name} | {ban_amount} |'
            formatted.append(entry)

        formatted.append(nl)

        # Add the player ban rows
        formatted.append(PLAYER_BAN_HEADER)
        for i, v in enumerate(data.values(), 1):
            name = stats_link(v['player_name'], self.region)

            # Add asterix if the "banned" player is part of WG staff team for region
            if v['player_name'] in self.moderator_names:
                is_employee_banned = True
                name = '\* ' + name

            entry = [
                str(i),
                name,
                intcomma(v['player_rank']),
                stats_link(v['clan_tag'], self.region, is_clan=True),
                intcomma(v['clan_rank']) or 'N/A',
                intcomma(v['player_fame_points']),
                intcomma(v['player_battles_count'])
            ]

            formatted.append('| ' + ' | '.join(entry) + ' |')

        formatted.append(nl)

        if is_employee_banned is True:
            formatted.append('\*: Wargaming staff members who removed themselves from the leaderboard as to not "steal" tanks from regular players.')

        formatted.append(nl)

        # Add new receivers rows
        formatted.append(NEW_RECEIVERS_HEADER)
        for i, v in enumerate(self.new_receivers.values(), 1):
            entry = f'''| {i} | {stats_link(v['player_name'], self.region)} | from {v['old_rank']} to {v['new_rank']} | '''
            formatted.append(entry)

        print_message('formatting to MarkDown', start_time)
        return nl.join(formatted)


    def get_leaderboard(self) -> Dict[str, Dict[str, Union[str, int]]]:
        '''Gets data from event_id leaderboard using the Wargaming API

        Returns:
            Dict[str, Dict[str, int]]: A dict of player IDs with data currently participating in event_id
                                       Includes player id, clan id, fame points and battles
        '''
        leaderboard = {}
        start_time = time.perf_counter()
        current_page = 0

        while True:
            r = SESSION.get(
                self.leaderboard_url.format(
                    self.event_id,
                    self.front_id,
                    current_page
                )
            ).json()

            if r.get('status') == 'ok':
                print_message(f'Received page {current_page + 1}/{r["pages_count"]}')

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

                if current_page >= r['pages_count']:
                    break

            else:
                error_code = r.get('code', 'N/A')
                print_message(f'API error (HTTP {error_code}), trying again in 5s...', colour=Fore.RED)
                time.sleep(5)

        print_message('getting leaderboard pages', start_time)
        return leaderboard


def main() -> None:
    '''Determining what to do and putting the GmBans class to work
    '''
    event_id = input('What is the events name? \n> ').lower().replace(' ', '_')

    while True:
        try:
            region = input('What region do you want to check for? \n> ').lower()
            region = Region(region)
        except ValueError:
            print_message('Invalid region', colour=Fore.RED)
        else:
            break

    evaluator = GmBans(
        region=region,
        front_id=event_id + '_bg',
        event_id=event_id
    )

    answer = input('Do you want to get the current leaderboard data? \ny/n > ').strip()
    if answer.lower() in YES:
        data = evaluator.get_leaderboard()
        file_operation(
            data=data,
            file=Path(f'globalmap_data/{region}/{event_id}/{datetime.now().strftime("%m-%d_%H-%M")}_data.json'),
            op=FileOp.WRITE
        )

    answer = input('Do you want to compare data and get banned players? \ny/n > ').strip()
    if answer.lower() in YES:
        filename1, filename2 = input('Which JSON files do you want to compare? \nAnswer <filename1> <filename2> > ').split()
        banned, new_receivers = get_difference(
            Path(f'globalmap_data/{region}/{event_id}/{filename1}.json'),
            Path(f'globalmap_data/{region}/{event_id}/{filename2}.json'),
            include_new_receivers=True
        )
        evaluator.new_receivers = new_receivers
        file_operation(
            data=banned,
            file=Path(f'globalmap_data/{region}/{event_id}/banned.json'),
            op=FileOp.WRITE
        )

    answer = input('Do you want to format finalized data using MarkDown? \ny/n > ').strip()
    if answer.lower() in YES:
        file = input('What JSON file do you want to format? \nAnswer <filename> > ').strip()
        formatted = evaluator.format_to_md(
            Path(f'globalmap_data/{region}/{event_id}/{file}.json')
        )
        file_operation(
            data=formatted,
            file=Path(f'globalmap_data/{region}/{event_id}/formatted.md'),
            op=FileOp.WRITE
        )

    answer = input('Do you want to upload formatted data to a Github Gist? \ny/n ').strip()
    if answer.lower() in YES:
        file = input('What MD file do you want to upload? \nAnswer <filename> > ').strip()
        upload_as_gist(
            Path(f'globalmap_data/{region}/{event_id}/formatted.md'),
            f'Player bans for the {event_id.title()} campaign ({str(region).upper()})'
        )

if __name__ == '__main__':
    main()
