#pylint:disable=W0611
import sqlite3
import discord
import os
import jishaku
import datetime

from discord.ext import commands

bot = commands.Bot(command_prefix="c;")

token = os.getenv("TOKEN")

@bot.event
async def on_ready():
	"""Bot startups"""
	print(f"[Ready]\nLogged in as: {bot.user.name}\nDev: mischievousdev\nStart Time: {datetime.datetime.utcnow()}")
	bot.load_extension("jishaku")
	
@bot.event
async def on_error(error):
	print(error)
	
for extension in os.listdir("./cogs"):
	if extension.endswith(".py"):
		bot.load_extension(f"cogs.{extension[:-3]}")
		
@bot.command(hidden=True)
async def load(ctx, extension):
	if "".join(extension.lower().split()).strip() == "all":
		for filename in os.listdir("./cogs"):
			if filename.endswith(".py"):
				bot.load_extension(f"cogs.{filename[:-3]}")
	else:
		bot.load_extension(f"cogs.{extension}")
		
@bot.command(hidden=True)
async def unload(ctx, extension):
	if "".join(extension.lower().split()).strip() == "all":
		for filename in os.listdir("./cogs"):
			if filename.endswith(".py"):
				bot.load_extension(f"cogs.{filename[:-3]}")
	else:
		bot.unload_extension(f"cogs.{extension}")
	
if __name__ == '__main__':
	bot.run(token)