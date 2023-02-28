'''check_changes.py: Check if the total amount of pages has changed.

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

import requests
from colorama import Fore
from playsound import playsound
from utils import print_message

SESSION = requests.Session()
SESSION.headers = {'x-requested-with': 'XMLHttpRequest'}

def main(url: str, reference_amount: int, check_interval: int) -> None:
    while True:
        print_message('Checking for changes...')
        r = SESSION.get(url)
        json = r.json()
        page_count = json.get('pages_count')

        if json.get('status') == 'ok':
            if page_count == reference_amount:
                print_message(f'The amount of pages has not changed: {page_count}.', colour=Fore.GREEN)

            else:
                print_message(f'The amount of pages has changed: {page_count}.', colour=Fore.RED)

                for _ in range (3):
                    playsound('alert.wav')
                    time.sleep(4)

                break

        else:
            error_code = json.get('code', 'N/A')
            print_message(f'API error (HTTP {error_code}), trying again in {check_interval}s...', colour=Fore.RED)

        time.sleep(check_interval)

if __name__ == '__main__':
    # Use page size 10, which is the minimum allowed for this API endpoint.
    # So at least 10 people would have to be removed for this to work.
    main(
        url='https://worldoftanks.eu/en/clanwars/rating/alley/users/?event_id=we_2023&front_id=we_2023_bg&page=0&page_size=10',
        reference_amount=6319,
        check_interval=30
    )