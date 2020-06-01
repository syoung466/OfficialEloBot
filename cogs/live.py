import discord
from discord.ext import commands
from elobot import watcher, getMongo
from functions.createEmbedLive import createEmbed, buildStrings

class Live(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['liv'])
    async def live(self, ctx, *args):
        try:
            async with ctx.typing():
                buildStrings(args)
                await createEmbed(ctx)

                elobot_usg = getMongo()
                elobot_usg.update_one({"command":"live"}, {"$inc": {"count": 1}}, upsert=True)

        except Exception as e:
            await ctx.send("No live game info for that account!")
            print(e)

def setup(client):
    client.add_cog(Live(client))