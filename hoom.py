from dhooks import Webhook, Embed

hook = Webhook("https://discordapp.com/api/webhooks/675352405197586445/fVhZ8SsBdlt0AbKW3EX7yDcmhFddT4HB2j9_ElMPLinuUiNnY6QkIUByQn6rdptZg8l8")

embed = Embed(
	description="Thanks for reading :smiley:",
	color=,
	timestap='now'
	)
	
img = 'https://cdn.discordapp.com/attachments/675344314510868513/675354687142363177/20200207_192559.jpg'
	
embed.set_author(name="C02", icon_url=img)
embed.add_field(name="About me", value="Hey! Im **C02** - A multifunctional discord bot, I am developed using **discord.py** and developed by <@675261346669002752>")
hook.send(embed=embed)