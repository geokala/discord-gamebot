import discord
import json


client = discord.Client()

def load_config(path):
    with open(path) as conf_handle:
        return json.load(conf_handle)


@client.event
async def on_ready():
    """Notify when bot is ready."""
    print("The bot is ready!")


@client.event
async def on_message(message):
    """Respond to messages."""
    if message.author == client.user:
        return
    if message.content == "Test":
        await client.send_message(message.channel, "Cake")


if __name__ == '__main__':
    config = load_config('config.json')
    client.run(config['token'])
