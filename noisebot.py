#! /usr/bin/env python3
"""Discord based game bot."""
import asyncio
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
    print('Available noises: {}'.format(
        ', '.join([
            track[:-4]
            for track in os.listdir('tracks')
            if track.endswith('.mp3')
        ]),
    ))


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


# Example- make more named sections like this to have specific sound commands.
# This example will play the tracks/roar.mp3 into the voice channel you are in
# whenever you say .roar
# @CLIENT.command()
# async def roar(ctx):
#     """Play a lion's roar!"""
#     await _play(ctx, 'roar')


if __name__ == '__main__':
    CONFIG = load_config('config.json')
    CLIENT.run(CONFIG['token'])
