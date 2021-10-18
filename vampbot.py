#! /usr/bin/env python3
"""Discord based game bot."""
import json
from math import ceil
import random

from discord import Embed, Game
from discord.ext.commands import Bot, is_owner
import websockets

from vampchar.session import BadInput, Session

CLIENT = Bot(command_prefix='!')
CONFIG = {}
SESSION = Session()
DOT = '•'
NO_DOT = '◦'
SKULL = '🕱'


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
async def reset(ctx):
    """Reset your character."""
    await _call_session_and_output(ctx, SESSION.reset, ctx.message.author.id)


@CLIENT.command()
async def undo(ctx):
    """Undo the last change to your character."""
    await _call_session_and_output(ctx, SESSION.undo, ctx.message.author.id)


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
async def set_(ctx):
    """Set various character attributes"""
    if not ctx.subcommand_passed:
        await ctx.send("Try !set with one of these: {}".format(
            ", ".join([command.name for command in set_.commands])))


@set_.command('attribute')
async def set_attribute(ctx, attribute, value):
    """Set an attribute to a given value."""
    await _call_session_and_output(ctx, SESSION.set_attribute,
                                   ctx.message.author.id, attribute, value)


@set_.command('skill')
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


@set_.command('background')
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


@set_.command('discipline')
async def set_discipline(ctx, *args):
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


@set_.command('clan')
async def set_clan(ctx, *clan_name):
    """Set a character's clan membership."""
    await _call_session_and_output(ctx, SESSION.set_clan,
                                   ctx.message.author.id, ' '.join(clan_name))


@set_.command('name')
async def set_name(ctx, *name):
    """Set a character's character name."""
    await _call_session_and_output(ctx, SESSION.set_name,
                                   ctx.message.author.id, ' '.join(name))


@set_.command('archetype')
async def set_archetype(ctx, *archetype):
    """Set a character's archetype."""
    await _call_session_and_output(ctx, SESSION.set_archetype,
                                   ctx.message.author.id, ' '.join(archetype))


@set_.command('blood_rate')
async def set_blood_rate(ctx, rate):
    """Set a character's blood burn rate."""
    await _call_session_and_output(ctx, SESSION.set_blood_burn_rate,
                                   ctx.message.author.id, rate)


@set_.command('healthy_count')
async def set_healthy_count(ctx, count):
    """Set a character's amount of healthy wound levels."""
    await _call_session_and_output(ctx, SESSION.set_healthy_count,
                                   ctx.message.author.id, count)


@set_.command('unhealthy_counts')
async def set_unhealthy_count(ctx, count):
    """Set a character's amount of injured/incapacitated wound levels."""
    await _call_session_and_output(ctx, SESSION.set_unhealthy_counts,
                                   ctx.message.author.id, count)


@set_.command('max_willpower')
async def set_max_willpower(ctx, maximum):
    """Set a character's maximum willpower."""
    await _call_session_and_output(ctx, SESSION.set_max_willpower,
                                   ctx.message.author.id, maximum)


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


# TODO: No pdf output, give nice output
#   Show state (blood, willpower, morality, health)
#   Status (put this in the header as a new, not inline, embed?)
#   Show equipment
# TODO: Clean up and rename this command
@CLIENT.command()
async def emb(ctx):
    embed = Embed(
        title='Character sheet',
    )
    character = SESSION.get_player_dict(ctx.message.author.id)

    # Add header
    header = character['header']
    sect = header['sect'] or 'unaligned'
    title = header['title'] or 'none'
    embed.add_field(
        name=(
            '~~\u200b    \u200b~~**Character**~~\u200b    \u200b~~'
        ),
        value=(
            'Name: {name}\n'
            'Player: {player}\n'
            'Archetype: {archetype}\n'
        ).format(
            name=header['character'],
            player=ctx.message.author.display_name,
            archetype=header['archetype'].title(),
        ),
    )
    embed.add_field(
        name='\u200b',
        value=(
            'Clan: {clan}\n'
            'Sect: {sect}\n'
            'Title: {title}\n'
        ).format(
            clan=header['clan'].title(),
            sect=sect.title(),
            title=title.title(),
        ),
    )
    embed.add_field(
        name='\u200b',
        value=(
            '**XP**\n'
            'Unspent: {unspent}\n'
            'Total: {total}\n'
        ).format(
            unspent=character['xp']['current'],
            total=character['xp']['total'],
        ),
    )

    # Add attributes
    def _format_attribute(attribute):
        output = ''
        value = attribute['value']

        base = min(value, 10)
        output = DOT * base + NO_DOT * (10 - base)
        # Insert a space for readability
        output = output[:5] + ' ' + output[5:]
        output += '\n'

        bonus = max(value - 10, 0)
        output += 'Bonus: '
        output += DOT * bonus + NO_DOT * (5 - bonus)
        output += '\n'

        output += ' '.join(
            focus.title() for focus in attribute['focuses']
        )
        return output

    attributes = character['attributes']
    embed.add_field(
        name=(
            '~~\u200b    \u200b~~**Attributes**~~\u200b    \u200b~~\n'
            'Physical'
        ),
        value=_format_attribute(attributes['physical']),
    )
    embed.add_field(
        name='\u200b\nMental',
        value=_format_attribute(attributes['mental']),
    )
    embed.add_field(
        name='\u200b\nSocial',
        value=_format_attribute(attributes['social']),
    )

    def _make_skill_columns(skills):
        columns = ['\u200b', '\u200b', '\u200b']
        ordered_skills = sorted(list(skills.keys()),
                                key=str.casefold)
        last_finish = 0
        for col in range(3):
            if col == 0:
                finish = ceil(len(skills) / 3)
            elif col == 1:
                remaining = len(skills) - last_finish
                if remaining:
                    finish = last_finish + ceil(remaining / 2)
            else:
                finish = None
            start = last_finish
            last_finish = finish

            for skill in ordered_skills[start:finish]:
                columns[col] += _dotted_display(skill, skills[skill])
        return columns

    def _dotted_display(name, value):
        base = min(value, 5)
        extra = max(value - 5, 0)

        rating_output = DOT * base
        rating_output += NO_DOT * (5 - base)
        if extra:
            rating_output += ' '
            rating_output += DOT * extra
        return '{}: {}\n'.format(name.title(), rating_output)

    # Add skills
    skills = character['skills']
    columns = _make_skill_columns(skills)
    embed.add_field(
        name=(
            '~~\u200b    \u200b~~**Skills**~~\u200b    \u200b~~'
        ),
        value=columns[0],
    )
    for column in columns[1:]:
        embed.add_field(name='\u200b', value=column)

    # Add backgrounds, disciplines, merits, and flaws
    backgrounds = character['backgrounds']
    ordered_backgrounds = sorted(list(backgrounds.keys()),
                                 key=str.casefold)
    embed.add_field(
        name=(
            '~~\u200b                                \u200b~~\n'
            'Backgrounds'
        ),
        value='\u200b' + ''.join(
            _dotted_display(name, backgrounds[name])
            for name in ordered_backgrounds
        ),
    )
    disciplines = character['disciplines']
    ordered_disciplines = sorted(list(disciplines.keys()))
    embed.add_field(
        name='\u200b\nDisciplines',
        value='\u200b' + ''.join(
            _dotted_display(name, disciplines[name])
            for name in ordered_disciplines
        ),
    )
    merits = character['merits_and_flaws']['merits']
    ordered_merits = sorted(list(merits.keys()), key=str.casefold)
    flaws = character['merits_and_flaws']['flaws']
    ordered_flaws = sorted(list(flaws.keys()), key=str.casefold)
    derangements = sorted(character['merits_and_flaws']['derangements'],
                          key=str.casefold)
    output = '\u200b'
    for merit in ordered_merits:
        output += '{} ({})\n'.format(merit.title(), merits[merit])
    for flaw in ordered_flaws:
        output += '{} (-{})\n'.format(flaw.title(), flaws[flaw])
    for derangement in derangements:
        output += '{}\n'.format(derangement.title())
    embed.add_field(
        name='\u200b\nMerits and Flaws',
        value=output,
    )

    def _format_resource(state):
        output = ''
        for pos in range(state['max']):
            # Add a newline every ten and a space every five blood for
            # readability
            if pos % 15 == 0 and pos > 0:
                output += '\n'
            elif pos % 5 == 0 and pos > 0:
                output += ' '

            output += DOT if pos < state['current'] else NO_DOT
        return output

    def _format_health(health_state):
        output = ''

        damage_applied = 0
        for level in ['healthy', 'injured', 'incapacitated']:
            output += '{}: '.format(level.capitalize())

            for pos in range(health_state['levels'][level]):
                if damage_applied < len(health_state['damage']):
                    damage_type = health_state['damage'][damage_applied]
                    if damage_type == 'normal':
                        output += NO_DOT
                    else:
                        output += SKULL
                    damage_applied += 1
                else:
                    output += DOT
            output += '\n'

        if damage_applied < len(health_state['damage']):
            output += 'Excess: '
            for damage_type in health_state['damage'][damage_applied:]:
                if damage_type == 'normal':
                    output += NO_DOT
                else:
                    output += SKULL

        return output

    # Add blood, willpower, morality (incl. beast traits), health
    state = character['state']
    blood_and_willpower_output = _format_resource(state['blood'])
    blood_and_willpower_output += '\n**Willpower**\n'
    blood_and_willpower_output += _format_resource(state['willpower'])
    embed.add_field(
        name=(
            '~~\u200b                                \u200b~~\n'
            'Blood ({}/round)'.format(state['blood']['rate'])
        ),
        value=blood_and_willpower_output,
    )
    embed.add_field(
        name='\u200b\nHealth ({})'.format(
            SESSION.get_health_level(ctx.message.author.id)
        ),
        value=_format_health(state['health']),
    )

    # TODO: From here (morality, beast traits)

    await ctx.send(embed=embed)


def generate_partials(group=None):
    """Generate aliases for all partial matches of commands, recursively."""
    if group is None:
        group = CLIENT
    commands = group.all_commands

    groups = []
    aliases_mapping = {}

    for command_name, command in commands.items():
        if hasattr(command, 'commands'):
            groups.append(command_name)
        found_unambiguous = False
        for pos in range(1, len(command_name)):
            sub = command_name[:pos]
            if found_unambiguous:
                aliases_mapping[command_name].append(sub)
            elif any(c.startswith(sub) for c in commands
                     if c != command_name):
                # This would be an ambiguous alias
                continue
            else:
                aliases_mapping[command_name] = [sub]
                found_unambiguous = True

    for command_name, aliases in aliases_mapping.items():
        command = commands[command_name]
        command.aliases.extend(aliases)
        group.remove_command(command_name)
        group.add_command(command)

    for sub_group in groups:
        generate_partials(commands[sub_group])


if __name__ == '__main__':
    CONFIG = load_config('config.json')
    SESSION.load(CONFIG['vamp_save_path'])
    generate_partials()
    CLIENT.run(CONFIG['token'])
