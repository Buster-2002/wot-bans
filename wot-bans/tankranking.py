#!/usr/bin/env python3
#-*- coding: utf-8 -*-
'''tankranking.py: Ranks clans with the amount of tanks they will receive

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
from collections import Counter, defaultdict
from pathlib import Path

from tabulate import tabulate

__author__ = 'Buster#5741'
__license__ = 'MIT'

EVENT = input('Event name > ').lower()
REGION = input('Region > ').lower()
FILENAME = input('Post ban data filename > ')

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
    tankranking = main(Path(f'globalmap_data/{REGION}/{EVENT}/{FILENAME}.json'))
    formatted = []

    for i, (clan_tag, data) in enumerate(tankranking.items(), 1):
        if len(data) == 2: # data[0] is amount of clan members that participated and data[1] is how many got a tank
            formatted.append([str(i).zfill(3), clan_tag, data[0], data[1], f'{(data[0] / data[1]) * 100:.2f}%'])

    with open(f'globalmap_data/{REGION}/{EVENT}/tankranking.txt', 'w', encoding='utf-8') as file:
        file.write(tabulate(
            tabular_data=formatted,
            headers=['Rank', 'Clan', 'Tanks', 'Participants', 'Rate'],
            tablefmt='presto',
            numalign='left'
        ))
