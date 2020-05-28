import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os
import shutil
import sqlite3
from os import system
from elobot import getMongo

DIR = os.path.dirname(__file__)
db = sqlite3.connect(os.path.join(DIR, "SongTracker.db"))  # connecting to DB if this file is not there it will create it
SQL = db.cursor()
title_list = []

class Music(commands.Cog):

	def __init__(self, client):
			self.client = client

	@commands.command(pass_context=True, aliases=['j', 'joi'])
	async def join(self, ctx):

		elobot_usg = getMongo()
		elobot_usg.update_one({"command":"play"}, {"$inc": {"count": 1}}, upsert=True)

		##################################################################

		'''
		if you would like to take a look at the database and the table please download: https://sqlitebrowser.org/dl/
		In the first section of the join command we first use SQLite to make us a table in our database that we have connected to above
		we use the statement 'create table if not exists' this creates the table if one by the name specified does not exist
		We create the table Music with columns that we populate right away with when you use the join command in a server
		it gets the Server ID, Sever name, voice channel id, voice channel name, user that used the join command, what postition in the queue we are (starts at one),
		generates queue folder name, and generates the song file name
		then the last thing we do is assign those variables to each column and then create a new row with that info
		then we use db.commit() to write these changes we are making ot the database (basically a save command)
		'''

		SQL.execute('create table if not exists Music('
					'"Num" integer not null primary key autoincrement, '
					'"Server_ID" integer, '
					'"Server_Name" text, '
					'"Voice_ID" integer, '
					'"Voice_Name" text, '
					'"User_Name" text, '
					'"Next_Queue" integer, '
					'"Queue_Name" text, '
					'"Song_Name" text'
					')')
		server_name = str(ctx.guild)
		server_id = ctx.guild.id
		SQL.execute(f'delete from music where Server_ID ="{server_id}" and Server_Name = "{server_name}"')
		db.commit()
		user_name = str(ctx.message.author)
		queue_name = f"Queue#{server_id}"
		song_name = f"Song#{server_id}"
		channel_id = ctx.message.author.voice.channel.id
		channel_name = str(ctx.message.author.voice.channel)
		queue_num = 1
		SQL.execute('insert into Music(Server_ID, Server_Name, Voice_ID, Voice_Name, User_Name, Next_Queue, Queue_Name, Song_Name) values(?,?,?,?,?,?,?,?)',
					(server_id, server_name, channel_id, channel_name, user_name, queue_num, queue_name, song_name))
		db.commit()

		##################################################################

		'''
		This is basic join command
		'''

		channel = ctx.message.author.voice.channel
		voice = get(self.client.voice_clients, guild=ctx.guild)

		if voice is not None:
			return await voice.move_to(channel)

		title_list.clear()
		await channel.connect()

		print(f"The bot has joined {channel}")

		await ctx.send(f"Joined {channel}")


	@commands.command(pass_context=True)
	async def test(self, ctx):
		id = ctx.guild
		id_hash = hash(id)
		user_name = str(ctx.message.author)
		print(ctx.guild.id)


	@commands.command(pass_context=True, aliases=['l', 'lea'])
	async def leave(self, ctx):

		##################################################################

		'''
		In the first section of the leave command we are setting variables to the server name, server id, voice channel name, and voice channel id
		then we use SQL to look for rows that match all four of those variables and delete it we are doing this because we don't want to
		create multiple rows for one server we want to keep each server to only be able to populate one row in the DB
		'''

		server_name = str(ctx.guild)
		server_id = ctx.guild.id
		channel_id = ctx.message.author.voice.channel.id
		channel_name = str(ctx.message.author.voice.channel)
		SQL.execute(f'delete from music where Server_ID ="{server_id}" and Server_Name = "{server_name}" and Voice_ID="{channel_id}" and Voice_Name="{channel_name}"')
		db.commit()

		##################################################################

		'''
		This is basic leave 
		'''

		channel = ctx.message.author.voice.channel
		voice = get(self.client.voice_clients, guild=ctx.guild)
		if voice and voice.is_connected():
			await voice.disconnect()
			print(f"The bot has left {channel}")
			await ctx.send(f"Left {channel}")
		else:
			print("Bot was told to leave voice channel, but was not in one")
			await ctx.send("Don't think I am in a voice channel")


	@commands.command(pass_context=True, aliases=['p', 'pla'])
	async def play(self, ctx, *url: str):


		'''
		In the first section of the play command
		We are doing like above command setting variables to info about the server the command is used in
		Then we are using SQl to select the generated song file name that matches with the server info so we can keep the song file names different
		name_song = SQL.fetchone() this is used to set the variabe name_song to what the SQL command returns
		This need a try block because if someone uses /play before ever having the bot join a voice channel the server will not have a row in the DB
		So it will return an error we use the try block and if that happens we tell the user what went wrong

		'''
		voice = get(self.client.voice_clients, guild=ctx.guild)
		if voice and voice.is_playing():
			print(url)
			await self.createQueue(ctx, url)
			return
		

		server_name = str(ctx.guild)
		server_id = ctx.guild.id
		channel_id = ctx.message.author.voice.channel.id
		channel_name = str(ctx.message.author.voice.channel)

		try:
			SQL.execute(f'select Song_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}" and Voice_ID="{channel_id}" and Voice_Name="{channel_name}"')
			name_song = SQL.fetchone()
			SQL.execute(f'select Server_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
			name_server = SQL.fetchone()
		except:
			await ctx.send("The bot must join a voice channel to play a song: Join one and use '/join'")
			return

		##################################################################

		'''
		in the second section of the play command we have the Check queue function changes inside
		'''

		def check_queue():

			##################################################################

			'''
			Setting variables to info about the server and setting DIR to the current path of the main bot path
			and we are getting the name of the queue folder
			'''

			DIR = os.path.dirname(__file__)
			db = sqlite3.connect(os.path.join(DIR, "SongTracker.db"))
			SQL = db.cursor()
			SQL.execute(f'select Queue_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
			name_queue = SQL.fetchone()
			SQL.execute(f'select Server_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
			name_server = SQL.fetchone()

			##################################################################

			'''
			First check to see if there even is a queues folder then we check for a generated queue folder inside of the queues folder
			after that we list that directory getting the first song file inside of it
			'''

			Queue_infile = os.path.isdir("./Queues")
			if Queue_infile is True:
				DIR = os.path.abspath(os.path.realpath("Queues"))
				Queue_Main = os.path.join(DIR, name_queue[0])
				length = len(os.listdir(Queue_Main))
				still_q = length - 1
				try:
					file_list = sorted(os.listdir(Queue_Main), key=lambda e: int(e.split('-')[0]))
					first_file = file_list[0]

					song_num = first_file.split('-')[0]
				except:
					print("No more queued song(s)\n")
					print(os.path.realpath(__file__))
					print(os.path.dirname(os.path.realpath(__file__)))
					SQL.execute('update Music set Next_Queue = 1 where Server_ID = ? and Server_Name = ?', (server_id, server_name))
					db.commit()
					return

				##################################################################

				'''
				We are now moving the song file gotten above out of the queues folders and then renaming based on the number at the start of the song file name 
				'''

				main_location = "."               
				song_path = os.path.abspath(os.path.realpath(Queue_Main) + "/" + first_file)
				if length != 0:
					print("Song done, playing next queued\n")
					print(f"Songs still in queue: {still_q}")
					song_there = os.path.isfile(f"{name_song[0]}({name_server[0]}).mp3")
					if song_there:
						os.remove(f"{name_song[0]}({name_server[0]}).mp3")
					shutil.move(song_path, main_location)
					for file in os.listdir("./"):
						if file == f"{song_num}-{name_song[0]}({name_server[0]}).mp3":
							os.rename(file, f'{name_song[0]}({name_server[0]}).mp3')

					##################################################################

					voice.play(discord.FFmpegPCMAudio(f'{name_song[0]}({name_server[0]}).mp3'), after=lambda e: check_queue())
					voice.source = discord.PCMVolumeTransformer(voice.source)
					voice.source.volume = 0.07

				else:
					SQL.execute('update Music set Next_Queue = 1 where Server_ID = ? and Server_Name = ?', (server_id, server_name))
					db.commit()
					return

			else:
				SQL.execute('update Music set Next_Queue = 1 where Server_ID = ? and Server_Name = ?', (server_id, server_name))
				db.commit()
				print("No songs were queued before the ending of the last song\n")

		##################################################################

		'''
		In the third section of the play command
		we check for an old song file with the same name as before and delete it
		'''

		song_there = os.path.isfile(f"{name_song[0]}({name_server[0]}).mp3")
		try:
			if song_there:
				os.remove(f"{name_song[0]}({name_server[0]}).mp3")
				SQL.execute('update Music set Next_Queue = 1 where Server_ID = ? and Server_Name = ?', (server_id, server_name))
				db.commit()
				print("Removed old song file")
		except PermissionError:
			print("Trying to delete song file, but it's being played")
			await ctx.send("ERROR: Music playing")
			return

		##################################################################

		'''
		In the fourth section of the play command
		we check for a queue folder inside of the queues folder with the same name as last time then delete it
		'''

		SQL.execute(f'select Queue_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
		name_queue = SQL.fetchone()
		queue_infile = os.path.isdir("./Queues")
		if queue_infile is True:
			DIR = os.path.abspath(os.path.realpath("Queues"))
			Queue_Main = os.path.join(DIR, name_queue[0])
			Queue_Main_infile = os.path.isdir(Queue_Main)
			if Queue_Main_infile is True:
				print("Removed old queue folder")
				shutil.rmtree(Queue_Main)

		##################################################################

		await ctx.send("Getting everything ready now")

		##################################################################

		'''
		In the sixth section of the play command
		This might look the same, but we have removed the renaming of the file by listing all filse in a folder then looking for one that end with .mp3
		because we will have more than one in there I have changed it to just download and name the song file what we want before anything else very similar top the queue command
		'''
		voice = get(self.client.voice_clients, guild=ctx.guild)
		song_path = f"./{name_song[0]}({name_server[0]}).mp3"

		ydl_opts = {
			'format': 'bestaudio/best',
			'quiet': False,
			'outtmpl': song_path,
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'mp3',
				'preferredquality': '192',
			}],
		}

		song_search = " ".join(url)

		try:
			with youtube_dl.YoutubeDL(ydl_opts) as ydl:
				print("Downloading audio now\n")
				info = ydl.extract_info(f"ytsearch1:{song_search}", download=False)
				info_dict = info.get('entries', None)[0]
				video_title = info_dict.get('title', None)
				ydl.download([f"ytsearch1:{song_search}"])

		except:
			print("FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if spotify URL)")
			c_path = os.path.dirname(os.path.realpath(__file__))
			system(f"spotdl -ff {name_song[0]}({name_server[0]}) -f " + '"' + c_path + '"' + " -s " + song_search)  # make sure there are spaces in the -s

		##################################################################

		'''
		one thing has changed it's the playing of the song
		'''

		voice.play(discord.FFmpegPCMAudio(f"{name_song[0]}({name_server[0]}).mp3"), after=lambda e: check_queue())
		voice.source = discord.PCMVolumeTransformer(voice.source)
		voice.source.volume = 0.07

		##################################################################

		#await ctx.send(f"Now playing: {video_title}")

		print("playing\n")


	@commands.command(pass_context=True, aliases=['pa', 'pau'])
	async def pause(self, ctx):

		voice = get(self.client.voice_clients, guild=ctx.guild)

		if voice and voice.is_playing():
			print("Music paused")
			voice.pause()
			await ctx.send("Music paused")
		else:
			print("Music not playing failed pause")
			await ctx.send("Music not playing failed pause")


	@commands.command(pass_context=True, aliases=['r', 'res'])
	async def resume(self, ctx):

		voice = get(self.client.voice_clients, guild=ctx.guild)

		if voice and voice.is_paused():
			print("Resumed music")
			voice.resume()
			await ctx.send("Resumed music")
		else:
			print("Music is not paused")
			await ctx.send("Music is not paused")


	@commands.command(pass_context=True, aliases=['c', 'cl'])
	async def clear(self, ctx):

		##################################################################

		'''
		In the first section of the stop command we are doing like above setting variables to server info the stop command was used in
		'''

		server_name = str(ctx.guild)
		server_id = ctx.guild.id
		SQL.execute('update Music set Next_Queue = 1 where Server_ID = ? and Server_Name = ?', (server_id, server_name))
		db.commit()
		SQL.execute(f'select Queue_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
		name_queue = SQL.fetchone()

		##################################################################

		'''
		in the second section of the stop command 
		we have the program check for a folder inside Queues folder to see if these is anything that need to be deleted
		'''

		queue_infile = os.path.isdir("./Queues")
		if queue_infile is True:
			DIR = os.path.abspath(os.path.realpath("Queues"))
			Queue_Main = os.path.join(DIR, name_queue[0])
			Queue_Main_infile = os.path.isdir(Queue_Main)
			if Queue_Main_infile is True:
				title_list.clear()
				shutil.rmtree(Queue_Main)

		##################################################################

		'''
		basic stuff here
		'''

		voice = get(self.client.voice_clients, guild=ctx.guild)
		if voice and voice.is_playing():
			print("Player cleared")
			voice.stop()
			await ctx.send("Player cleared!")
		else:
			print("No music playing failed to clear")
			await ctx.send("No music playing failed to clear")


	async def createQueue(self, ctx, url: str):

		##################################################################

		'''
		In the first section of the queue command we are doing like above setting variables to server info the queue command was used in
		also like above we have a try block for the same reasons
		but instead of just getting the generated song name we also get the generated queue name as well as the next queue number
		'''

		server_name = str(ctx.guild)
		server_id = ctx.guild.id
		try:
			SQL.execute(f'select Queue_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
			name_queue = SQL.fetchone()
			SQL.execute(f'select Song_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
			name_song = SQL.fetchone()
			SQL.execute(f'select Next_Queue from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
			q_num = SQL.fetchone()
		except:
			await ctx.send("The bot must join a voice channel to queue a song: Join one and use '/join'")
			return

		##################################################################

		'''
		In the second section of the queue command we have also made some changes
		instead of like before where we just have one queue folder then download songs to that folder we make a queues folder
		then we make a folder with the name generated in the join command inside of the queue folder
		this is how we separate the queues
		'''

		Queue_infile = os.path.isdir("./Queues")
		if Queue_infile is False:
			os.mkdir("Queues")
		DIR = os.path.abspath(os.path.realpath("Queues"))
		Queue_Main = os.path.join(DIR, name_queue[0])
		print(Queue_Main)
		Queue_Main_infile = os.path.isdir(Queue_Main)
		if Queue_Main_infile is False:
			os.mkdir(Queue_Main)

		##################################################################

		'''
		In the Third section of the queue command it's basically the same 
		with some minor changes for the name of the song file within the queue folders
		'''
		SQL.execute(f'select Server_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
		name_server = SQL.fetchone()
		queue_path = os.path.abspath(os.path.realpath(Queue_Main) + f"/{q_num[0]}-{name_song[0]}({name_server[0]}).mp3")
		print(os.path.abspath(os.path.realpath(Queue_Main)))
		print(queue_path)
		ydl_opts = {
			'format': 'bestaudio/best',
			'quiet': False,
			'outtmpl': queue_path,
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'mp3',
				'preferredquality': '192',
			}],
		}

		song_search = " ".join(url)

		try:
			with youtube_dl.YoutubeDL(ydl_opts) as ydl:
				# print("Downloading audio now\n")
				ydl.download([f"ytsearch1:{song_search}"])
				info = ydl.extract_info(f"ytsearch1:{song_search}", download=False)
				info_dict = info.get('entries', None)[0]
				video_title = info_dict.get('title', None)
				title_list.append(video_title)
		except:
			print("FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if spotify URL)")
			# q_path = os.path.abspath(os.path.realpath("Queue"))
			Q_DIR = os.path.abspath(os.path.realpath("Queues"))
			Queue_Path = os.path.join(Q_DIR, name_queue[0])
			system(f"spotdl -ff {q_num[0]}-{name_song[0]}({name_server[0]}) -f " + '"' + Queue_Path + '"' + " -s " + song_search)

		##################################################################

		'''
		inside the fourth section of the queue command we do basically the same stuff with one add on
		we use SQl to add one the Next queue number so we can keep the song file names separate inside of the queue folder 
		EX:
		1song#48297234638927438.mp3
		2song#48297234638927438.mp3
		3song#48297234638927438.mp3
		4song#48297234638927438.mp3
		'''

		await ctx.send(f"Adding {video_title} to the queue")

		SQL.execute('update Music set Next_Queue = Next_Queue + 1 where Server_ID = ? and Server_Name = ?', (server_id, server_name))
		db.commit()

		print(f"added to queue\n")

	@commands.command(pass_context=True, aliases=['q', 'sq'])
	async def queue(self, ctx):
		if not title_list:
			await ctx.send("No songs in the queue!")

		else:   
			count = 0
			for i in title_list:
				count += 1
				await ctx.send(f'{count}. {i}\n')
		


	@commands.command(pass_context=True, aliases=['n', 'nex'])
	async def next(self, ctx):
		voice = get(self.client.voice_clients, guild=ctx.guild)

		if voice and voice.is_playing():
			print("Playing next song")
			voice.stop()
			title_list.pop(0)
			await ctx.send("Next Song")
		else:
			print("No music playing failed to play next song")
			await ctx.send("No music playing failed")


def setup(client):
	client.add_cog(Music(client))