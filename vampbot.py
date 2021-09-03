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


async def _check_int(ctx, value):
    """Try to cast something as an int, and scream otherwise."""
    try:
        return int(value)
    except ValueError:
        await ctx.send("You must specify an integer value.")
        raise


@CLIENT.command()
@is_owner()
async def begin(ctx):
    """Finish character creation, begin the adventure!"""
    await ctx.send(SESSION.finish_character_creation())


# TODO: Organise groups of commands better; allow partial non-ambiguous command matching
@CLIENT.group('notes')
async def notes(ctx):
    """Deal with notes on a character sheet."""
    if not ctx.subcommand_passed:
        await ctx.send("Try !notes with one of these: {}".format(
            ", ".join([command.name for command in notes.commands])))


@notes.group('add')
async def add_note(ctx, *content):
    """Add a note to a character."""
    content = ' '.join(content)
    await ctx.send(
        SESSION.add_note(ctx.message.author.id, content))


@notes.group('list')
async def list_notes(ctx):
    """List notes for a character."""
    await ctx.send(
        SESSION.list_notes(ctx.message.author.id))


@notes.group('delete')
async def delete_note(ctx, pos):
    """Delete note for a character."""
    pos = await _check_int(ctx, pos)
    await ctx.send(
        SESSION.remove_note(ctx.message.author.id, pos))


@CLIENT.group('set')
async def _set(ctx):
    """Set various character attributes"""
    if not ctx.subcommand_passed:
        await ctx.send("Try !set with one of these: {}".format(
            ", ".join([command.name for command in _set.commands])))


@_set.command('attribute')
async def set_attribute(ctx, attribute, value):
    """Set an attribute to a given value."""
    value = await _check_int(ctx, value)
    await ctx.send(
        SESSION.set_attribute(ctx.message.author.id, attribute, value))


@_set.command('skill')
async def set_skill(ctx, skill, value):
    """Set a skill to a given value."""
    value = await _check_int(ctx, value)
    await ctx.send(
        SESSION.set_skill(ctx.message.author.id, skill, value))


@_set.command('background')
async def set_background(ctx, background, value):
    """Set a background to a given value."""
    value = await _check_int(ctx, value)
    await ctx.send(
        SESSION.set_background(ctx.message.author.id, background, value))


@_set.command('discipline')
async def set_discipline(ctx, discipline, value):
    """Set a discipline to a given value."""
    value = await _check_int(ctx, value)
    await ctx.send(
        SESSION.set_discipline(ctx.message.author.id, discipline, value))


@CLIENT.command('focus')
async def add_focus(ctx, attribute, focus):
    """Add a focus for an attribute."""
    await ctx.send(SESSION.add_focus(ctx.message.author.id, attribute, focus))


@CLIENT.command('unfocus')
async def remove_focus(ctx, attribute, focus):
    """Add a focus for an attribute."""
    await ctx.send(
        SESSION.remove_focus(ctx.message.author.id, attribute, focus))


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
