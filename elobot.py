import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from riotwatcher import LolWatcher, ApiError
from Resources.region_mapping import reg_names, reg_dict
from functions.mongoSetup import mongoSetup

# INITIALIZE TOKEN FROM .ENV
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# INITIALIZE RIOT API
RIOT_KEY = os.getenv('RIOT_KEY')
watcher = LolWatcher(RIOT_KEY)

# DEFAULT REGION
set_region = 'NA1'

# MONGO DB
elobot_usg = None

# SET PREFIX FOR COMMANDS
client = commands.Bot(command_prefix = '$')
client.remove_command("help")

def getRegion():
	return set_region

def getMongo():
	return elobot_usg

# BOT ONLINE CONFIRMATION
@client.event
async def on_ready():
	global elobot_usg
	print(f'{client.user} has logged in.')

	# INITIALIZE MONGODB
	USER = os.getenv('MONGO_USER')
	PASS = os.getenv('MONGO_PASS')
	elobot_usg = mongoSetup(USER, PASS)

	await client.change_presence(status=discord.Status.online, activity=discord.Game("League and Music! | $help"))
	client.load_extension('cogs.music')

# LOAD ALL FILES ENDING IN .PY FROM COGS
for filename in os.listdir('./cogs'):
	if filename.endswith('.py') and filename != 'music.py':
		client.load_extension(f'cogs.{filename[:-3]}')

# LOAD COMMANDS FROM COG FOLDER
@client.command()
async def load(ctx, extentsion):
	client.load_extension(f'cogs.{extension}')

# UNLOAD COMMANDS FROM COG FOLDER
@client.command()
async def unload(ctx, extentsion):
	client.unload_extension(f'cogs.{extension}')

# REGION COMMAND TO CHANGE OR CHECK
@client.command()
async def region(ctx, *arg):
	global set_region 

	elobot_usg.update_one({"command":"region"}, {"$inc": {"count": 1}}, upsert=True) 

	if not arg:
		region_str = reg_names.get(set_region)
		res_str = f'The current region is set to **{region_str}**'
		await ctx.send(res_str)

	else:   
		if arg[0].upper() in reg_dict:                

			set_region = reg_dict.get(arg[0].upper())
			reg_str = reg_names.get(set_region)
			await ctx.send(f'Region successfully changed to **{reg_str}**')

		else:
			await ctx.send("That region doesn't exist! Please type a valid region:\n" +
						   "[NA, EUW, EUNE, JP, KR, LAN, LAS, BR, OC, RU, TR]")


client.run(TOKEN)