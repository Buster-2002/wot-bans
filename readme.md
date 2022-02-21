# World of Tanks competitive bans
Made by [Buster#5741](https://discord.com/users/764584777642672160)

## Introduction
The code found in `wot-bans/globalmap.py` and `wot-bans/ranked.py` are used to generate lists of banned people for global map events and ranked seasons respectively. Using this code I will attempt to do so whenever possible, and publish the lists.

## Previous lists

**Ranked**
- Season 2022-01 : [EU](https://gist.github.com/Buster-2002/af6c23395fc9ac69091b856a2f79b57d)

**Global map**
- Thunderstorm : [EU](https://gist.github.com/Buster-2002/deb3995455dffb9aab1f0df1d8c67461)
- Rennaisance : [EU](https://gist.github.com/Buster-2002/d56985709696f0b057ccb90e278d6311)

## Data gathering
For the sake of transparency, the raw data is included in this repo. What follows is an explanation on how the data is gathered and created, and under what scheme it is saved.

**Raw Leaderboard data**  
Gathered by saving the data for each page from the leaderboard API (which is also used on the leaderboards : [EU](worldoftanks.eu/en/clanwars/rating/alley/#wot&aof_rating=accounts&aof_filter=all&aof_page=0&aof_size=25), [NA](worldoftanks.com/en/clanwars/rating/alley/#wot&aof_rating=accounts&aof_filter=all&aof_page=0&aof_size=25), [RU](worldoftanks.ru/en/clanwars/rating/alley/#wot&aof_rating=accounts&aof_filter=all&aof_page=0&aof_size=25), [ASIA](worldoftanks.asia/en/clanwars/rating/alley/#wot&aof_rating=accounts&aof_filter=all&aof_page=0&aof_size=25))

`wot-bans/globalmap_data/region/eventname_{month}-{day}_{hour}-{minute}_data.json`  
`wot-bans/ranked_data/region/eventname_{month}-{day}_{hour}-{minute}_data.json`  

**Raw Banned data**  
Created by comparing two raw leaderboard data sets (checking which were removed). Note that you need both data from before and after the disqualifications propagated on the API.

`wot-bans/globalmap_data/region/eventname_banned.json`  
`wot-bans/ranked_data/region/eventname_banned.json`  

**Formatted data**  
Created by taking the raw banned data and formatting it in a way that is easily readable and appealing to look at (using MarkDown). I also calculate which clans had 10 + of their members banned, and show those clans in a separate table

`wot-bans/globalmap_data/region/eventname_formatted.md`  
`wot-bans/ranked_data/region/eventname_formatted.md`  
