import discord
from discord.ext import commands
from elobot import watcher, getRegion
from Resources.region_mapping import riot_dict
from Resources.emoji_mapping import mast_dict
from Resources.champ_mapping import champ_map
from functions.ddragon import dragonVersion
import urllib.request
import json
import time

master_list = []
# 0 - Acc Name
# 1 - Acc Name Sp
# 2 - Profile Icon URL
# 3 - Champ name list
# 4 - Mastery List
# 5 - Last Play List
# 6 - Footer String

def buildStrings(args):

    region = getRegion()

    master_list.clear()

    acc_name = "".join(args)
    master_list.append(acc_name)

    # SCRAPE GENERAL ACC INFO
    account = watcher.summoner.by_name(region, acc_name)
    acc_name_sp = account['name']
    master_list.append(acc_name_sp)

    version = dragonVersion()

    # CREATE PROFILE ICON URL
    embed_str = f'http://ddragon.leagueoflegends.com/cdn/{version}/img/profileicon/'
    embed_icon =  "{}{}.png".format(embed_str, account['profileIconId'])
    master_list.append(embed_icon)

    # CREATE CHAMP INFO JSON
    champ_url = f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    url_get_champ = urllib.request.urlopen(champ_url).read().decode()
    champ_data = json.loads(url_get_champ)

    acc_id = account['id']
    
    mast_info = watcher.champion_mastery.by_summoner(region, acc_id)

    # Create names list
    count = 0
    champ_str = ''
    for i in mast_info[:5]:
        champ_id = i['championId']
        count += 1

        for j in champ_data["data"]:
            if str(champ_id) == champ_data["data"][j]["key"]:
                champ_name = champ_data["data"][j]["name"]
                temp_str = "**{}**. {}\n".format(count, champ_name)
                champ_str += temp_str

    master_list.append(champ_str)

    
    # Create Mastery Point List
    mast_str = ''
    for i in mast_info[:5]:
        champ_lvl = i['championLevel']
        mast_pts = i['championPoints']
        temp_str = "**{}**: {:,}\n".format(mast_dict.get(champ_lvl), mast_pts)
        mast_str += temp_str

    master_list.append(mast_str)

    # Create time since last played list
    time_str = ''
    for i in mast_info[:5]:
        start_time = round(time.time())
        last_play = i['lastPlayTime'] / 1000
        last_play = start_time - last_play

        days, rem_h = divmod(last_play, 86400)
        hours, rem_m = divmod(rem_h, 3600)
        mins, rem_s = divmod(rem_m, 60)

        temp_str = '**{}** days **{}** hours **{}** mins ago\n'.format(round(days), round(hours), round(mins))
        time_str += temp_str

    master_list.append(time_str)

    # Get total champs played and total mastery levels
    total_played = len(mast_info)
    tot_acc_mast = watcher.champion_mastery.scores_by_summoner(region, acc_id)
    
    # Get total mastery points
    tot_mast_pts = 0
    for i in mast_info:
        tot_mast_pts += i['championPoints']


    footer_str = "**Champions**: {} | **Mastery Levels**: {} | **Total Points**: {:,}".format(total_played, tot_acc_mast, tot_mast_pts)

    master_list.append(footer_str)



async def createEmbed(ctx):

    region = getRegion()
    lg_graphs = ''
    name = ''

    name = master_list[1].replace(' ', '+')
    
    reg = riot_dict.get(region)
    lg_graphs += "https://www.leagueofgraphs.com/summoner/{}/{}".format(reg, name)

    title_str = "Champion Mastery for {}".format(master_list[1])

    embed = discord.Embed(title=title_str, url=lg_graphs, colour=discord.Colour(0xff005c), description="Shows champion mastery information for a given summoner.")
    embed.set_thumbnail(url=master_list[2])
    embed.set_author(name="EloBot", icon_url="https://i.imgur.com/rqXHyI8.png")

    # Champ List
    embed.add_field(name="**Top Champs  |**", value=master_list[3], inline=True)

    # Mastery List
    embed.add_field(name="**Mastery Points  |**", value=master_list[4], inline=True)

    # Last Played
    embed.add_field(name="**Last Played**", value=master_list[5], inline=True)

    embed.add_field(name="**Account Totals**", value=master_list[6], inline=True)

    # Footer
    embed.set_footer(text="Click username to view League of Graphs | Created by Sam and Alek", icon_url="https://i.imgur.com/rqXHyI8.png")

    await ctx.send(embed=embed)



# Specific Mastery Point String
async def specific(ctx, *args):
    spec_mast_list = []
    region = getRegion()
    args_str = ''.join(args)
    arg_list = args_str.split('-')
    acc_name = arg_list[0]
    champ_name = arg_list[1].lower()

    account = watcher.summoner.by_name(region, acc_name)
    acc_name_sp = account['name']
    acc_id = account['id']
    champ_id = champ_map.get(champ_name)[0]
    champ_name_sp = champ_map.get(champ_name)[1]

    spec_mast_dict = watcher.champion_mastery.by_summoner_by_champion(region, acc_id, champ_id)

    # Create Mastery Point List
    mast_str = ''

    champ_lvl = spec_mast_dict["championLevel"]
    champ_played = spec_mast_dict['lastPlayTime']
    champ_pts = spec_mast_dict['championPoints']
    temp_str = "**{}**: {:,}\n".format(mast_dict.get(champ_lvl), champ_pts)
    mast_str += temp_str

    # Create time since last played list
    time_str = ''
    start_time = round(time.time())
    last_play = champ_played / 1000
    last_play = start_time - last_play

    days, rem_h = divmod(last_play, 86400)
    hours, rem_m = divmod(rem_h, 3600)
    mins, rem_s = divmod(rem_m, 60)

    temp_str = '**{}** days **{}** hours **{}** mins ago\n'.format(round(days), round(hours), round(mins))
    time_str += temp_str

    spec_mast_list.append(champ_name_sp)
    spec_mast_list.append(acc_name_sp)
    spec_mast_list.append(time_str)
    spec_mast_list.append(mast_str)

    await createSpecificEmbed(ctx, spec_mast_list, account)

async def createSpecificEmbed(ctx, spec_list, account):    

    version = dragonVersion()

    title_str = f'Mastery on {spec_list[0]} for {spec_list[1]}'

    embed_str = f'http://ddragon.leagueoflegends.com/cdn/{version}/img/profileicon/'
    embed_icon =  "{}{}.png".format(embed_str, account['profileIconId'])

    embed = discord.Embed(colour=discord.Colour(0xff005c))
    embed.set_author(name=title_str, icon_url=embed_icon)

    # Mastery List
    embed.add_field(name="**Mastery Points**", value=spec_list[3], inline=True)

    # Last Played
    embed.add_field(name="**Last Played**", value=spec_list[2], inline=True)

    embed.set_footer(text="Created by Sam and Alek", icon_url="https://i.imgur.com/rqXHyI8.png")

    await ctx.send(embed=embed)



    
        
