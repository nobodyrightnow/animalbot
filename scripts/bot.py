import discord
from dotenv import load_dotenv # for loading discord token from .env file
import os
from image_analyzer import analyze_image

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
    # ignore bot's own messages
    if message.author == client.user:
        return

    # check if the bot was mentioned
    if client.user in message.mentions:
        # check for image attachment
        image_attachments = []
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith("image/"):
                image_attachments.append(attachment)

        num_images = len(image_attachments)
        if num_images == 0:
            await message.reply("Don't ping me without an image >:(")
            return
        elif num_images > 1:
            await message.reply("Slow down! I can only handle one image at a time right now :(")
            return

        # download the image
        image = await image_attachments[0].read()

        await message.reply(analyze_image(image))
        return

client.run(DISCORD_TOKEN)
