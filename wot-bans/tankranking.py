#!/usr/bin/env python3
#-*- coding: utf-8 -*-
'''tankranking.py: Ranks clans with the amount of tanks they will receive'''

import json
from collections import Counter, defaultdict
from pathlib import Path

from tabulate import tabulate

EVENT = input('Event name > ').lower()
REGION = input('Region > ').lower()
FILENAME = input('Filename > ')

def main(file_path: Path) -> dict:
    tank_ranking = Counter()
    clan_participating = Counter()

    with open(file_path, encoding='utf-8') as file:
        data = json.load(file)

    for player_data in data.values():
        clan_tag = player_data['clan_tag']
        if clan_tag is not None:
            if player_data['receives_tank'] is True:
                tank_ranking[clan_tag] += 1
            clan_participating[clan_tag] += 1

    merged = defaultdict(list)
    for d in (dict(tank_ranking.most_common()), dict(clan_participating)):
        for k, v in d.items():
            merged[k].append(v)

    return merged

if __name__ == '__main__':
    tankranking = main(Path(f'globalmap_data/{REGION}/{FILENAME}.json'))
    formatted = []

    for i, (clan_tag, data) in enumerate(tankranking.items(), 1):
        if len(data) == 2: # data[0] is amount of clan members that participated and data[1] is how many got a tank
            formatted.append([str(i).zfill(3), clan_tag, data[0], data[1], f'{(data[0] / data[1]) * 100:.2f}%'])

    with open(f'globalmap_data/{REGION}/{EVENT}_tankranking.txt', 'w', encoding='utf-8') as file:
        file.write(tabulate(formatted, headers=['Rank', 'Clan', 'Tanks', 'Participants', 'Rate']))
