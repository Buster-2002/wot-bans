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


class FileOp(Enum):
    '''Enumeration for file operations
    '''
    WRITE = 'w'
    READ = 'r'


class Evaluate:
    '''Program to get the banned users in any World of Tanks Ranked season by comparing data
    '''

    def __init__(self, season_id: str, region: str):
        self.region = region
        self.leaderboard_url = f"https://worldoftanks.{'com' if region == 'na' else region}/parla/seasons/leaderboard/?season_id={season_id}&limit=20&offset={{}}"
        self.season_id = season_id
        self.gold_league_range: range = None
        self.silver_league_range: range = None
        self.bronze_league_range: range = None


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


    def set_ranked_league_ranges(self):
        '''Sets the ranges of player ranks for each Ranked League

        Top 10% -> Gold League
        Top % -> Silver League
        Top % -> Bronze League
        '''
        start_time = time.perf_counter()
        r = SESSION.get(self.leaderboard_url.format(1)).json()
        data = r['data']
        self.gold_league_range, self.silver_league_range, self.bronze_league_range = [
            range(r['first'], r['last']) for r in data['meta']['ranges']
        ]

        self.print_message('setting league ranges', start_time)


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
        banned_players = {
            'gold': [],
            'silver': [],
            'bronze': []
        }
        start_time = time.perf_counter()
        data = self.file_op(filename=filename, op=FileOp.READ)

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
        most_banned_clans = '\n'.join([
            f'**{i}:** [{c}](https://wot-life.com/eu/clan/{c}/) ({b} bans)  '
            for i, (c, b) in enumerate(Counter([u['clan_tag']
            for u in data.values() if u['clan_tag']
        ]).most_common(5), 1)])

        # Format banned players and assign them to their league
        for i, v in enumerate(data.values(), 1):
            rank = v['player_rank']
            data_string = f"""| {i} | [{self.escape_md(v['player_name'])}](https://en.wot-life.com/eu/player/{v['player_name']}/) | {intcomma(rank)} | {f"[{self.escape_md(v['clan_tag'])}](https://wot-life.com/eu/clan/{v['clan_tag']}/)" if v['clan_tag'] else 'No Clan'} | {intcomma(v['battles_played'])} | {intcomma(v['avg_exp'])} | {intcomma(v['avg_dmg'])} | {intcomma(v['avg_assist'])} | {v['effectiveness']}% | {v['chevrons']} |"""

            if rank in self.gold_league_range:
                banned_players['gold'].append(data_string)
            elif rank in self.silver_league_range:
                banned_players['silver'].append(data_string)
            elif rank in self.bronze_league_range:
                banned_players['bronze'].append(data_string)

        nl = '\n'
        formatted = f'''
# Player bans for season {self.season_id} of ranked ({self.region.upper()})

## General

This list was made by {__author__}.
If you wish to check out the code that I made to generate this, do so [here](https://gist.github.com/Buster-2002/4db831fb788e4bd89ca15550658e0d13).

This list contains a total of **{len(data.keys())}** banned players. Note that I am only able to know the banned players who were on the leaderboard
at the time of the event ending.

**Top 5 banned clans:**
{most_banned_clans}

## ![goldleaguebadge](https://eu-wotp.wgcdn.co/static/5.97.0_abe061/wotp_static/img/hall_of_fame/frontend/scss/ribbon/img/league-first.png) Gold League

| Index          | Player         | Player Rank    | Clan           | Battles Played | Average XP     | Average Damage | Average Assist | Performance    | Chevrons       |
|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|
{nl.join(banned_players['gold'])}

## ![silverleaguebadge](https://eu-wotp.wgcdn.co/static/5.97.0_abe061/wotp_static/img/hall_of_fame/frontend/scss/ribbon/img/league-second.png) Silver League

| Index          | Player         | Player Rank    | Clan           | Battles Played | Average XP     | Average Damage | Average Assist | Performance    | Chevrons       |
|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|
{nl.join(banned_players['silver'])}

## ![bronzeleaguebadge](https://eu-wotp.wgcdn.co/static/5.97.0_abe061/wotp_static/img/hall_of_fame/frontend/scss/ribbon/img/league-third.png) Bronze League

| Index          | Player         | Player Rank    | Clan           | Battles Played | Average XP     | Average Damage | Average Assist | Performance    | Chevrons       |
|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|:--------------:|
{nl.join(banned_players['bronze'])}
        '''

        self.print_message('formatting to MarkDown', start_time)
        return formatted


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
                self.print_message(f'Received page no.{offset // 20} (offset={offset})', colour=Fore.CYAN)

                for entry in data['results']:
                    season = entry.get('season', {})
                    leaderboard[entry['spa_id']] = ({ # Key is player ID
                        'clan_tag': entry.get('clan_info', {}).get('tag'),
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
                self.print_message(f'API error (HTTP {r["error"]["code"]}), trying again in 5s...', colour=Fore.RED)
                time.sleep(5)

            if not r['data']['results']:
                break

        self.print_message('getting leaderboard pages', start_time)
        return leaderboard


def main():
    '''Determining what to do and putting the Evaluate class to work
    '''
    season_id = input('What is the seasons ID? \n> ').lower()
    region = input('What region do you want to check for? \n> ').lower()
    evaluator = Evaluate(
        season_id=season_id,
        region=region
    )

    answer = input('Do you want to get the current leaderboard data? \ny/n > ').strip()
    if answer.lower() in YES:
        data = evaluator.get_leaderboard()
        evaluator.file_op(
            data,
            Path(f'ranked_data/{region}/{season_id}_{datetime.now().strftime("%m-%d_%H-%M")}_data.json'),
            op=FileOp.WRITE
        )

    answer = input('Do you want to compare data and get banned players? \ny/n > ').strip()
    if answer.lower() in YES:
        filename1, filename2 = input('Which JSON files do you want to compare? \nAnswer <filename1> <filename2> > ').split()
        banned = evaluator.get_difference(
            Path(f'ranked_data/{region}/{filename1}.json'),
            Path(f'ranked_data/{region}/{filename2}.json')
        )
        evaluator.file_op(
            banned,
            Path(f'ranked_data/{region}/{season_id}_banned.json'),
            op=FileOp.WRITE
        )

    answer = input('Do you want to format finalized data using MarkDown? \ny/n > ').strip()
    if answer.lower() in YES:
        file = input('What JSON file do you want to format? \nAnswer <filename> > ').strip()
        formatted = evaluator.format_to_md(
            Path(f'ranked_data/{region}/{file}.json')
        )
        evaluator.file_op(
            formatted,
            Path(f'ranked_data/{region}/{season_id}_formatted.md'),
            op=FileOp.WRITE
        )

if __name__ == '__main__':
    main()
