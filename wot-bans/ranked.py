#!/usr/bin/env python3
#-*- coding: utf-8 -*-
'''ranked_bans.py: Gets ranked leaderboards and formats final data to applicable markdown

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

import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Union

import requests
from colorama import Fore, init
from humanize import intcomma

from utils import *

__author__ = 'Buster#5741'
__license__ = 'MIT'

init(autoreset=True)
SESSION = requests.Session()
SESSION.headers = {'x-requested-with': 'XMLHttpRequest'}
GOLD_HEADER = '''
### <img src="https://eu-wotp.wgcdn.co/static/5.97.0_abe061/wotp_static/img/hall_of_fame/frontend/scss/ribbon/img/league-first.png" alt="goldleaguebadge" width="30"/> Gold League (top {})

| Index          | Player         | Player Rank    | Clan           | Battles Played | Average XP     | Average Damage | Average Assist | Performance    | Chevrons       |
|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|
'''.strip()
SILVER_HEADER = '''
### <img src="https://eu-wotp.wgcdn.co/static/5.97.0_abe061/wotp_static/img/hall_of_fame/frontend/scss/ribbon/img/league-second.png" alt="silverleaguebadge" width="30"/> Silver League (top {})

| Index          | Player         | Player Rank    | Clan           | Battles Played | Average XP     | Average Damage | Average Assist | Performance    | Chevrons       |
|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|
'''.strip()
BRONZE_HEADER = '''
### <img src="https://eu-wotp.wgcdn.co/static/5.97.0_abe061/wotp_static/img/hall_of_fame/frontend/scss/ribbon/img/league-third.png" alt="bronzeleaguebadge" width="30"/> Bronze League (top {})

| Index          | Player         | Player Rank    | Clan           | Battles Played | Average XP     | Average Damage | Average Assist | Performance    | Chevrons       |
|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|
'''.strip()

class RankedBans(BanEvaluator):
    def __init__(self, region: Region, season_id: str):
        self.region = region
        self.leaderboard_url = f"https://worldoftanks.{'com' if region is Region.NORTH_AMERICA else str(region)}/parla/seasons/leaderboard/?season_id={season_id}&limit=20&offset={{}}"

        self.season_id = season_id
        self.gold_league_range: range = None
        self.silver_league_range: range = None
        self.bronze_league_range: range = None


    def set_ranked_league_ranges(self):
        '''Sets the ranges of player ranks for each Ranked League

        Top 10% participants -> Gold League
        Top 20% participants -> Silver League
        Top 50% participants -> Bronze League
        '''
        start_time = time.perf_counter()
        r = SESSION.get(self.leaderboard_url.format(1)).json()
        data = r['data']
        self.gold_league_range, self.silver_league_range, self.bronze_league_range = [
            range(r['first'], r['last']) for r in data['meta']['ranges']
        ]

        print_message('setting league ranges', start_time)


    def format_to_md(self, file: Path) -> str:
        '''Formats finalized data to text using MarkDown. Suitable
        for uploading to a Github Gist or other MarkDown sharing system

        Args:
            file: The file including the finalized data
        Returns:
            str: The formatted data
        '''
        banned_players = {
            'gold': [],
            'silver': [],
            'bronze': []
        }
        formatted, start_time, nl = [], time.perf_counter(), '\n'
        data = file_operation(file=file, op=FileOp.READ)

        # Check if league ranges have been manually set, if not set them using API
        if not any([self.gold_league_range, self.silver_league_range, self.bronze_league_range]):
            self.set_ranked_league_ranges()

        # Sort banned players by their rank respectively
        data = dict(sorted(
            data.items(),
            key=lambda item: item[1]['player_rank'],
            reverse=False
        ))

        # Get top 5 clans with most banned members in this list
        most_banned_clans = nl.join([
            f'**{i}:** {stats_link(clan_tag, self.region, is_clan=True)} ({ban_amount} bans)  '
            for i, (clan_tag, ban_amount) in enumerate(Counter([v['clan_tag']
            for v in data.values() if v['clan_tag'] is not None
        ]).most_common(5), 1)])

        # Format banned players and assign them to their league
        for i, v in enumerate(data.values(), 1):
            rank = v['player_rank']
            data_string = f"""| {i} | {stats_link(v['player_name'], self.region)} | {intcomma(rank)} | {stats_link(v['clan_tag'], self.region, is_clan=True)}| {intcomma(v['battles_played'])} | {intcomma(v['avg_exp'])} | {intcomma(v['avg_dmg'])} | {intcomma(v['avg_assist'])} | {v['effectiveness']}% | {v['chevrons']} |"""

            if rank in self.gold_league_range:
                banned_players['gold'].append(data_string)
            elif rank in self.silver_league_range:
                banned_players['silver'].append(data_string)
            elif rank in self.bronze_league_range:
                banned_players['bronze'].append(data_string)

        formatted.append(get_description(self.region, BanType.RANKED).format(
            season=self.season_id,
            region=str(self.region).upper(),
            author=f'[{__author__}](https://discord.com/users/764584777642672160)',
            amount_banned=len(data.keys()),
            most_banned_clans=most_banned_clans
        ))

        formatted.append(nl)

        # Add the gold league bans rows
        formatted.append(GOLD_HEADER.format(len(self.gold_league_range) - 1))
        formatted.append(nl.join(banned_players['gold']))
        
        formatted.append(nl)

        # Add the silver league bans rows
        formatted.append(SILVER_HEADER.format(len(self.silver_league_range) - 1))
        formatted.append(nl.join(banned_players['silver']))

        formatted.append(nl)

        # Add the bronze league bans rows
        formatted.append(BRONZE_HEADER.format(len(self.bronze_league_range) - 1))
        formatted.append(nl.join(banned_players['bronze']))

        print_message('formatting to MarkDown', start_time)
        return nl.join(formatted)


    def get_leaderboard(self) -> Dict[str, Dict[str, Union[str, int]]]:
        '''Gets data from event leaderboard using the Wargaming API

        Returns:
            Dict[str, Dict[str, int]]: A dict of player IDs with data currently participating in event
                                       Includes player id/name/rank, battles played, average xp/damage/assist, effectiveness and chevrons earned
        '''
        leaderboard, start_time, offset = dict(), time.perf_counter(), int()

        while True:
            r = SESSION.get(self.leaderboard_url.format(offset)).json()
            data = r['data']

            if r.get('status') == 'ok':
                print_message(f'Received page no.{offset // 20} (offset={offset})', colour=Fore.CYAN)

                for entry in data['results']:
                    season = entry.get('season', {})
                    leaderboard[entry['spa_id']] = ({ # Key is player ID
                        'clan_tag': entry['clan_info']['tag'] or None,
                        'player_name': entry['nickname'],
                        'player_rank': entry['position'],
                        'is_suspended': entry['is_suspended'],
                        'battles_played': season['total_battles'],
                        'avg_exp': season['avg_exp'],
                        'avg_dmg': season['avg_damage'],
                        'avg_assist': season['avg_assist_damage'],
                        'effectiveness': season['rank_progress'],
                        'chevrons': season['battles_with_steps']
                    })

                # One "page" contains a max of 20 players. The API here uses an offset
                # of amount of players; so an offset 40 would result in page 3.

                # This is different from the API endpoint for the clanwars leaderboard, as that
                # takes a page number and can result in a maximum of 100 players per request.
                offset += 20

            else:
                print_message(f'API error (HTTP {r["error"]["code"]}), trying again in 5s...', colour=Fore.RED)
                time.sleep(5)

            if not r['data']['results']:
                break

        print_message('getting leaderboard pages', start_time)
        return leaderboard


def main():
    '''Determining what to do and putting the RankedBans class to work
    '''
    season_id = input('What is the seasons ID? \n> ').lower()

    while True:
        try:
            region: str = input('What region do you want to check for? \n> ').lower()
            region: Region = Region(region)
        except ValueError:
            print_message('Invalid region', colour=Fore.RED)
        else:
            break

    evaluator = RankedBans(
        region=region,
        season_id=season_id
    )

    answer = input('Do you want to get the current leaderboard data? \ny/n > ').strip()
    if answer.lower() in YES:
        data = evaluator.get_leaderboard()
        file_operation(
            data=data,
            file=Path(f'ranked_data/{region}/{season_id}/{datetime.now().strftime("%m-%d_%H-%M")}_data.json'),
            op=FileOp.WRITE
        )

    answer = input('Do you want to compare data and get banned players? \ny/n > ').strip()
    if answer.lower() in YES:
        filename1, filename2 = input('Which JSON files do you want to compare? \nAnswer <filename1> <filename2> > ').split()
        banned = get_difference(
            Path(f'ranked_data/{region}/{season_id}/{filename1}.json'),
            Path(f'ranked_data/{region}/{season_id}/{filename2}.json'),
            include_new_receivers=False
        )
        file_operation(
            data=banned,
            file=Path(f'ranked_data/{region}/{season_id}/banned.json'),
            op=FileOp.WRITE
        )

    answer = input('Do you want to format finalized data using MarkDown? \ny/n > ').strip()
    if answer.lower() in YES:
        file = input('What JSON file do you want to format? \nAnswer <filename> > ').strip()
        formatted = evaluator.format_to_md(
            Path(f'ranked_data/{region}/{season_id}/{file}.json')
        )
        file_operation(
            data=formatted,
            file=Path(f'ranked_data/{region}/{season_id}/formatted.md'),
            op=FileOp.WRITE
        )

    answer = input('Do you want to upload formatted data to a Github Gist? \ny/n ').strip()
    if answer.lower() in YES:
        file = input('What MD file do you want to upload? \nAnswer <filename> > ').strip()
        upload_as_gist(
            Path(f'ranked_data/{region}/{season_id}/formatted.md'),
            f'Player bans for season {season_id.title()} of ranked ({str(region).upper()})'
        )

if __name__ == '__main__':
    main()
