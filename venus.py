#pylint:disable=W0611
import sqlite3
import discord
import jishaku

from discord.ext import commands

bot = commands.Bot(command_prefix="v;")

ie = {
	'jishaku'
}

for ext in ie:
	try:
		bot.load_extension(ext)
	except Exception as e:
		print(e)
		
@bot.event
async def on_ready():
	print("Logged in as {}".format(bot.user.name))
	
bot.run("NjUzNzk5MjY5OTI0NDcwNzg1.XjWbuA.Sem0pjalCvNfIdVGozhuskW_OJk")