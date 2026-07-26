import discord
from dotenv import load_dotenv # for loading discord token from .env file
import os

# Load discord token
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Check to see if discord token could be loaded
if DISCORD_TOKEN is None:
    raise ValueError("DISCORD_TOKEN is missing from .env")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(DISCORD_TOKEN)
