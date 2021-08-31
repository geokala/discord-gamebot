#! /usr/bin/env python3
"""Discord based game bot."""
import json
import random

from discord import Game
from discord.ext.commands import Bot, is_owner
import websockets

CLIENT = Bot(command_prefix='!')
CONFIG = {}


def load_config(path):
    """Load the configuration"""
    with open(path) as conf_handle:
        return json.load(conf_handle)


@CLIENT.command()
async def rps(ctx):
    await ctx.send(
        'You {}'.format(random.choice(['win', 'lose', 'draw']))
    )


@CLIENT.command()
async def roll(ctx, dice='1d100'):
    """Roll dice"""
    dice_split = dice.split('d')
    if len(dice_split) != 2:
        await ctx.send('Expected to see !roll xdy, e.g. 2d6')
        return

    count, sides = dice_split

    try:
        count = int(count)
        sides = int(sides)
    except ValueError:
        await ctx.send(
            'Either {} is not an integer, or {} is not an integer.\n'
            'Try again, e.g. using 2d6'.format(
                count, sides,
            )
        )
        return

    if count < 1:
        await ctx.send('Rolling less than one dice was really quick!')
        return

    if sides < 1:
        await ctx.send(
            'Rolling dice with less than 0 sides...\n'
            'Assuming all values are 42.\n'
            'Results: {}{}'.format(
                ' '.join('42' for i in range(count)),
                '\nTotal: {}'.format(42 * count) if count > 1 else "",
            )
        )
        return

    if count > 30:
        await ctx.send(
            'I only have 30 dice in my dice box, sorry.'
        )
        return

    if sides > 100:
        await ctx.send(
            'Sorry, someone stole all the dice I had with more than 100 '
            'sides. Something really needs to be done about the crime around '
            'here!'
        )
        return

    results = []
    for _ in range(count):
        results.append(random.randint(1, sides))

    await ctx.send(
        'Rolling {}\n'
        'Results: {}{}'.format(
            dice,
            ' '.join(str(r) for r in results),
            '\nTotal: {}'.format(sum(results)) if count > 1 else "",
        )
    )


@CLIENT.event
async def on_ready():
    """Output a message when connected"""
    print("Logged in as " + CLIENT.user.name)
    await CLIENT.change_presence(activity=Game(
        name="with fire",
    ))


@CLIENT.command()
async def hello(ctx):
    """Respond to a greeting"""
    await ctx.send("Shall we play a game?")


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
    CLIENT.run(CONFIG['token'])
