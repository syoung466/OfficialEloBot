import discord
from discord.ext import commands
from elobot import watcher, getRegion, getMongo
from functions.createEmbedUser import createEmbed
from collections import Counter
from Resources.pos_mapping import pos_dict
from Resources.emoji_mapping import rank_dict
from functions.ddragon import dragonVersion

ranked_result_list = []
account_result_list = []

def outputRank(arg):

	region = getRegion()

	# Pull account info and ranked info
	try:
		account = watcher.summoner.by_name(region, arg)    
		ranked_result_list.append(account)  

		ranked_stats = watcher.league.by_summoner(region, account['id'])    
		ranked_result_list.append(ranked_stats)

		# Create Profile Icon ID
		version = dragonVersion()
		embed_str = f'http://ddragon.leagueoflegends.com/cdn/{version}/img/profileicon/'

		embed_icon =  "{}{}.png".format(embed_str, account['profileIconId'])
	
		ranked_result_list.append(embed_icon)

		# Create output format
		ranked_str = "{0} **Solo/Duo**: {1} {2} - {3}LP\n{4} **Flex**: {5} {6} - {7}LP"
		unranked = 'UNRANKED'
		s = '' 

		# Check to see if user's ranked list is populated (has a rank)
		# User has no ranked info
		if not ranked_stats:
			emoji_u = "<:unrank_alt:710104565143568404>"
			unrank_final_str = ranked_str.format(emoji_u, unranked, s, s, emoji_u, unranked, s, s)
			temp_str = unrank_final_str.replace("LP", '')
			final_str = temp_str.replace("-", '')
		
			ranked_result_list.append(final_str)

		# User is ranked in only ONE queue
		elif len(ranked_stats) == 1:
			if (ranked_stats[0]['queueType'] == 'RANKED_FLEX_SR'):
				emoji_u = "<:unrank_alt:710104565143568404>" 
				flex_only_str = ranked_str.format(emoji_u, unranked, s, 0, rank_dict.get(ranked_stats[0]['tier']),
								ranked_stats[0]['tier'], ranked_stats[0]['rank'], ranked_stats[0]['leaguePoints'])                                
							
				ranked_result_list.append(flex_only_str)

			else:
				emoji_u = "<:unrank_alt:710104565143568404>"
				solo_only_str = ranked_str.format(rank_dict.get(ranked_stats[0]['tier']), ranked_stats[0]['tier'], ranked_stats[0]['rank'], 
												  ranked_stats[0]['leaguePoints'], emoji_u, unranked, s, s)
			
				ranked_result_list.append(solo_only_str)

		# User is ranked in both queues
		else:
			for i in range(0, 2):
				if ranked_stats[i]['queueType'] == 'RANKED_SOLO_5x5':  
					emoji_s = rank_dict.get(ranked_stats[i]['tier'])              
					tier_sd = ranked_stats[i]['tier']
					rank_sd = ranked_stats[i]['rank']
					points_sd = ranked_stats[i]['leaguePoints']

				if ranked_stats[i]['queueType'] == 'RANKED_FLEX_SR':    
					emoji_f = rank_dict.get(ranked_stats[i]['tier'])          
					tier_flex = ranked_stats[i]['tier']
					ranked_stats[i]['tier']
					rank_flex = ranked_stats[i]['rank']
					points_flex = ranked_stats[i]['leaguePoints']

			all_rank_str = ranked_str.format(emoji_s, tier_sd, rank_sd, points_sd, 
											 emoji_f, tier_flex, rank_flex, points_flex)
		
			ranked_result_list.append(all_rank_str)

	except:
	
		ranked_result_list.append(0)
	
def outputAccount(arg):

	region = getRegion()
 
	account = watcher.summoner.by_name(region, arg)
	acc_id = account['id']
	acc_enc_id = account['accountId']

	acc_level = account['summonerLevel']
	account_result_list.append(acc_level)

	acc_mastery = watcher.champion_mastery.scores_by_summoner(region, acc_id)
	account_result_list.append(acc_mastery)

	matchlist = watcher.match.matchlist_by_account(region, acc_enc_id, queue=[400, 420, 430, 440], begin_index=0, end_index=100)

	# (LANE, ROLE)
	lane_list = []
	role_list = []
	merge_list = []

	# Creating lane and role lists
	for i in matchlist['matches']:
		lane_list.append(i['lane'])
		role_list.append(i['role'])

	# Merge lists as tuples into one list
	for i in range(0, len(lane_list)):
		temp_tuple = (lane_list[i], role_list[i])
		merge_list.append(temp_tuple)

	# Determine most common tuple
	mc_tuple = Counter(merge_list).most_common(1)

	# Create most common pos string
	pos_str = ''
	for key, value in pos_dict.items():
		if (mc_tuple[0][0] == key):
			pos_str = value
			break
		else:
			pos_str = "UNDETECTED"

	account_result_list.append(pos_str)


	# Create final embed string
	account_final_str = "**Account Level**: {}\n**Total Mastery**: {}\n**Most Played**: {}".format(account_result_list[0], account_result_list[1], account_result_list[2])
	account_result_list.append(account_final_str)

class User(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.command()
	async def user(self, ctx, *args):

		# Ensure list is cleared for each use of command
	
		ranked_result_list.clear()
		account_result_list.clear()
		# Store acc name without spaces
		acc_name = "".join(args)

		async with ctx.typing():
			try:
				outputRank(acc_name)
				outputAccount(acc_name)

				# Store account name with spaces
				acc_name_sp = ranked_result_list[0]['name']

				# Create and message final result
				
				await createEmbed(acc_name, acc_name_sp,
								ranked_result_list[2], account_result_list[3],
								ranked_result_list[3], ctx)

				elobot_usg = getMongo()
				elobot_usg.update_one({"command":"user"}, {"$inc": {"count": 1}}, upsert=True)  

			except Exception as e:
				await ctx.send("Cannot find account's information!")
				print(e)

def setup(client):
	client.add_cog(User(client))
