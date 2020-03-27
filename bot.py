#! /usr/bin/env python3
"""Discord based game bot."""
import json

from discord import Game
from discord.ext.commands import Bot


CLIENT = Bot(command_prefix='!')
CONFIG = {}


def load_config(path):
    """Load the configuration."""
    with open(path) as conf_handle:
        return json.load(conf_handle)


@CLIENT.event
async def on_ready():
    """Output a message when connected."""
    print("Logged in as " + CLIENT.user.name)
    await CLIENT.change_presence(activity=Game(name="Warm atomic conflict?"))


@CLIENT.command()
async def hello(ctx):
    """Respond to a greeting."""
    await ctx.send("Shall we play a game?")


if __name__ == '__main__':
    CONFIG = load_config('config.json')
    CLIENT.run(CONFIG['token'])
