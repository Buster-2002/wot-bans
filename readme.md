# World of Tanks competitive bans
Made by Buster#5741

## Introduction
The code found in `gm_bans.py` and `ranked_bans.py` are used to generate lists of banned people for global map events and ranked seasons respectively. Using this code I will attempt to do so whenever possible.

## Data gathering
For the sake of transparency, the raw data is included in this repo. What follows is an explanation on how the data is gathered and created, and under what scheme it is saved.

**Raw Leaderboard data**  
Gathered by saving the data for each page from the leaderboard API (which is also used on the leaderboards - [EU](worldoftanks.eu/en/clanwars/rating/alley/#wot&aof_rating=accounts&aof_filter=all&aof_page=0&aof_size=25), [NA](worldoftanks.com/en/clanwars/rating/alley/#wot&aof_rating=accounts&aof_filter=all&aof_page=0&aof_size=25), [RU](worldoftanks.ru/en/clanwars/rating/alley/#wot&aof_rating=accounts&aof_filter=all&aof_page=0&aof_size=25), [ASIA](worldoftanks.asia/en/clanwars/rating/alley/#wot&aof_rating=accounts&aof_filter=all&aof_page=0&aof_size=25))

`globalmap_data/region/eventname_%m-%d_%H-%M_data.json`  
`ranked_data/region/eventname_%m-%d_%H-%M_data.json`  

**Raw Banned data**  
Created by comparing two raw leaderboard data sets (checking which were removed). Note that you need both data from before and after the disqualifications propagated on the API.

`globalmap_data/region/eventname_banned.json`  
`ranked_data/region/eventname_banned.json`  

**Formatted data**  
Created by taking the raw banned data and formatting it in a way that is easily readable and appealing to look at (using MarkDown)

`globalmap_data/region/eventname_formatted.md`  
`ranked_data/region/eventname_formatted.md`  
