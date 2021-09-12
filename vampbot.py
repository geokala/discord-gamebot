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
async def set_skill(ctx, *args):
    """Set a skill to a given value."""
    if len(args) < 2:
        await ctx.send(
            'Expected a skill name followed by an integer for value.')
    else:
        skill = ' '.join(args[:-1])
        value = args[-1]
        await _call_session_and_output(ctx, SESSION.set_skill,
                                       ctx.message.author.id, skill, value)


@_set.command('background')
async def set_background(ctx, *args):
    """Set a background to a given value."""
    if len(args) < 2:
        await ctx.send(
            'Expected a background name followed by an integer for value.')
    else:
        background = ' '.join(args[:-1])
        value = args[-1]
        await _call_session_and_output(ctx, SESSION.set_background,
                                       ctx.message.author.id, background,
                                       value)


@_set.command('discipline')
async def set_discipline(ctx, discipline, value):
    """Set a discipline to a given value."""
    if len(args) < 2:
        await ctx.send(
            'Expected a discipline name followed by an integer for value.')
    else:
        discipline = ' '.join(args[:-1])
        value = args[-1]
        await _call_session_and_output(ctx, SESSION.set_discipline,
                                       ctx.message.author.id, discipline,
                                       value)


@_set.command('clan')
async def set_clan(ctx, *clan_name):
    """Set a character's clan membership."""
    await _call_session_and_output(ctx, SESSION.set_clan,
                                   ctx.message.author.id, ' '.join(clan_name))


@_set.command('name')
async def set_name(ctx, *name):
    """Set a character's character name."""
    await _call_session_and_output(ctx, SESSION.set_name,
                                   ctx.message.author.id, ' '.join(name))


@_set.command('archetype')
async def set_archetype(ctx, *archetype):
    """Set a character's archetype."""
    await _call_session_and_output(ctx, SESSION.set_archetype,
                                   ctx.message.author.id, ' '.join(archetype))


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


@buy.command('exceptional')
async def buy_exceptional_skill(ctx, skill):
    """Buy an extra point (including beyond 5) in a skill."""
    await _call_session_and_output(ctx, SESSION.increase_skill,
                                   ctx.message.author.id, skill,
                                   exceed_maximum=True)


@buy.command('in-clan')
async def buy_in_clan_discipline(ctx, *discipline):
    """Buy an extra point in an in-clan discipline."""
    discipline = ' '.join(discipline)
    await _call_session_and_output(ctx, SESSION.increase_discipline,
                                   ctx.message.author.id, discipline)


@buy.command('out-of-clan')
async def buy_out_of_clan_discipline(ctx, *discipline):
    """Buy an extra point in an out-of-clan discipline."""
    discipline = ' '.join(discipline)
    await _call_session_and_output(ctx, SESSION.increase_discipline,
                                   ctx.message.author.id, discipline, True)


@buy.command('background')
async def buy_background(ctx, background):
    """Buy an extra point in a background."""
    await _call_session_and_output(ctx, SESSION.increase_background,
                                   ctx.message.author.id, background)


@buy.command('merit')
async def buy_merit(ctx, *args):
    """Add a merit."""
    if len(args) < 2:
        await ctx.send(
            'Expected a merit name followed by an integer for cost.')
    else:
        merit_name = ' '.join(args[:-1])
        cost = args[-1]
        await _call_session_and_output(ctx, SESSION.add_merit,
                                       ctx.message.author.id,
                                       merit_name, cost)


@CLIENT.group('inflict')
async def inflict(ctx):
    """Deal with inflicting ailments on a character."""
    if not ctx.subcommand_passed:
        await ctx.send("Try !inflict with one of these: {}".format(
            ", ".join([command.name for command in inflict.commands])))


@inflict.command('flaw')
async def inflict_flaw(ctx, *args):
    """Inflict a flaw."""
    if len(args) < 2:
        await ctx.send(
            'Expected a flaw name followed by an integer for value.')
    else:
        flaw_name = ' '.join(args[:-1])
        value = args[-1]
        await _call_session_and_output(ctx, SESSION.add_flaw,
                                       ctx.message.author.id,
                                       flaw_name, value)


@inflict.command('derangement')
async def inflict_derangement(ctx, *args):
    """Inflict a derangement."""
    derangement = ' '.join(args)
    await _call_session_and_output(ctx, SESSION.add_derangement,
                                   ctx.message.author.id,
                                   derangement)


@inflict.command('damage')
async def inflict_normal_damage(ctx, amount=1):
    """Inflict one or more points of normal damage."""
    await _call_session_and_output(ctx, SESSION.inflict_damage,
                                   ctx.message.author.id, 'normal', amount)


@inflict.command('aggravated')
async def inflict_aggravated_damage(ctx, amount=1):
    """Inflict one or more points of aggravated damage."""
    await _call_session_and_output(ctx, SESSION.inflict_damage,
                                   ctx.message.author.id,
                                   'aggravated', amount)


@CLIENT.group('heal')
async def heal(ctx):
    """Deal with healing ailments on a character."""
    if not ctx.subcommand_passed:
        await ctx.send("Try !heal with one of these: {}".format(
            ", ".join([command.name for command in heal.commands])))


@heal.command('damage')
async def heal_normal_damage(ctx):
    """Heal one point of normal damage."""
    await _call_session_and_output(ctx, SESSION.heal_damage,
                                   ctx.message.author.id, 'normal')


@heal.command('aggravated')
async def heal_aggravated_damage(ctx):
    """Heal one point of aggravated damage."""
    await _call_session_and_output(ctx, SESSION.heal_damage,
                                   ctx.message.author.id, 'aggravated')


@CLIENT.group('remove')
async def remove(ctx):
    """Deal with removing things for xp on a character sheet."""
    if not ctx.subcommand_passed:
        await ctx.send("Try !remove with one of these: {}".format(
            ", ".join([command.name for command in remove.commands])))


@remove.command('merit')
async def remove_merit(ctx, *merit_name):
    """Remove a merit from a character.
    Refund the cost if during character creation.
    """
    merit_name = ' '.join(merit_name)
    await _call_session_and_output(ctx, SESSION.remove_merit,
                                   ctx.message.author.id, merit_name)


@remove.command('flaw')
async def remove_flaw(ctx, *flaw_name):
    """Remove a flaw from a character.
    Remove the bonus XP if done during character creation.
    Spend XP after character creation.
    """
    flaw_name = ' '.join(flaw_name)
    await _call_session_and_output(ctx, SESSION.remove_flaw,
                                   ctx.message.author.id, flaw_name)


@remove.command('derangement')
async def remove_derangement(ctx, *derangement_name):
    """Remove a derangement from a character.
    Remove the bonus XP if done during character creation.
    Spend XP after character creation.
    """
    derangement_name = ' '.join(derangement_name)
    await _call_session_and_output(ctx, SESSION.remove_derangement,
                                   ctx.message.author.id, derangement_name)


@remove.command('beast')
async def remove_beast_traits(ctx, amount=1):
    """Remove some beast traits."""
    await _call_session_and_output(ctx, SESSION.remove_beast_traits,
                                   ctx.message.author.id, amount)


@remove.command('morality')
async def remove_morality(ctx):
    """Remove a point of morality."""
    await _call_session_and_output(ctx, SESSION.remove_morality,
                                   ctx.message.author.id)


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


@CLIENT.group('spend')
async def spend(ctx):
    """Spend resources."""
    if not ctx.subcommand_passed:
        await ctx.send("Try !spend with one of these: {}".format(
            ", ".join([command.name for command in spend.commands])))


@spend.command('willpower')
async def spend_willpower(ctx, amount=1):
    """Spend some blood."""
    await _call_session_and_output(ctx, SESSION.spend_willpower,
                                   ctx.message.author.id, amount)


@spend.command('blood')
async def spend_blood(ctx, amount=1):
    """Gain some blood."""
    await _call_session_and_output(ctx, SESSION.spend_blood,
                                   ctx.message.author.id, amount)


@CLIENT.group('gain')
async def gain(ctx):
    """Gain resources."""
    if not ctx.subcommand_passed:
        await ctx.send("Try !gain with one of these: {}".format(
            ", ".join([command.name for command in gain.commands])))


@gain.command('willpower')
async def gain_willpower(ctx, amount=1):
    """Gain some blood."""
    await _call_session_and_output(ctx, SESSION.gain_willpower,
                                   ctx.message.author.id, amount)


@gain.command('blood')
async def gain_blood(ctx, amount=1):
    """Gain some blood."""
    await _call_session_and_output(ctx, SESSION.gain_blood,
                                   ctx.message.author.id, amount)


@gain.command('beast')
async def gain_beast_traits(ctx, amount=1):
    """Gain some beast traits."""
    await _call_session_and_output(ctx, SESSION.gain_beast_traits,
                                   ctx.message.author.id, amount)


@gain.command('morality')
async def gain_morality(ctx):
    """Gain some morality."""
    await _call_session_and_output(ctx, SESSION.gain_morality,
                                   ctx.message.author.id)


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
