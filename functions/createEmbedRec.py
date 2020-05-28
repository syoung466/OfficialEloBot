import discord
from discord.ext import commands
from elobot import watcher, getRegion
from Resources.region_mapping import riot_dict
from functions.ddragon import dragonVersion

master_list = []
# 0 - Acc Name
# 1 - Acc Name Sp
# 2 - Game Breakdown String
# 3 - Most Kills


def buildStrings(args):

    region = getRegion()

    master_list.clear()
    acc_name = "".join(args)
    master_list.append(acc_name)

    account = watcher.summoner.by_name(region, acc_name)
    acc_name_sp = account['name']
    master_list.append(acc_name_sp)

    acc_id = account['id']
    acc_enc_id = account['accountId']
    match_list = watcher.match.matchlist_by_account(region, acc_enc_id, queue=[400, 420, 430, 440, 450, 700], begin_index=0, end_index=12)

    # Create game ID and Q type lists
    game_id_list = []
    q_type_list = []

    for i in match_list['matches']:
        game_id_list.append(i['gameId'])
        q_type_list.append(i['queue'])

    # Count # of Aram vs SR games
    aram_count = 0
    sr_count = 0
    for i in q_type_list:        
        if i == 450:
            aram_count += 1
        else:
            sr_count += 1

    # Generate Win/Loss String
    win = loss = team_id = part_id = 0
    kill_list, death_list, assist_list, vision_list, kill_spree, penta_list = ([] for i in range(6))

    for i in game_id_list:
        game_info = watcher.match.by_id(region, i)
        
        for j in game_info['participantIdentities']:

            if acc_id == j['player']['summonerId']:
                part_id = j['participantId']
                if j['participantId'] < 6:
                    team_id = 100
                else:
                    team_id = 200

        for i in game_info['teams']:
            if i['teamId'] == team_id:
                if i['win'] == 'Win':
                    win += 1
                else:
                    loss += 1


        # Loop through again to avoid so much fucking nesting!!

        for k in game_info['participants']:
            if part_id == k['participantId']:
                kill_list.append(k['stats']['kills'])
                death_list.append(k['stats']['deaths'])
                assist_list.append(k['stats']['assists'])
                vision_list.append(k['stats']['visionScore'])
                kill_spree.append(k['stats']['largestKillingSpree'])
                penta_list.append(k['stats']['pentaKills'])  


    # Create W/L and Win Percentage and KDA
    percent = win / len(game_id_list) * 100
    kda = (sum(kill_list) + sum(assist_list)) / sum(death_list)

    game_breakdown_str = "Summoners Rift: **{}** | Howling Abyss: **{}**\n".format(sr_count, aram_count)
    w_l_str = "Wins: **{}** | Losses: **{}** | Win Rate: **{}%** | **{} KDA**".format(win, loss, round(percent, 2), round(kda, 2))

    game_breakdown_str += w_l_str
    master_list.append(game_breakdown_str)

    # Creating Field Strings
    most_kills = "⚔️ {}".format(max(kill_list))
    fewest_deaths = "☠ {}".format(min(death_list))
    most_assists = "🩹 {}".format(max(assist_list))
    most_vision = "👁 {}".format(max(vision_list))
    most_kspree = "🧨 {}".format(max(kill_spree))
    penta_kills = "🔥 {}".format(sum(penta_list))

    master_list.extend([most_kills, fewest_deaths, most_assists, most_vision, most_kspree, penta_kills])

    version = dragonVersion()

    embed_str = f'http://ddragon.leagueoflegends.com/cdn/{version}/img/profileicon/'
    embed_icon =  "{}{}.png".format(embed_str, account['profileIconId'])
    master_list.append(embed_icon)
    

async def createEmbed(ctx):

    region = getRegion()
    op_gg = ''

    if region == "KR":
        op_gg += "https://www.op.gg/summoner/userName={}".format(master_list[0])

    else:
        reg = riot_dict.get(region)
        op_gg += "https://{}.op.gg/summoner/userName={}".format(reg, master_list[0])

    title_str = "Recent Match Stats for {}".format(master_list[1])

    embed = discord.Embed(title=title_str, url=op_gg, colour=discord.Colour(0xff005c), description=master_list[2])
    embed.set_thumbnail(url=master_list[9])
    embed.set_author(name="EloBot", icon_url="https://i.imgur.com/rqXHyI8.png")

    
    embed.add_field(name="**Most Kills**", value=master_list[3], inline=True)

    embed.add_field(name="**Fewest Deaths**", value=master_list[4], inline=True)

    embed.add_field(name="**Most Assists**", value=master_list[5], inline=True)

    embed.add_field(name="**Highest Vision**", value=master_list[6], inline=True)

    embed.add_field(name="**Best Killing Spree**", value=master_list[7], inline=True)

    embed.add_field(name="**Pentakills**", value=master_list[8], inline=True)

    # Footer
    embed.set_footer(text="Click username to view OP.GG stats | Created by Sam and Alek", icon_url="https://i.imgur.com/rqXHyI8.png")

    await ctx.send(embed=embed)