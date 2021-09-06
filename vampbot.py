#! /usr/bin/env python3
"""Discord based game bot."""
import json
import random

from discord import Game
from discord.ext.commands import Bot, is_owner
import websockets

from vampchar.session import BadInput, Session

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
    await _call_session_and_output(
        ctx, SESSION.add_player,
        ctx.message.author.id, ctx.message.author.display_name,
    )


@CLIENT.command()
async def get(ctx):
    """Get the character sheet."""
    await _call_session_and_output(
        ctx, SESSION.get_player_json, ctx.message.author.id)


async def _call_session_and_output(ctx, command, *args, **kwargs):
    """Call a session command and output the result."""
    try:
        await ctx.send(command(*args, **kwargs))
    except BadInput as err:
        await ctx.send(str(err))


@CLIENT.command()
async def award(ctx, amount, reason):
    """Award XP."""
    await _call_session_and_output(ctx, SESSION.award_xp, amount, reason)

@CLIENT.command()
@is_owner()
async def begin(ctx):
    """Finish character creation, begin the adventure!"""
    await _call_session_and_output(ctx, SESSION.finish_character_creation)


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
    await _call_session_and_output(ctx, SESSION.add_note,
                                   ctx.message.author.id, content)


@notes.group('list')
async def list_notes(ctx):
    """List notes for a character."""
    await _call_session_and_output(ctx, SESSION.list_notes,
                                   ctx.message.author.id)


@notes.group('delete')
async def delete_note(ctx, pos):
    """Delete note for a character."""
    await _call_session_and_output(ctx, SESSION.remove_note,
                                   ctx.message.author.id, pos)


@CLIENT.group('set')
async def _set(ctx):
    """Set various character attributes"""
    if not ctx.subcommand_passed:
        await ctx.send("Try !set with one of these: {}".format(
            ", ".join([command.name for command in _set.commands])))


@_set.command('attribute')
async def set_attribute(ctx, attribute, value):
    """Set an attribute to a given value."""
    await _call_session_and_output(ctx, SESSION.set_attribute,
                                   ctx.message.author.id, attribute, value)


@_set.command('skill')
async def set_skill(ctx, skill, value):
    """Set a skill to a given value."""
    await _call_session_and_output(ctx, SESSION.set_skill,
                                   ctx.message.author.id, skill, value)


@_set.command('background')
async def set_background(ctx, background, value):
    """Set a background to a given value."""
    await _call_session_and_output(ctx, SESSION.set_background,
                                   ctx.message.author.id, background, value)


@_set.command('discipline')
async def set_discipline(ctx, discipline, value):
    """Set a discipline to a given value."""
    await _call_session_and_output(ctx, SESSION.set_discipline,
                                   ctx.message.author.id, discipline, value)


@CLIENT.group('buy')
async def buy(ctx):
    """Deal with buying things for xp on a character sheet."""
    if not ctx.subcommand_passed:
        await ctx.send("Try !buy with one of these: {}".format(
            ", ".join([command.name for command in buy.commands])))


@buy.command('attribute')
async def buy_attribute(ctx, attribute):
    """Buy an extra point in an attribute."""
    await _call_session_and_output(ctx, SESSION.increase_attribute,
                                   ctx.message.author.id, attribute)


@buy.command('skill')
async def buy_skill(ctx, skill):
    """Buy an extra point in a skill."""
    await _call_session_and_output(ctx, SESSION.increase_skill,
                                   ctx.message.author.id, skill)

# TODO: buy_exceptional_attribute- same as buy_attribute, but with exceed_maximum=True


@CLIENT.command('focus')
async def add_focus(ctx, attribute, focus):
    """Add a focus for an attribute."""
    await _call_session_and_output(ctx, SESSION.add_focus,
                                   ctx.message.author.id, attribute, focus)


@CLIENT.command('unfocus')
async def remove_focus(ctx, attribute, focus):
    """Add a focus for an attribute."""
    await _call_session_and_output(ctx, SESSION.remove_focus,
                                   ctx.message.author.id, attribute, focus)


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
