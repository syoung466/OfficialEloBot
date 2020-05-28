import discord
from discord.ext import commands
from functions.createBuild import createString
from elobot import getMongo

class Build(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.command()
	async def build(self, ctx, *args):
		try:
			champ_name = "".join(args)
			champ_name = champ_name.lower()
			await createString(self, ctx, champ_name)

			elobot_usg = getMongo()
			elobot_usg.update_one({"command":"build"}, {"$inc": {"count": 1}}, upsert=True)
		except Exception as e:
			await ctx.send("No build information for that champion!")
			print(e)   


def setup(client):
	client.add_cog(Build(client))