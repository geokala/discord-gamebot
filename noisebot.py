#! /usr/bin/env python3
"""Discord based game bot."""
import asyncio
import functools
import json
import os
import string

from discord import Game, FFmpegPCMAudio
from discord.ext.commands import Bot
import websockets

CLIENT = Bot(command_prefix='.')
CONFIG = {}


def load_config(path):
    """Load the configuration"""
    with open(path) as conf_handle:
        return json.load(conf_handle)


@CLIENT.event
async def on_ready():
    """Output a message when connected"""
    print("Logged in as " + CLIENT.user.name)
    await CLIENT.change_presence(activity=Game(
        name="Making noise",
    ))
    available_noises = [
        track[:-4]
        for track in os.listdir('tracks')
        if track.endswith('.mp3')
    ]
    print('Available noises: {}'.format(
        ', '.join(available_noises),
    ))
    existing_commands = [
        'play', 'close', 'stop',
    ]
    for noise in available_noises:
        if (
                noise in existing_commands
                or noise[0] in (string.digits + '-')
        ):
            print(
                'Could not create command for {command}. '
                'Please ensure all noises have names that are not in this '
                'list: {existing}\n'
                'Names must not start with a number and must not contain '
                'any hyphen (-) if you wish them to be made into commands.'
                .format(
                    command=noise,
                    existing=', '.join(existing_commands),
                )
            )
        else:
            CLIENT.command(
                name=noise,
                help="Play {} sound".format(noise),
            )(
                func=asyncio.coroutine(
                    functools.partial(_play, track=noise),
                ),
            )
            print('Created command to play {0}: .{0}'.format(noise))


async def _get_voice_client(ctx):
    """Get voice client for this context's relevant channel."""
    channel = ctx.author.voice.channel
    for voice_client in CLIENT.voice_clients:
        if voice_client.channel.id == channel.id:
            return voice_client
    return None


async def _get_voice_channel(ctx):
    """Get the voice channel for a given context."""
    channel = ctx.author.voice.channel
    if await _get_voice_client(ctx):
        return channel
    return await channel.connect()


async def _play(ctx, track):
    """Play a file."""
    valid = string.ascii_letters + string.digits + '_-'
    for char in track:
        if char not in valid:
            print('{} is an invalid track name.'.format(track))
            print('Only the following characters are allowed: {}'.format(
                valid
            ))
            return

    voice = await _get_voice_channel(ctx)
    if voice is None:
        print('Failed to connect to voice channel.')
    else:
        track = FFmpegPCMAudio(os.path.join('tracks', track + '.mp3'))
        voice.play(track)
        while voice.is_playing():
            await asyncio.sleep(1)
        voice.stop()


@CLIENT.command()
async def close(ctx):
    """Disconnect the bot and stop running."""
    if ctx.author.id == CONFIG['owner_id']:
        print("Closing by owner's demand.")
        try:
            await CLIENT.close()
        except websockets.exceptions.ConnectionClosedOK:
            pass


@CLIENT.command()
async def stop(ctx):
    """Stop being noisy."""
    voice = await _get_voice_client(ctx)
    voice.stop()


@CLIENT.command()
async def play(ctx, track):
    """Play the specified noise."""
    await _play(ctx, track)


if __name__ == '__main__':
    CONFIG = load_config('config.json')
    CLIENT.run(CONFIG['token'])
