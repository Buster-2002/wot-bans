#!/usr/bin/env python3
#-*- coding: utf-8 -*-
'''gbadges.py: Calculates which players will get the Global Map Legend badge'''

import json
from pathlib import Path

REGION = input('Region > ')
FILENAME = input('Filename > ')
CLAN_AMOUNT = int(input('Clan amount > '))
PLAYER_AMOUNT = int(input('Player amount > '))

def main(file_path: Path):
    gbadge_gamers = {}
    with open(file_path, encoding='utf-8') as file:
        data = json.load(file)

    for player_id, player_data in data.items():
        if (player_data['player_rank'] <= (PLAYER_AMOUNT / 100)) \
        and (player_data['clan_rank'] <= (CLAN_AMOUNT / 100)):
            gbadge_gamers[player_id] = player_data
            print(player_data['player_name'])

    return gbadge_gamers


if __name__ == '__main__':
    main(Path(f'globalmap_data/{REGION}/{FILENAME}.json'))