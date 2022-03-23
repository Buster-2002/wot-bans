# World of Tanks competitive bans
Made by [Buster#5741](https://discord.com/users/764584777642672160)

## Introduction
I will attempt to upload ban lists for each season of ranked and each global map event for each nation. **Use of the code, data and these lists falls under MIT license and are therefore free to use in any way you want.**

## Uses
- [`wot-bans/globalmap.py`](https://github.com/Buster-2002/wot-bans/blob/master/wot-bans/globalmap.py): Get/compare/format (ban) data for WoT Global Map events 
- [`wot-bans/ranked.py`](https://github.com/Buster-2002/wot-bans/blob/master/wot-bans/ranked.py): Get/compare/format (ban) data for WoT Ranked map events 
- [`wot-bans/tankranking.py`](https://github.com/Buster-2002/wot-bans/blob/master/wot-bans/tankranking.py): Rank clans by amounts of reward tanks for WoT Global Map events
- [`wot-bans/gbadges.py`](https://github.com/Buster-2002/wot-bans/blob/master/wot-bans/gbadges.py): List players who receive a GML badge for WoT Global Map events

## Previous lists

**Ranked**
- Season 2022-01 : [EU](https://gist.github.com/Buster-2002/af6c23395fc9ac69091b856a2f79b57d)
- Season 2022-03 : [ASIA](https://gist.github.com/Buster-2002/547c307758e2b3d722877d7bf03aedc9) - [EU](https://gist.github.com/Buster-2002/b7797c0f0bf0be7be3cb77687fe82d91) - [NA](https://gist.github.com/Buster-2002/952a651e2b1c5987326a76f592678ad9) - [RU](https://gist.github.com/Buster-2002/a6633faadd0e89777749859e1eca7e52)

**Global map**
- Thunderstorm : [EU](https://gist.github.com/Buster-2002/deb3995455dffb9aab1f0df1d8c67461)
- Rennaisance : [EU](https://gist.github.com/Buster-2002/d56985709696f0b057ccb90e278d6311)
- Confrontation : [ASIA](https://gist.github.com/Buster-2002/6bc04d5dac617a996822f4e27c5dee58) - [EU](https://gist.github.com/Buster-2002/ec2cee5c54d2f6fc773c66cd83c681d1) - [NA](https://gist.github.com/Buster-2002/d3b827135fc84779cc0267f4c56d33a9) - [RU](https://gist.github.com/Buster-2002/2540640cb2afe7cb92a6600dd9870fdc)

## Data gathering
For the sake of transparency, the raw data is included in this repo. What follows is an explanation on how the data is gathered and created, and under what scheme it is saved.

**Raw Leaderboard data**  
Gathered by saving the data obtained from each page of the leaderboard ([EU](https://worldoftanks.eu/en/clanwars/rating/alley/), [NA](https://worldoftanks.com/en/clanwars/rating/alley/), [RU](https://worldoftanks.ru/en/clanwars/rating/alley/), [ASIA](https://worldoftanks.asia/en/clanwars/rating/alley/) for global map and [EU](https://worldoftanks.eu/en/ratings/ranked/), [NA](https://worldoftanks.com/en/ratings/ranked/), [RU](https://worldoftanks.ru/ru/ratings/ranked/), [ASIA](https://worldoftanks.asia/en/ratings/ranked/) for ranked)

`wot-bans/globalmap_data/{region}/{eventname}/{month}-{day}_{hour}-{minute}_data.json`  
`wot-bans/ranked_data/{region}/{eventname}/{month}-{day}_{hour}-{minute}_data.json`  

**Raw Banned data**  
Created by comparing two raw leaderboard data sets (checking which account ids (the keys) were removed). Note that I require both the leaderboard data from before and after the disqualifications were propagated on the API.

`wot-bans/globalmap_data/{region}/{eventname}/banned.json`  
`wot-bans/ranked_data/{region}/{eventname}/banned.json`  

**Formatted data**  
Created by taking the raw banned data and formatting it in a way that is easily readable and appealing to look at (using MarkDown). Along with this I also show which clans had X+ members banned, and 
which players will now receive a tank as result of the bans if it is a Global Map ban list.

`wot-bans/globalmap_data/{region}/{eventname}/formatted.md`  
`wot-bans/ranked_data/{region}/{eventname}/formatted.md`  
