import discord
from types import SimpleNamespace
from discord.ext import commands

class Moderation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		
	@commands.group(invoke_without_command=True)
	async def setup(self, ctx):
		"""
		Setup commands to set up modlog
		"""
		await ctx.send_help(ctx.command)
	
	@setup.command()
	async def modlog(self, ctx):
		"""
		Sets up modlog for the server
		
		This is used when any actions take place, it will just send to a modlog channel
		"""
		if ctx.author.guild_permissions.administrator:
			overwrites = {
				ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
				ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
			}
			
			category = await ctx.guild.create_category(name=f"{self.bot.user.name}", overwrites=overwrites)
			
			await category.edit(position=0)
			
			ch = await ctx.guild.create_text_channel(name='mod-log', category=category)
			
			await ch.send("Successfully setted up mod-log\nNow in this channel all mod log will be sent")
		
	@commands.command(aliases=["del"])
	async def purge(self, ctx, limit: int):
		"""
		Clear the given messages
		"""
		if ctx.author.guild_permissions.manage_messages:
			await ctx.channel.purge(limit=limit)
			ch = discord.utils.get(ctx.guild.text_channels, name="mod-log")
			if ch == None:
				await ctx.send(f"Please setup modlog for the bot\nTo Setup: {ctx.prefix}setup modlog")
			else:
				await ch.send(f"Sucessfully deleted {limit} of messages\nModerator: {ctx.author.name}")
			
	@commands.command()
	async def kick(self, ctx, member: discord.Member, *, reason):
		"""
		Kick a member
		"""
		if ctx.author.guild_permissions.kick_members:
			await member.kick(reason=reason)
			ch = discord.utils.get(ctx.guild.text_channels, name="mod-log")
			if ch == None:
				await ctx.send(f"Please setup modlog for the bot\nTo Setup: {ctx.prefix}setup modlog")
			else:
				await ch.send(f"Case: Kicked {member.name}\nModerator - {ctx.author.mention}\nReason - {reason}")
			
	@commands.command()
	async def ban(self, ctx, member: discord.Member, *, reason):
		"""
		Ban a member
		"""
		if ctx.author.guild_permissions.ban_members:
			await member.ban(reason=reason)
			ch = discord.utils.get(ctx.guild.text_channels, name="mod-log")
			if ch == None:
				await ctx.send(f"Please setup modlog for the bot\nTo Setup: {ctx.prefix}setup modlog")
			else:
				await ch.send(f"Case: Banned {member.name}\nModerator - {ctx.author.mention}\nReason - {reason}")
			
	@commands.command()
	async def unban(self, ctx, member: discord.Member, *, reason):
		"""
		Unban a member
		"""
		if ctx.author.guild_permissions.ban_members:
			bannedusers = ctx.guild.bans()
			for bentry in bannedusers:
				m = bentry.user
				
				if (m.name, m.id) == (member.name, member.id):
					await ctx.guild.unban(m)
					ch = discord.utils.get(ctx.guild.text_channels, name="mod-log")
					if ch == None:
						await ctx.send(f"Please setup modlog for the bot\nTo Setup: {ctx.prefix}setup modlog")
					else:
						await ch.send(f"Case: Unbanned {member.name}\nModerator - {ctx.author.mention}\nReason - {reason}")
					
	@commands.command()
	async def mute(self, ctx, member: discord.Member, *, reason):
		"""
		Mute the member
		"""
		if ctx.author.guild_permissions.kick_members:
			role = discord.utils.get(ctx.guild.roles, name='Muted')
			if role == None:
				role = await ctx.guild.create_role(name="Muted")
				for channel in ctx.guild.text_channels:
					await channel.set_permissions(role, send_messages=False)
			await member.add_roles(role)
			ch = discord.utils.get(ctx.guild.text_channels, name="mod-log")
			if ch == None:
				await ctx.send(f"Please setup modlog for the bot\nTo Setup: {ctx.prefix}setup modlog")
			else:
				await ch.send(f"Case: Muted {member.name}\nModerator - {ctx.author.mention}\nReason - {reason}")
			
	@commands.command()
	async def unmute(self, ctx, member: discord.Member, *, reason):
		"""
		Unmute a member
		"""
		if ctx.author.guild_permissions.kick_members:
			role = discord.utils.get(ctx.guild.roles, name="Muted")
			if role in member.roles:
				await member.remove_roles(role)
				ch = discord.utils.get(ctx.guild.text_channels, name="mod-log")
			if ch == None:
				await ctx.send(f"Please setup modlog for the bot\nTo Setup: {ctx.prefix}setup modlog")
			else:
				await ch.send(f"Case: Unmuted {member.name}\nModerator - {ctx.author.mention}\nReason - {reason}")
			
def setup(bot):
	bot.add_cog(Moderation(bot))