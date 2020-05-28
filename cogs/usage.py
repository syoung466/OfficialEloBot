import discord
from discord.ext import commands
from elobot import watcher, getMongo

class Usage(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def usage(self, ctx):

        try:
            elobot_usg = getMongo()
            elobot_usg.update_one({"command":"usage"}, {"$inc": {"count": 1}}, upsert=True)

            build_c = elobot_usg.find_one({"command": "build"})['count']
            help_c = elobot_usg.find_one({"command": "help"})['count']
            live_c = elobot_usg.find_one({"command": "live"})['count']
            mastery_c = elobot_usg.find_one({"command": "mastery"})['count']
            play_c = elobot_usg.find_one({"command": "play"})['count']
            recent_c = elobot_usg.find_one({"command": "recent"})['count']
            status_c = elobot_usg.find_one({"command": "status"})['count']
            usage_c = elobot_usg.find_one({"command": "usage"})['count']
            user_c = elobot_usg.find_one({"command": "user"})['count']
            total_c = build_c + help_c + live_c + mastery_c + play_c + recent_c + status_c + usage_c + user_c

            usage_str = f"""**Help:** {help_c}
                            **Build:** {build_c}
                            **Live:** {live_c}
                            **Mastery:** {mastery_c} 
                            **Recent:** {recent_c} 
                            **Status:** {status_c}
                            **Usage:** {usage_c}
                            **User:** {user_c} 
                            **Play:** {play_c}\n
                            **TOTAL:** {total_c}"""

            embed = discord.Embed(title="EloBot Usage Information", colour=discord.Colour(0xff005c))
            embed.add_field(name="**Command Totals**", value=usage_str, inline=False)

            embed.set_footer(text="Created by Sam and Alek", icon_url="https://i.imgur.com/rqXHyI8.png")

            await ctx.send(embed=embed)


        except Exception as e:
            await ctx.send("Error retrieving usage information!")
            print(e)

def setup(client):
    client.add_cog(Usage(client))
