import discord
from discord.ext import commands
from elobot import watcher, getMongo
from functions.createEmbedRec import createEmbed, buildStrings

class Recent(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.command()
	async def recent(self, ctx, *args):

		try:
			async with ctx.typing():
				buildStrings(args)
				await createEmbed(ctx)

				elobot_usg = getMongo()
				elobot_usg.update_one({"command":"recent"}, {"$inc": {"count": 1}}, upsert=True)
		except:
			await ctx.send("Cannot find account's information!")

def setup(client):
	client.add_cog(Recent(client))