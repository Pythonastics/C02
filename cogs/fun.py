import discord
import random
import aiohttp
import typing
import box
import json
import nekos

from discord.ext import commands
from dadjokes import Dadjoke
from random_password import random_password

class Misc(commands.Cog):
	"""Miscellenous Commands to make the server active and fun"""
	def __init__(self, bot):
		self.bot = bot
		self.jokes = Dadjoke()
		self.session = aiohttp.ClientSession()
		
	@commands.command()
	async def dice(self, ctx):
		"""Rolls the dice"""
		cont = random.randint(0, 7)
		await ctx.send("**You Rolled {}**".format(cont))
		
	@commands.command()
	async def toss(self, ctx):
		"""Put the toss"""
		ch = ['Heads', 'Tails']
		rch = random.choice(ch)
		await ctx.send(f"You got __**{rch}**__")
		
	@commands.command()
	async def reverse(self, ctx, *, text):
		"""Reverse the given text"""
		await ctx.send("".join(list(reversed(str(text)))))
		
	@commands.command()
	async def password(self, ctx):
		"""Generates password with 8 characters"""
		cont = random_password(length=16)
		await ctx.author.send(f"Your Password is **{cont}**")
		
	@commands.command()
	async def dadjoke(self, ctx):
		"""Sends the dadjokes"""
		async with ctx.typing():
			joke = self.jokes.joke
			await ctx.send(joke)
		
	@commands.command()
	async def meme(self, ctx):
		"""Sends you random meme"""
		r = await self.session.get("https://www.reddit.com/r/dankmemes/top.json?sort=top&t=day&limit=500")
		r = await r.json()
		r = box.Box(r)
		data = random.choice(r.data.children).data
		img = data.url
		title = data.title
		embed = discord.Embed(title=title, color=discord.Color.blurple())
		embed.set_image(url=img)
		await ctx.send(embed=embed)
		
	@commands.command()
	async def cat(self, ctx):
		"""Sends you random cat image"""
		r = await self.session.get("http://aws.random.cat/meow")
		r = await r.json()
		r = box.Box(r)
		url = r.file
		embed = discord.Embed(title=":cat: ~meow~", colour=discord.Colour.blurple())
		embed.set_image(url=url)
		await ctx.send(embed=embed)
		
	@commands.command()
	async def bitcoin(self, ctx):
		"""
		Shows the bitcoin current price
		"""
		r = await self.session.get("https://api.coindesk.com/v1/bpi/currentprice/BTC.json")
		r = await r.text()
		r = json.loads(r)
		await ctx.send("Bitcoin Price(in $)" + r['bpi']['USD']['rate'])
		
	@commands.command()
	async def slap(self, ctx, member: discord.Member):
		"""Slaps the member"""
		url = nekos.img("slap")
		embed = discord.Embed(title=f"__**{ctx.author}**__ Slapped __**{member}**__")
		embed.set_image(url=url)
		await ctx.send(embed=embed)
		
	@commands.command()
	async def hug(self, ctx, member: discord.Member):
		"""Hugs the member"""
		url = nekos.img("hug")
		embed = discord.Embed(title=f"__**{ctx.author}**__ Hugged __**{member}**__")
		embed.set_image(url=url)
		await ctx.send(embed=embed)
		
	@commands.command()
	async def echo(self, ctx, *, text: str):
		"""Repeat after you"""
		await ctx.send(text)
		
def setup(bot):
	bot.add_cog(Misc(bot))