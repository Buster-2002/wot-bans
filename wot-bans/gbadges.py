#!/usr/bin/env python3
#-*- coding: utf-8 -*-
'''gbadges.py: Calculates which players will get the Global Map Legend badge'''

import json
from pathlib import Path

from tabulate import tabulate

REGION = input('Region > ').lower()
FILENAME = input('Filename > ')
CLAN_AMOUNT = int(input('Clan amount > '))
PLAYER_AMOUNT = int(input('Player amount > '))

def main(file_path: Path) -> dict:
    gbadge_gamers = {}
    with open(file_path, encoding='utf-8') as file:
        data = json.load(file)

    for player_id, player_data in data.items():
        if all([player_data['player_rank'], player_data['clan_rank']]):
            if (player_data['player_rank'] <= (PLAYER_AMOUNT / 100)) \
            and (player_data['clan_rank'] <= (CLAN_AMOUNT / 100)):
                gbadge_gamers[player_id] = player_data

    return gbadge_gamers

if __name__ == '__main__':
    gbadges = main(Path(f'globalmap_data/{REGION}/{FILENAME}.json'))
    formatted = []

    for i, (player_id, player_data) in enumerate(gbadges.items(), 1):
        formatted.append([str(i).zfill(3), player_data['player_name'], player_data['player_rank'], player_data['clan_tag'], player_data['clan_rank']])

    with open(f'globalmap_data/{REGION}/_gbadges.txt', 'w', encoding='utf-8') as file:
        file.write(tabulate(formatted, headers=['Index', 'Name', 'Rank', 'Clan', 'Rank']))
