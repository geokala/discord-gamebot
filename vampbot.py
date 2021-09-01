#! /usr/bin/env python3
"""Discord based game bot."""
import json
import random

from discord import Game
from discord.ext.commands import Bot, is_owner
import websockets

from vampchar.session import Session

CLIENT = Bot(command_prefix='!')
CONFIG = {}
SESSION = Session()


def load_config(path):
    """Load the configuration"""
    with open(path, encoding='utf-8') as conf_handle:
        return json.load(conf_handle)


@CLIENT.command()
async def rps(ctx):
    """Get a rock-paper-scissors result."""
    await ctx.send(
        'You {}'.format(random.choice(['win', 'lose', 'draw']))
    )


@CLIENT.command()
async def join(ctx):
    """Join the game, creating a character."""
    player_name = ctx.message.author.display_name
    player_id = ctx.message.author.id

    await ctx.send(SESSION.add_player(player_id, player_name))


@CLIENT.command()
async def get(ctx):
    """Get the character sheet."""
    await ctx.send(
        SESSION.get_player_json(ctx.message.author.id)
    )

@CLIENT.command()
async def award(ctx, amount, reason):
    """Award XP."""
    try:
        amount = int(amount)
    except ValueError:
        await ctx.send("You must specify an integer XP award.")
    SESSION.award_xp(amount, reason)
    await ctx.send("All characters received {} XP for {}.".format(amount,
                                                                  reason))


@CLIENT.event
async def on_ready():
    """Output a message when connected"""
    print("Logged in as " + CLIENT.user.name)
    await CLIENT.change_presence(activity=Game(
        name="with blood.",
    ))


@CLIENT.command()
async def hello(ctx):
    """Respond to a greeting"""
    await ctx.send("Such beautiful music.")


@CLIENT.command()
@is_owner()
async def close(_):
    """Disconnect the bot and stop running."""
    print("Closing by owner's demand.")
    try:
        await CLIENT.close()
    except websockets.exceptions.ConnectionClosedOK:
        pass


if __name__ == '__main__':
    CONFIG = load_config('config.json')
    SESSION.load(CONFIG['vamp_save_path'])
    CLIENT.run(CONFIG['token'])
