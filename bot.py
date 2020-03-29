#! /usr/bin/env python3
"""Discord based game bot."""
import json
import random

from discord import Game, DMChannel, TextChannel, utils, ChannelType
from discord.ext.commands import Bot

from secret_hitler.exceptions import (
    GameAlreadyRunning,
    GameEnded,
    GameInProgress,
    GameNotRunning,
    GameNotStarted,
    InvalidPolicyType,
    NotEnoughPlayers,
    NotPresidentTurn,
    PlayerLimitReached,
)
from secret_hitler.tracker import GameTracker


CLIENT = Bot(command_prefix='!')
CONFIG = {}
TRACKER = GameTracker()


def load_config(path):
    """Load the configuration"""
    with open(path) as conf_handle:
        return json.load(conf_handle)


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
    except TypeError:
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
        results.append(random.randint(1, sides + 1))

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
        name="Secret Hitler (0 games)",
    ))


@CLIENT.command()
async def hello(ctx):
    """Respond to a greeting"""
    await ctx.send("Shall we play a game?")


async def _get_id_from_name(ctx, player):
    """Translate the user's name to their ID"""
    return ctx.message.server.get_member_named(player).id


async def _get_game(ctx, name):
    """Get the game for this channel"""
    game = TRACKER.current_games.get(name)
    if not game:
        await ctx.send("No game exists in channel {}.".format(name))
    return game


async def _is_text_channel(ctx, message):
    """Ensure we're operating on a text channel. Complain with the given
    message if we're not"""
    if not isinstance(ctx.channel, TextChannel):
        await ctx.send(message)
        return False
    return True


async def _is_private_channel(ctx, message):
    """Ensure we're operating on a private channel. Complain with the given
    message if we're not"""
    if not isinstance(ctx.channel, DMChannel):
        await ctx.send(message)
        return False
    return True


@CLIENT.command()
async def start(ctx):
    """Start a game of Secret Hitler"""
    if not await _is_text_channel(
            ctx,
            message="The game must be cancelled in a text channel.",
    ):
        return
    try:
        TRACKER.start_game(ctx.channel.name, ctx.message.author.id)
        await ctx.send(
            'Preparing to start game.\n'
            'Players can join or leave with !join and !leave.\n'
            'The game can only be played with 5 - 10 players.\n'
            'Once all players have joined, enter !go to start!'
        )
        await CLIENT.change_presence(activity=Game(
            name="Secret Hitler ({} games)".format(len(TRACKER.current_games))
        ))
    except GameAlreadyRunning as err:
        await ctx.send(str(err))


@CLIENT.command()
async def cancel(ctx):
    """Cancel a game of Secret Hitler"""
    if not await _is_text_channel(
            ctx,
            message="The game must be cancelled in the appropriate channel.",
    ):
        return

    try:
        TRACKER.cancel_game(ctx.channel.name)
        await ctx.send('Game cancelled.')
        await CLIENT.change_presence(activity=Game(
            name="Secret Hitler ({} games)".format(len(TRACKER.current_games))
        ))
    except GameNotRunning as err:
        await ctx.send(str(err))


@CLIENT.command()
async def join(ctx):
    """Join a game of secret hitler that is about to start"""
    if not await _is_text_channel(
            ctx,
            message="The game must be joined in the appropriate channel.",
    ):
        return

    game = await _get_game(ctx, ctx.channel.name)
    if not game:
        return

    try:
        game.add_player(ctx.message.author.id)
        await ctx.send(
            "Welcome to the game, {}. "
            "There are currently {} players. "
            "When you are all ready to start, say !go".format(
                ctx.message.author.display_name,
                len(game.player_ids),
            )
        )
    except GameInProgress as err:
        await ctx.send(str(err))
    except PlayerLimitReached as err:
        await ctx.send(str(err))


@CLIENT.command()
async def leave(ctx):
    """Leave a game of secret hitler that is about to start"""
    if not await _is_text_channel(
            ctx,
            message="The game must be joined in the appropriate channel.",
    ):
        return

    game = await _get_game(ctx, ctx.channel.name)
    if not game:
        return

    try:
        game.remove_player(ctx.message.author.id)
        await ctx.send(
            "Sorry to see you go, {}. "
            "There are currently {} players.".format(
                ctx.message.author.display_name,
                len(game.player_ids),
            )
        )
    except GameInProgress as err:
        await ctx.send(str(err))


@CLIENT.command()
async def who(ctx):
    """List the players of a game of secret hitler"""
    if not await _is_text_channel(
            ctx,
            message="The game must be joined in the appropriate channel.",
    ):
        return

    game = await _get_game(ctx, ctx.channel.name)
    if not game:
        return

    await ctx.send(
        'Current players: {}'.format(
            ', '.join(CLIENT.get_user(user_id).display_name
                      for user_id in game.player_ids),
        )
    )


@CLIENT.command()
async def go(ctx):  # pylint: disable=invalid-name
    """Start a game of secret hitler now that players have joined"""
    if not await _is_text_channel(
            ctx,
            message="The game must be started in the appropriate channel.",
    ):
        return

    game = await _get_game(ctx, ctx.channel.name)
    if not game:
        await ctx.send("You should !start first to get players.")
        return

    try:
        await ctx.send(game.launch_game)
        for player in [CLIENT.get_user(user_id) for user_id in game.player_ids]:
            await player.send(game.get_starting_knowledge(player.id))
    except GameInProgress as err:
        await ctx.send(str(err))
    except GameEnded as err:
        await ctx.send(str(err))
    except NotEnoughPlayers as err:
        await ctx.send(str(err))


@CLIENT.command()
async def nominate(ctx, player):
    """Allow the president to nominate their chancellor"""
    if not await _is_text_channel(
            ctx,
            message="The nomination must be declared publically.",
    ):
        return

    game = await _get_game(ctx, ctx.channel.name)
    if not game:
        await ctx.send("You should !start first to get players.")
        return

    if not game.round_state == 'Election':
        await ctx.send(
            'Nomination is only applicable during the Election stage.'
        )
        return

    await ctx.send(game.nominate(await _get_id_from_name(ctx, player)))
    await ctx.send(
        "Everyone can now privately say '!vote {channel} ja' or "
        "'!vote {channel} nein'".format(channel=ctx.channel.name)
    )


@CLIENT.command()
async def vote(ctx, channel, selected_vote):
    """Allow everyone to vote on a proposed government"""
    game = await _get_game(ctx, channel)
    if not game:
        await ctx.send("Couldn't find game {}.".format(channel))
        return

    if not game.round_state == 'Election' or not game.chancellor:
        await ctx.send('Voting can only be performed in an election after a'
                       'chancellor is nominated.')
        return

    if not await _is_private_channel(
            ctx,
            message=(
                "Voting should be performed privately. "
                "Nice attempt to mislead the others though! "
                "Don't worry, it's just between you and... us."
            ),
    ):
        return

    if selected_vote.lower() == 'ja':
        selected_vote = True
    elif selected_vote.lower() == 'nein':
        selected_vote = False
    else:
        await ctx.send("You must vote either 'ja' or 'nein'.")
        return

    result = game.cast_vote(ctx.message.author.id, selected_vote)
    if result:
        utils.get(ctx.message.server.channels, name=channel,
                  type=ChannelType.text).send(result)

    try:
        TRACKER.update_game_on_completion(channel)
        return
    except GameNotRunning:
        # Race condition, state will have been updated anyway.
        return

    if not game.end_state:
        CLIENT.get_user(game.president).send(
            "Discard a policy with '!discard.{channel} Liberal' "
            "or '!discard {channel} Fascist.' "
            'Available policies: {policies}'.format(
                channel=channel,
                policies=', '.join(game.president_policies),
            ),
        )


@CLIENT.command()
async def discard(ctx, channel, policy):
    """Allow the president to discard a policy"""
    game = await _get_game(ctx, channel)
    if not game:
        await ctx.send("Couldn't find game {}.".format(channel))
        return

    is_president = ctx.message.author.id == game.president

    if not game.round_state == 'Legislative Session' or not is_president:
        await ctx.send('Discarding can only be performed in a legistlative '
                       'session by the president.')
        return

    if not await _is_private_channel(
            ctx,
            message=(
                "Discarding should be performed privately. "
                "Nice attempt to mislead the others though! "
                "Don't worry, it's just between you and... us."
            ),
    ):
        return

    try:
        await ctx.send(game.discard(policy))
    except NotPresidentTurn as err:
        await ctx.send(str(err))
        return
    except InvalidPolicyType as err:
        await ctx.send(str(err))
        return

    CLIENT.get_user(game.chancellor).send(
        "Select a policy with '!select.{channel} Liberal' "
        "or '!select {channel} Fascist.' "
        'Available policies: {policies}'.format(
            channel=channel,
            policies=', '.join(game.chancellor_policies),
        ),
    )


@CLIENT.command()
async def select(ctx, channel, policy):
    """Allow the chancellor to select a policy"""
    game = await _get_game(ctx, channel)
    if not game:
        await ctx.send("Couldn't find game {}.".format(channel))
        return

    is_chancellor = ctx.message.author.id == game.chancellor

    if not game.round_state == 'Legislative Session' or not is_chancellor:
        await ctx.send('Discarding can only be performed in a legistlative '
                       'session by the president.')
        return

    if not await _is_private_channel(
            ctx,
            message=(
                "Policy selection should be performed privately. "
                "Nice attempt to mislead the others though! "
                "Don't worry, it's just between you and... us."
            ),
    ):
        return

    try:
        utils.get(ctx.message.server.channels, name=channel,
                  type=ChannelType.text).send(game.select_policy(policy))
    except InvalidPolicyType as err:
        await ctx.send(str(err))
        return

    if policy not in game.chancellor_policies:
        await ctx.send(
            "Nice try, but you can't choose a policy you don't have. "
            "The policy was automatically chosen."
        )

    if game.round_stage == 'Executive Action':
        power_command = {
            'Investigate Loyalty': '!investigate <player>',
            'Call Special Election': '!elect <player>',
            'Policy Peek': '!peek',
            'Execution': '!execute <player>',
        }[game.presidential_power]
        utils.get(
            ctx.message.server.channels,
            name=channel,
            type=ChannelType.text
        ).send(
            'The President must now act with: {}'.format(power_command)
        )


async def _act(ctx, target=None):
    """Generic presidential power action"""
    if not await _is_text_channel(
            ctx,
            message=(
                "Executive action should be performed publically."
            ),
    ):
        return

    game = await _get_game(ctx, ctx.channel.name)

    if not game:
        await ctx.send("Couldn't find game {}.".format(ctx.channel.name))
        return

    is_president = ctx.message.author.id == game.president

    if not game.round_state == 'Executive Action' or not is_president:
        await ctx.send('Executive actions can only be performed during '
                       'Executive Action by the president.')
        return

    if target:
        target = await _get_id_from_name(ctx, target)

    private, public = game.enact_power(target)

    await ctx.send(public)
    ctx.message.author.send(private)


@CLIENT.command()
async def investigate(ctx, target):
    """Presidential investigation action"""
    await _act(ctx, target)


@CLIENT.command()
async def peek(ctx):
    """Presidential policy peek action"""
    await _act(ctx)


@CLIENT.command()
async def execute(ctx, target):
    """Presidential execution action"""
    await _act(ctx, target)


@CLIENT.command()
async def elect(ctx, target):
    """Presidential special election action"""
    await _act(ctx, target)


@CLIENT.command()
async def veto(ctx):
    """Chancellor's veto action"""
    if not await _is_text_channel(
            ctx,
            message=(
                "Veto should be performed publically."
            ),
    ):
        return

    game = await _get_game(ctx, ctx.channel.name)

    if not game:
        await ctx.send("Couldn't find game {}.".format(ctx.channel.name))
        return

    is_chancellor = ctx.message.author.id == game.chancellor

    if game.policies.count('Fascist') < 5:
        await ctx.send('Vetos can only be requested when there are 5 Fascist '
                       'policies.')
        return

    if not game.round_state == 'Legislative Session' or not is_chancellor:
        await ctx.send('Vetos can only be requested during Legislative Session'
                       'by the chancellor.')
        return

    game.veto()
    await ctx.send('A veto has been requested. The President can confirm '
                   'this by saying !confirm. Otherwise, the Chancellor must '
                   '!select a policy.')


@CLIENT.command()
async def confirm(ctx):
    """President's veto confirmation"""
    if not await _is_text_channel(
            ctx,
            message=(
                "Veto should be confirmed publically."
            ),
    ):
        return

    game = await _get_game(ctx, ctx.channel.name)

    if not game:
        await ctx.send("Couldn't find game {}.".format(ctx.channel.name))
        return

    is_president = ctx.message.author.id == game.president

    if not game.veto_request:
        await ctx.send('The president can only confirm a veto after it is '
                       'requested by the chancellor saying !veto.')

    if not game.round_state == 'Legislative Session' or not is_president:
        await ctx.send('Vetos can only be confirmed during Legislative Session'
                       'by the president.')
        return

    await ctx.send(game.veto_confirm())


@CLIENT.command()
async def show(ctx):
    """Show the board state"""
    if not await _is_text_channel(
            ctx,
            message=(
                "Show can only be called publically."
            ),
    ):
        return

    game = await _get_game(ctx, ctx.channel.name)

    if not game:
        await ctx.send("Couldn't find game {}.".format(ctx.channel.name))
        return

    try:
        fields = game.get_fascist_policy_powers()
    except GameNotStarted as err:
        await ctx.send(str(err))
        return

    key = {
        'Empty field with no power': u"\u25FB\uFE0F",
        'Policy Peek': u"\U0001F52E",
        'Investigate Loyalty': u"\U0001F50E",
        'Execution': u"\U0001F5E1",
        'Call Special Election': u"\U0001F454",
        'Fascists win': u"\u2620",
        'Liberals win': u"\U0001F54A",
        'Occupied field': u"\U0001F0A0",
    }

    fascist_row = [
        key.get(field, u"\u25FB\uFE0F") for field in fields
    ]
    fascist_row.append(key['Fascists win'])
    liberal_row = [
        u"\u25FB\uFE0F" for i in range(4)
    ]
    liberal_row.append(key['Liberals win'])

    for i in range(game.policies.count('Fascist')):
        fascist_row[i] = key['Occupied field']

    for i in range(game.policies.count('Liberal')):
        liberal_row[i] = key['Occupied field']

    key_output = ''
    for k in sorted(key.keys()):
        key_output += '{}: {}\n'.format(k, key[k])

    await ctx.send(
        'Game board:\n'
        'Fascist: {fascist}\n'
        'Liberal: {liberal}\n'
        '\n'
        'Key:\n'
        '{key}'.format(
            fascist=''.join(fascist_row),
            liberal=''.join(liberal_row),
            key=key_output,
        )
    )


@CLIENT.command()
async def stats(ctx):
    """Show the stats"""
    stat_output = ''
    for stat in sorted(TRACKER.stats.keys()):
        stat_output += '{}: {}\n'.format(
            stat,
            TRACKER.stats[stat],
        )
    await ctx.send(stat_output)


if __name__ == '__main__':
    CONFIG = load_config('config.json')
    CLIENT.run(CONFIG['token'])
