#!/usr/bin/env python3

from bot_functions import Branch
from env import discord_token, discord_admin_users
import discord

client = discord.Client()
branch_commands = Branch()

def admin_commands(command):
    subcommands = {
        'branch': branch_commands
    }
    if command[0] not in subcommands.keys():
        return f'Available subcommands: {", ".join(subcommands.keys())}'
    return subcommands[command[0]].run(command[1:])

# to_run = [
#     'branch',
#     'create'
# ]

# output = admin_commands(to_run)
# print(output)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}.')
    print('Ready!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if not message.content.startswith('%'):
        return
    # non-admin commands go here

    if message.author.id in discord_admin_users:
        command = message.content[1:].split(' ')
        output = admin_commands(command)
        await message.channel.send(output)
        return

client.run(discord_token)