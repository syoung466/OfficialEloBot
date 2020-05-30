import discord
from discord.ext import commands
from elobot import watcher, getMongo
from functions.createEmbedMast import *

class Mastery(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.command()
	async def mastery(self, ctx, *args):
		try:
			if len(args) == 1:   
				async with ctx.typing():         
					buildStrings(args)	
					await createEmbed(ctx)				
					
			else:
				args = "".join(args)
				await specific(ctx, args)

			elobot_usg = getMongo()
			elobot_usg.update_one({"command":"mastery"}, {"$inc": {"count": 1}}, upsert=True)

		except Exception as e:
			await ctx.send("Cannot find account's information!\nIf you were trying to look up a user's\nmastery on a specific champion use: **$mastery [user] - [champion]**")
			print(e)

def setup(client):
	client.add_cog(Mastery(client))
