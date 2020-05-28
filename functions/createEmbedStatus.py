import discord
from discord.ext import commands
from elobot import watcher, getRegion
from elobot import client

master_list = []

def buildStrings():

    region = getRegion()

    master_list.clear()

    region_list = ["na1", "euw1", "kr", "oc1", "eun1", "jp1", "la1", "la2", "br1"]

    status_dict = {}
    # Create region info for each region
    for i in region_list:

        region_status = watcher.lol_status.shard_data(i)
        status_list = []
        status_tup = {}

        # Scrape status info for each of 4 services
        for j in region_status['services']:
            
            status_tup[j['name']] = j['status']
            status_dict[i] = status_tup

    # Jump into each region
    for i in status_dict:

        region_str = ''
        j_str = ''

        # Jump to each service
        for j in status_dict[i]:   

            j_str = j_str + j

            if status_dict[i][j] == 'online':
                emoji = client.get_emoji(709372443852275743)
                temp_str = f': {emoji}\n'
                j_str = j_str + temp_str

            else:
                emoji = client.get_emoji(709372456913207416)
                temp_str = f': {emoji}\n'
                j_str = j_str + temp_str

        region_str = j_str
        master_list.append(region_str)


async def createEmbed(ctx):
    
    s_status = "https://status.riotgames.com/?locale=en_US&product=leagueoflegends"
    title_str = "Riot Server Status"

    embed = discord.Embed(title=title_str, url=s_status, colour=discord.Colour(0xff005c), description="Shows full server status sorted by region and Riot service.")
    embed.set_thumbnail(url='')
    embed.set_author(name="EloBot", icon_url="https://i.imgur.com/rqXHyI8.png")


    embed.add_field(name="**North America**", value=master_list[0], inline=True)

    embed.add_field(name="**Europe West**", value=master_list[1], inline=True)

    embed.add_field(name="**Korea**", value=master_list[2], inline=True)

    embed.add_field(name="**Oceania**", value=master_list[3], inline=True)

    embed.add_field(name="**Europe Nordic**", value=master_list[4], inline=True)

    embed.add_field(name="**Japan**", value=master_list[5], inline=True)

    embed.add_field(name="**L.A. North**", value=master_list[6], inline=True)

    embed.add_field(name="**L.A. South**", value=master_list[7], inline=True)

    embed.add_field(name="**Brazil**", value=master_list[8], inline=True)

    # Footer
    embed.set_footer(text="Created by Sam and Alek", icon_url="https://i.imgur.com/rqXHyI8.png")

    await ctx.send(embed=embed)