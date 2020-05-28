import discord
from discord.ext import commands
from elobot import getMongo


class Help(commands.Cog):

	def __init__(self, client):
		self.client = client

	
	@commands.command(pass_context=True, aliases=['h'])
	async def help(self, ctx):

		league_cmnds = """
					  **$build [champion]** *Shows most frequent build info for a given champion*
					  **$live [username]** *Shows in-game info for a user*
					  **$mastery [username]** *Shows mastery scores for a user*
					  **$recent [username]** *Shows recent game stats for a user*
					  **$status** *Shows server status for each region*
					  **$user [username]** *Shows general account info for a user*
					  **$region** *Shows the currently selected region*
					  **$region [NA/EUW/KR...]** *Allows you to use commands for accounts in the selected region*\n"""
					  

		music_cmnds = """
					  **$join** *Connects the bot to your current voice channel*
					  **$leave** *Disconnects the bot from your current voice channel*
					  **$play [URL or song name]** *Plays the URL or song name given. If a song is already playing, adds it to the queue*
					  **$queue** *Displays the current queue*
					  **$next** *Skips the current song and plays the next one in queue*
					  **$clear** *Stops the current song and clears the queue*"""

		embed = discord.Embed(colour=discord.Colour(0xff005c))

		embed.add_field(name="<:league_icon:713961777691623436> **League Commands**", value=league_cmnds, inline=False)

		embed.add_field(name="<:djsona:713966916708073519> **Music Commands**", value=music_cmnds, inline=False)

		embed.set_footer(text="Created by Sam and Alek", icon_url="https://i.imgur.com/rqXHyI8.png")

		await ctx.send(embed=embed)

		elobot_usg = getMongo()
		elobot_usg.update_one({"command":"help"}, {"$inc": {"count": 1}}, upsert=True)

def setup(client):
	client.add_cog(Help(client))