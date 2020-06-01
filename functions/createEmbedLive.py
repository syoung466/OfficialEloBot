import discord
from discord.ext import commands
from elobot import watcher, getRegion
from Resources.queue_mapping import que_list
from Resources.region_mapping import riot_dict
from Resources.emoji_mapping import rank_dict
from Resources.rank_map import rank_avg_dict
from functions.ddragon import dragonVersion
import urllib.request
import json
import time

master_list = []
# 0 - Acc Name
# 1 - Acc Name_Sp
# 2 - Game Type
# 3 - Champ Icon URL
# 4 - Blue Team String
# 5 - Red Team String
# 6 - Blue Rank String
# 7 - Red Rank String
# 8 - Blue Average Rank
# 9 - Red Average Rank

def buildStrings(args): 

	region = getRegion()

	master_list.clear()

	acc_name = "".join(args)
	master_list.append(acc_name)

	account = watcher.summoner.by_name(region, acc_name)
	acc_name_sp = account['name']
	master_list.append(acc_name_sp)

	acc_id = account['id']


	live_game_info = watcher.spectator.by_summoner(region, acc_id)
	game_queue_id = live_game_info['gameQueueConfigId']

	# Calculate elapsed game time
	start_time = round(time.time())
	game_start = live_game_info['gameStartTime'] / 1000
	game_start = start_time - game_start

	days, rem_h = divmod(game_start, 86400)
	hours, rem_m = divmod(rem_h, 3600)
	mins, rem_s = divmod(rem_m, 60)
	secs, rem_ms = divmod(rem_s, 60)

	time_str = ' | {}:{:2}'.format(round(mins), round(rem_s))

	# Search que_list for game type
	curr_game = ""
	for i in que_list:
		if i["queueId"] == game_queue_id:
			temp_str = "**{}**{}".format(i["map"], i["description"])
			curr_game = temp_str
			break

	curr_game += time_str
	master_list.append(curr_game) 
	buildTeamStr(account, acc_id, live_game_info)

def buildTeamStr(account, acc_id, live_game_info):

	region = getRegion()

	version = dragonVersion()

	champ_url = f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
	url_get_champ = urllib.request.urlopen(champ_url).read().decode()
	champ_data = json.loads(url_get_champ)

	# Create blue side lists    
	blue_list = []
	for i in live_game_info["participants"][:5]:
		champ_key = i["championId"]
		for j in champ_data["data"]:
			if str(champ_key) == champ_data["data"][j]["key"]:                
				blue_list.append((i["summonerName"], champ_data["data"][j]["name"], i["summonerId"], champ_key))

	# Create red side lists
	red_list = []
	for i in live_game_info["participants"][5:]:
		champ_key = i["championId"]
		for j in champ_data["data"]:
			if str(champ_key) == champ_data["data"][j]["key"]:                
				red_list.append((i["summonerName"], champ_data["data"][j]["name"], i["summonerId"], champ_key)) 


	# Generate Champion Icon URL
	comb_list = blue_list + red_list
	champ_key = 0

	for i in comb_list:
		if acc_id == i[2]:
			champ_key = i[3]

	img_str = ""

	for i in champ_data["data"]:
		if str(champ_key) == champ_data["data"][i]["key"]:
			temp_str = champ_data["data"][i]["image"]["full"]
			img_str = temp_str


	champ_icon_url = f"http://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{img_str}"
	master_list.append(champ_icon_url)

	# Building complete team strings
	b_team_str = ""
	r_team_str = ""

	for i in blue_list:
		temp_str = "**{}** - {}\n".format(i[0], i[1])
		b_team_str += temp_str

	master_list.append(b_team_str)

	for i in red_list:
		temp_str = "**{}** - {}\n".format(i[0], i[1])
		r_team_str += temp_str

	master_list.append(r_team_str)

	# Build rank info for blue team
	b_rank_str = ""
	b_rank_pts = []

	for i in blue_list:
		temp_rank = watcher.league.by_summoner(region, i[2])
		if not temp_rank:
			emoji_u = "<:unrank_alt:710104565143568404>"
			temp_str = f'{emoji_u} **UNRANKED**\n'
			b_rank_str += temp_str

		else:
			if len(temp_rank) == 1:
				for j in temp_rank:
					if j["queueType"] == "RANKED_SOLO_5x5":
						temp_str = "{} **Solo/Duo**: {} {}\n".format(rank_dict.get(j["tier"]), j["tier"], j["rank"])
						b_rank_str += temp_str
						pt_str = j["tier"] + ' ' + j["rank"]
						b_rank_pts.append(rank_avg_dict.get(pt_str))
						break

					else:
						temp_str = "{} **Flex**: {} {}\n".format(rank_dict.get(j["tier"]), j["tier"], j["rank"])
						b_rank_str += temp_str
						pt_str = j["tier"] + ' ' + j["rank"]
						b_rank_pts.append(rank_avg_dict.get(pt_str))
						break

			if len(temp_rank) == 2:
				for j in temp_rank:
					if j["queueType"] == "RANKED_SOLO_5x5":
						temp_str = "{} **Solo/Duo**: {} {}\n".format(rank_dict.get(j["tier"]), j["tier"], j["rank"])
						b_rank_str += temp_str
						pt_str = j["tier"] + ' ' + j["rank"]
						b_rank_pts.append(rank_avg_dict.get(pt_str))
						break


	master_list.append(b_rank_str)

	# Build rank info for red team
	r_rank_str = ""
	r_rank_pts = []

	for i in red_list:
		temp_rank = watcher.league.by_summoner(region, i[2])

		if not temp_rank:
			emoji_u = "<:unrank_alt:710104565143568404>"
			temp_str = f'{emoji_u} **UNRANKED**\n'
			r_rank_str += temp_str

		else:
			if len(temp_rank) == 1:
				for j in temp_rank:
					if j["queueType"] == "RANKED_SOLO_5x5":
						temp_str = "{} **Solo/Duo**: {} {}\n".format(rank_dict.get(j["tier"]), j["tier"], j["rank"])
						r_rank_str += temp_str
						pt_str = j["tier"] + ' ' + j["rank"]
						print(pt_str)
						r_rank_pts.append(rank_avg_dict.get(pt_str))
						break

					else:
						temp_str = "{} **Flex**: {} {}\n".format(rank_dict.get(j["tier"]), j["tier"], j["rank"])
						r_rank_str += temp_str
						pt_str = j["tier"] + ' ' + j["rank"]
						print(pt_str)
						r_rank_pts.append(rank_avg_dict.get(pt_str))
						break

			if len(temp_rank) == 2:
				for j in temp_rank:
					if j["queueType"] == "RANKED_SOLO_5x5":
						temp_str = "{} **Solo/Duo**: {} {}\n".format(rank_dict.get(j["tier"]), j["tier"], j["rank"])
						r_rank_str += temp_str
						pt_str = j["tier"] + ' ' + j["rank"]
						print(pt_str)
						r_rank_pts.append(rank_avg_dict.get(pt_str))
						break

	master_list.append(r_rank_str)

	if sum(b_rank_pts) == 0:
		master_list.append("Tier Average: UNRANKED")
	else:
		blue_avg = round(sum(b_rank_pts) / len(b_rank_pts))
		for k, v in rank_avg_dict.items():
			if v == blue_avg:
				blue_str = f"Tier Average: {k}"
				master_list.append(blue_str)

	if sum(r_rank_pts) == 0:
		master_list.append("Tier Average: UNRANKED")
	else:
		red_avg = round(sum(r_rank_pts) / len(r_rank_pts))
		for k, v in rank_avg_dict.items():
			if v == red_avg:
				red_str = f"Tier Average: {k}"
				master_list.append(red_str)
	
	print(len(master_list))

async def createEmbed(ctx):
	
	region = getRegion()
	op_gg = ''

	if region == "KR":
		op_gg += "https://www.op.gg/summoner/userName={}".format(master_list[0])

	else:
		reg = riot_dict.get(region)
		op_gg += "https://{}.op.gg/summoner/userName={}".format(reg, master_list[0])

	title_str = "Live Game Information for {}".format(master_list[1])

	embed = discord.Embed(title=title_str, url=op_gg, colour=discord.Colour(0xff005c), description=master_list[2])
	embed.set_thumbnail(url=master_list[3])
	embed.set_author(name="EloBot", icon_url="https://i.imgur.com/rqXHyI8.png")

	# Your Team
	embed.add_field(name="**Blue Side**", value=master_list[4], inline=True)

	# Your Team Ranks
	embed.add_field(name=master_list[8], value=master_list[6], inline=True)
	embed.add_field(name="\u200b", value = "\u200b")

	# Enemy Team
	embed.add_field(name="**Red Side**", value=master_list[5], inline=True)

	# Enemy Team Ranks
	embed.add_field(name=master_list[9], value=master_list[7], inline=True)
	embed.add_field(name="\u200b", value = "\u200b")

	# Footer
	embed.set_footer(text="Click username to view OP.GG stats | Created by Sam and Alek", icon_url="https://i.imgur.com/rqXHyI8.png")

	await ctx.send(embed=embed)