import discord
import asyncio
import time
import itertools
import platform
import datetime
import requests
import sys
import os
import inspect

from discord.ext import commands
from random import choice
from googletrans import Translator
from .utils import languages
from .utils.paginator import Pages

class HelpPaginator(Pages):
    def __init__(self, help_command, ctx, entries, *, per_page=4):
        super().__init__(ctx, entries=entries, per_page=per_page)
        self.reaction_emojis.append(('\N{WHITE QUESTION MARK ORNAMENT}', self.show_bot_help))
        self.total = len(entries)
        self.help_command = help_command
        self.prefix = help_command.clean_prefix
        self.is_bot = False

    def get_bot_page(self, page):
        cog, description, commands = self.entries[page - 1]
        self.title = f'{cog} Commands'
        self.description = description
        return commands

    def prepare_embed(self, entries, page, *, first=False):
        self.embed.clear_fields()
        self.embed.description = self.description
        self.embed.title = self.title

        if self.is_bot:
            value ='For more help, join the official bot support server: https://discord.gg/2Vv3dct'
            self.embed.add_field(name='Support', value=value, inline=False)

        self.embed.set_footer(text=f'Use "{self.prefix}help command" for more info on a command.')

        for entry in entries:
            signature = f'{entry.qualified_name} {entry.signature}'
            self.embed.add_field(name=signature, value=entry.short_doc or "No help given", inline=False)

        if self.maximum_pages:
            self.embed.set_author(name=f'Page {page}/{self.maximum_pages} ({self.total} commands)')

    async def show_help(self):
        """shows this message"""

        self.embed.title = 'Paginator help'
        self.embed.description = 'Hello! Welcome to the __**CO2**__ help page.'

        messages = [f'{emoji} {func.__doc__}' for emoji, func in self.reaction_emojis]
        self.embed.clear_fields()
        self.embed.add_field(name='What are these reactions for?', value='\n'.join(messages), inline=False)

        self.embed.set_footer(text=f'We were on page {self.current_page} before this message.')
        await self.message.edit(embed=self.embed)

        async def go_back_to_current_page():
            await asyncio.sleep(30.0)
            await self.show_current_page()

        self.bot.loop.create_task(go_back_to_current_page())

    async def show_bot_help(self):
        """shows how to use the bot"""

        self.embed.title = 'Using the **C02* bot'
        self.embed.description = 'Hello! Welcome to the help page.'
        self.embed.clear_fields()

        entries = (
            ('<argument>', 'This means the argument is __**required**__.'),
            ('[argument]', 'This means the argument is __**optional**__.'),
            ('[A|B]', 'This means the it can be __**either A or B**__.'),
            ('[argument...]', 'This means you can have multiple arguments.\n__**You do not type in the brackets!**__')
        )

        for name, value in entries:
            self.embed.add_field(name=name, value=value, inline=False)

        self.embed.set_footer(text=f'We were on page {self.current_page} before this message.')
        await self.message.edit(embed=self.embed)

        async def go_back_to_current_page():
            await asyncio.sleep(30.0)
            await self.show_current_page()

        self.bot.loop.create_task(go_back_to_current_page())

class PaginatedHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={
            'cooldown': commands.Cooldown(1, 3.0, commands.BucketType.member),
            'help': 'Shows help about the bot, a command, or a category'
        })

    async def on_help_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(str(error.original))

    def get_command_signature(self, command):
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = '|'.join(command.aliases)
            fmt = f'[{command.name}|{aliases}]'
            if parent:
                fmt = f'{parent} {fmt}'
            alias = fmt
        else:
            alias = command.name if not parent else f'{parent} {command.name}'
        return f'{alias} {command.signature}'

    async def send_bot_help(self, mapping):
        def key(c):
            return c.cog_name or '\u200bNo Category'

        bot = self.context.bot
        entries = await self.filter_commands(bot.commands, sort=True, key=key)
        nested_pages = []
        per_page = 9
        total = 0

        for cog, commands in itertools.groupby(entries, key=key):
            commands = sorted(commands, key=lambda c: c.name)
            if len(commands) == 0:
                continue

            total += len(commands)
            actual_cog = bot.get_cog(cog)
            # get the description if it exists (and the cog is valid) or return Empty embed.
            description = (actual_cog and actual_cog.description) or discord.Embed.Empty
            nested_pages.extend((cog, description, commands[i:i + per_page]) for i in range(0, len(commands), per_page))

        # a value of 1 forces the pagination session
        pages = HelpPaginator(self, self.context, nested_pages, per_page=1)

        # swap the get_page implementation to work with our nested pages.
        pages.get_page = pages.get_bot_page
        pages.is_bot = True
        pages.total = total
        await pages.paginate()

    async def send_cog_help(self, cog):
        entries = await self.filter_commands(cog.get_commands(), sort=True)
        pages = HelpPaginator(self, self.context, entries)
        pages.title = f'{cog.qualified_name} Commands'
        pages.description = cog.description

        await pages.paginate()

    def common_command_formatting(self, page_or_embed, command):
        page_or_embed.title = self.get_command_signature(command)
        if command.description:
            page_or_embed.description = f'{command.description}\n\n{command.help}'
        else:
            page_or_embed.description = command.help or 'No help found...'

    async def send_command_help(self, command):
        # No pagination necessary for a single command.
        embed = discord.Embed(colour=discord.Colour.blurple())
        self.common_command_formatting(embed, command)
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        subcommands = group.commands
        if len(subcommands) == 0:
            return await self.send_command_help(group)

        entries = await self.filter_commands(subcommands, sort=True)
        pages = HelpPaginator(self, self.context, entries)
        self.common_command_formatting(pages, group)
        await pages.paginate()

class Meta(commands.Cog):
    """Commands for utilities related to bot and discord"""
    
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()
        self.old_help_command = bot.help_command
        bot.help_command = PaginatedHelpCommand()
        bot.help_command.cog = self
        self.start_time = datetime.datetime.utcnow()

    def cog_unload(self):
        self.bot.help_command = self.old_help_command
       
    @commands.command()
    async def ping(self, ctx):
    	"""Shows the latency of the bot"""
    	start = time.monotonic()
    	msg = await ctx.send("Ping...")
    	end = time.monotonic()
    	duration = (start - end) * 1000
    	embed = discord.Embed(color=discord.Color.blurple())
    	embed.add_field(name="Ping", value=f"**Message Responce**: {duration:.2f}ms\n**Websocket Latency**: {round(self.bot.latency * 1000)}ms")
    	await msg.edit(embed=embed)
    	
    @commands.command()
    async def invite(self, ctx):
    	"""Send the bot invite url"""
    	url = f"https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot"
    	await ctx.send(url)
    	
    @commands.command()
    async def source(self, ctx):
    	"""Display my source code url"""
    	await ctx.send("https://github.com/mischievousdev/C02")
    	
    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
    	"""Shutdown the bot - Only owners can do this"""
    	await self.bot.logout()
    	
    def get_uptime(self, *, brief=False):
    	uptime = datetime.datetime.utcnow() - self.start_time
    	(hours, remainder) = divmod(int(uptime.total_seconds()), 3600)
    	(minutes, seconds) = divmod(remainder, 60)
    	(days, hours) = divmod(hours, 24)
    	
    	if not brief:
    		if days:
    			fmt = f'{d} days, {h} hours, {m} minutes, {s} seconds'
    		else:
    			fmt = f'{h} hours, {m} minutes, {s} seconds'
    	else:
    		fmt = '{h}h {m}m {s}s'
    		if days:
    			fmt = f'{d}d' + fmt
    	return fmt.format(d=days, h=hours, m=minutes, s=seconds)
    	
    @commands.command(aliases=['bi'])
    async def about(self, ctx):
    	"""Shows info bot"""
    	bot = self.bot
    	uptime = self.get_uptime(brief=True)
    	plat = platform.python_version()
    	users = len(bot.users)
    	guilds = len(bot.guilds)
    	textc = 0
    	voicec = 0
    	for guild in self.bot.guilds:
    		for channel in guild.channels:
    			if isinstance(channel, discord.TextChannel):
    				textc += 1
    			if isinstance(channel, discord.VoiceChannel):
    				voicec += 1
    	embed = discord.Embed(color=discord.Color.blurple())
    	embed.url = "https://discord.gg/2Vv3dct"
    	embed.title = 'Official server of C02'
    	embed.add_field(name="Developer", value="<@675261346669002752>")
    	embed.add_field(name="Stats", value=f"Used By - {users}\nGuilds - {guilds}\nLibrary - discord.py({discord.__version__})\nText Channels - {textc}\nVoice Channels - {voicec}\nUptime - {uptime}")
    	embed.add_field(name="System Stats", value=f"Python Version - {plat}\nCommands - {len(bot.commands)}\nPlatform - {sys.platform}")
    	await ctx.send(embed=embed)
    	
    @commands.command()
    async def avatar(self, ctx, *, member: discord.Member=None):
    	if not member:
    		member = ctx.author
    		
    	url = member.avatar_url_as(static_format='png')
    	embed = discord.Embed(timestap=ctx.message.created_at)
    	embed.set_image(url=url)
    	await ctx.send(embed=embed)
    	
    @commands.command()
    async def info(self, ctx, *, member: discord.Member=None):
    	"""
    	Show info about a member, if not member the member is you
    	"""
    	if not member:
    		member = ctx.author
    		
    	embed = discord.Embed(color=member.color)
    	embed.set_thumbnail(url=member.avatar_url)
    	embed.set_author(name=str(member.name))
    	roles = ""
    	for role in member.roles:
    		roles += role.mention
    	servers = sum(g.get_member(member.id) is not None for g in self.bot.guilds)
    	embed.add_field(name="ID", value=member.id)
    	embed.add_field(name="Servers", value=f'{servers} shared')
    	embed.add_field(name="Roles", value=f"All Roles: {roles}\nTop Role: {member.top_role.mention}")
    	embed.add_field(name="Joined", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
    	embed.add_field(name="Created", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
    	await ctx.send(embed=embed)
    	
    @commands.command()
    async def serverinfo(self, ctx):
    	"""
    	Shows information about the server
    	"""
    	guild = ctx.guild
    	embed = discord.Embed(color=ctx.author.color)
    	embed.title = guild.name
    	embed.add_field(name="ID", value=guild.id)
    	embed.add_field(name="Owner", value=guild.owner)
    	embed.add_field(name="Region & Verification", value=f"Region - {guild.region}\nVerification - {guild.verification_level}")
    	embed.set_thumbnail(url=guild.icon_url)
    	info = []
    	features = set(guild.features)
    	all_features = {
    		'VIP_REGIONS': 'VIP Voice Regions',
    		'VANITY_URL': 'Vanity Invite',
    		'VERIFIED': 'Verified Server',
    		'INVITE_SPLASH': 'Special Splash Invite',
    		'PARTNERED': 'Partnered Server',
    		'MORE_EMOJI': 'More than 50 emotes',
    		'DISCOVERABLE': 'Server discovery',
    		'COMMERCE': 'Sell things',
    		'PUBLIC': 'Lurkable',
    		'NEWS': 'News Channels',
    		'BANNER': 'Banner',
    		'ANIMATED_ICON': 'Animated Icon',
    	}
    	for feature, label in all_features.items():
    		if feature in features:
    			info.append(f'{label}')
    			
    	if info:
    		embed.add_field(name="Features", value="\n".join(info))
    		
    	online = len([m.id for m in ctx.guild.members if m.status == discord.Status.online])
    	idle = len([m.id for m in ctx.guild.members if m.status == discord.Status.idle])
    	dnd = len([m.id for m in ctx.guild.members if m.status == discord.Status.dnd])
    	offline = len([m.id for m in ctx.guild.members if m.status == discord.Status.offline])
    	bot = 0
    	humans = 0
    	total = 0
    	for x in ctx.guild.members:
    		if x.bot == True:
    			bot += 1
    			total += 1
    		else:
    			humans += 1
    			total += 1
    			
    	embed.add_field(name="Members", value=f"Online - {online} members\nIdle - {idle} members\nDo Not Disturb - {dnd} members\nOffline - {offline} members\nTotal - {total} members")
    	embed.add_field(name="Channels", value=f"Text Channels - {len(guild.text_channels)}\nVoice Channels - {len(guild.voice_channels)}\nTotal Channels - {(len(guild.text_channels) + len(guild.voice_channels))}")
    	embed.add_field(name="Emojis & Roles", value=f"Emojis - {len(guild.emojis)}\nRoles - {len(guild.roles)}")
    	
    	await ctx.send(embed=embed)
    	
    @commands.command()
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.user)
    async def feedback(self, ctx, *, message):
    	"""
    	You can give feedback/bug-report through this command to dev directly
    	"""
    	ch = self.bot.get_channel(675344359306297364)
    	embed = discord.Embed(title=f"New Feedback by {ctx.author}", color=0x5CDBF0)
    	embed.set_footer(text=f"Feedback from {ctx.author} | {ctx.guild}")
    	embed.add_field(name="Feedback", value=message)
    	await ch.send(embed=embed)
    	await ctx.send(":white_check_mark:")
    	
    @commands.group(invoke_without_command=True)
    async def github(self, ctx):
    	"""Commands related to github"""
    	await ctx.send_help(ctx.command)
    	
    @github.command()
    async def userinfo(self, ctx, *, github_username=None):
    	"""Shows username github stats"""
    	if not github_username:
    		await ctx.send("No username provided")
    		await ctx.message.add_reaction('\N{NO ENTRY SIGN}')
    	else:
    		r = requests.get(f"https://api.github.com/users/{github_username}")
    		resp = r.json()
    		name = resp['login']
    		id = resp['id']
    		avatar_url = resp['avatar_url']
    		turl = resp['html_url']
    		bio = resp['bio']
    		repos = resp['public_repos']
    		gists = resp['public_gists']
    		followers = resp['followers']
    		created = resp['created_at']
    		
    		embed = discord.Embed(title=name, url=turl, description=bio, color=ctx.author.color)
    		embed.add_field(name='ID', value=id)
    		embed.add_field(name='Repos', value=repos)
    		embed.add_field(name='Gists', value=gists)
    		embed.add_field(name='Followers', value=followers)
    		embed.add_field(name='Created', value=created)
    		embed.set_thumbnail(url=avatar_url)
    		embed.set_footer(text=f'Requested by {ctx.author} | {ctx.message.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")}')
    		await ctx.send(embed=embed)
    		
    @github.command()
    async def repoinfo(self, ctx, owner, *, reponame):
    	"""Shows the repoinfo of the given repo"""
    	if not owner and reponame:
    		await ctx.send("No Owner/Repository name provided")
    		await ctx.message.add_reaction("\N{NO ENTRY SIGN}")
    	else:
    		r = requests.get(f"https://api.github.com/repos/{owner}/{reponame}")
    		r = r.json()
    		tname = r["full_name"]
    		turl = r["html_url"]
    		id = r["id"]
    		tdesc = r["description"]
    		owner = r["owner"]["login"]
    		size = r["size"]
    		stars = r["stargazers_count"]
    		watchs = r["watchers_count"]
    		lang = r["language"]
    		forks = r["forks_count"]
    		subscribers = r["subscribers_count"]
    		license = r["license"]["name"]
    		oissues = r["open_issues"]
    		
    		embed = discord.Embed()
    		embed.title = tname
    		embed.url = turl
    		embed.color = 0x00ffff
    		embed.description = tdesc
    		embed.add_field(name="ID", value=id)
    		embed.add_field(name="Owner", value=owner)
    		embed.add_field(name="Language", value=lang)
    		embed.add_field(name="Size", value=size)
    		embed.add_field(name="Forks", value=forks)
    		embed.add_field(name="Stargazers", value=stars)
    		embed.add_field(name="Watchers", value=watchs)
    		embed.add_field(name="Subscribers", value=subscribers)
    		embed.add_field(name="Open Issues", value=oissues)
    		embed.add_field(name="License", value=license)
    		await ctx.send(embed=embed)
    		
    @commands.command()
    async def translate(self, ctx, *, message):
    	"""Translate the given message to english"""
    	tcont = self.translator.translate(message)
    	embed = discord.Embed()
    	embed.color = 0x00ffff
    	embed.description = tcont.text
    	await ctx.send(embed=embed)
    	
    @commands.command()
    async def beta(self, ctx):
    	"""
    	Only works on https://discord.gg/2Vv3dct
    	
    	Gives you the beta-tester role
    	"""
    	guild = self.bot.get_guild(675341508278353939)
    	role = discord.utils.get(guild.roles, name="beta-test")
    	await ctx.author.add_roles(role)
    	await ctx.send("You are now a beta tester")
		
def setup(bot):
	bot.add_cog(Meta(bot))
