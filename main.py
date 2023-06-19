import os
import asyncio
import discord 
import discord.app_commands as commands
import buttons

TOKEN = os.environ['DECK_TOKEN']

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = commands.CommandTree(client)

@tree.command(name='deck',description='Make deck.')
async def deck(ctx):
    await ctx.response.send_message('Choose Deck type.', view=buttons.DeckView(['Trump', '1 to 100'], timeout=None))

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await tree.sync()

client.run(TOKEN)