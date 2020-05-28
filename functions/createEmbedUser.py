import discord
from discord.ext import commands
from Resources.region_mapping import riot_dict
from elobot import getRegion

async def createEmbed(name, name_sp, icon_url, acc_str, ranked_str, ctx):  

    # Create account specific op.gg url
    region = getRegion()
    op_gg = ''

    if region == "KR":
        op_gg += "https://www.op.gg/summoner/userName={}".format(name)

    else:
        reg = riot_dict.get(region)
        op_gg += "https://{}.op.gg/summoner/userName={}".format(reg, name)

    title_str = "Account Information for {}".format(name_sp)
    
    # General embed info
    embed = discord.Embed(title=title_str, colour=discord.Colour(0xff005c), url=op_gg, description="Shows current account information for a given summoner.")
    embed.set_thumbnail(url=icon_url)
    embed.set_author(name="EloBot", icon_url="https://i.imgur.com/rqXHyI8.png")
    embed.set_footer(text="Click username to view OP.GG stats | Created by Sam and Alek", icon_url="https://i.imgur.com/rqXHyI8.png")

    # Account info field
    embed.add_field(name="**Account Stats**", value=acc_str)

    # Ranked info field
    embed.add_field(name="**Ranked Stats**", value=ranked_str)
    
    await ctx.send(embed=embed)


