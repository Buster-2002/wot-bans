# World of Tanks competitive bans
Made by [Buster#5741](https://discord.com/users/764584777642672160)

## Introduction
The code found in `wot-bans/globalmap.py` and `wot-bans/ranked.py` are used to generate lists of banned people for global map events and ranked seasons respectively. Using this code I will attempt to do so whenever possible, and publish the lists. `wot-bans/gbadges.py` is used to generate a list of people who will receive a Global Map Legend badge and decals (top 1% clan and player by FP). `wot-bans/tankranking.py` is used to generate a ranking of clans by how many tanks they got for their members. All scripts require data that is obtained directly from the leaderboard API.

## Previous lists

**Ranked**
- Season 2022-01 : [EU](https://gist.github.com/Buster-2002/af6c23395fc9ac69091b856a2f79b57d)

**Global map**
- Thunderstorm : [EU](https://gist.github.com/Buster-2002/deb3995455dffb9aab1f0df1d8c67461)
- Rennaisance : [EU](https://gist.github.com/Buster-2002/d56985709696f0b057ccb90e278d6311)
- Confrontation : [ASIA](https://gist.github.com/Buster-2002/6bc04d5dac617a996822f4e27c5dee58) - [EU](https://gist.github.com/Buster-2002/ec2cee5c54d2f6fc773c66cd83c681d1) - [NA](https://gist.github.com/Buster-2002/d3b827135fc84779cc0267f4c56d33a9) - [RU](https://gist.github.com/Buster-2002/2540640cb2afe7cb92a6600dd9870fdc)

## Data gathering
For the sake of transparency, the raw data is included in this repo. What follows is an explanation on how the data is gathered and created, and under what scheme it is saved.

**Raw Leaderboard data**  
Gathered by saving the data obtained from each page of the leaderboard ([EU](worldoftanks.eu/en/clanwars/rating/alley/#wot&aof_rating=accounts&aof_filter=all&aof_page=0&aof_size=25), [NA](worldoftanks.com/en/clanwars/rating/alley/#wot&aof_rating=accounts&aof_filter=all&aof_page=0&aof_size=25), [RU](worldoftanks.ru/en/clanwars/rating/alley/#wot&aof_rating=accounts&aof_filter=all&aof_page=0&aof_size=25), [ASIA](worldoftanks.asia/en/clanwars/rating/alley/#wot&aof_rating=accounts&aof_filter=all&aof_page=0&aof_size=25))

`wot-bans/globalmap_data/{region}/{eventname}/{month}-{day}_{hour}-{minute}_data.json`  
`wot-bans/ranked_data/{region}/{eventname}/{month}-{day}_{hour}-{minute}_data.json`  

**Raw Banned data**  
Created by comparing two raw leaderboard data sets (checking which keys were removed). Note that you need both data from before and after the disqualifications propagated on the API.

`wot-bans/globalmap_data/{region}/{eventname}/banned.json`  
`wot-bans/ranked_data/{region}/{eventname}/banned.json`  

**Formatted data**  
Created by taking the raw banned data and formatting it in a way that is easily readable and appealing to look at (using MarkDown). Along with this I also show which clans had X+ members banned, and 
which players will now receive a tank as result of the bans.

`wot-bans/globalmap_data/{region}/{eventname}/formatted.md`  
`wot-bans/ranked_data/{region}/{eventname}/formatted.md`  
