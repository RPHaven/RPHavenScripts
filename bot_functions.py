#!/usr/bin/env python3

import peewee
from requests import request

db = peewee.SqliteDatabase('rphbot.db')
db.connect()

class RPHBranch(peewee.Model):
    class Meta:
        database = db
    name = peewee.TextField(unique=True)
    rss_feed = peewee.TextField()
    discord_channel = peewee.IntegerField()
    discord_role = peewee.IntegerField()
    
db.create_tables([RPHBranch])

class Branch:
    def get_branch(self, name):
        return RPHBranch.select().where(RPHBranch.name == name).first()

    def create(self, args):
        if len(args) == 0:
            return '''Usage:
`%branch create name [feed] [channel] [role]`
name: Required, the name of the branch to create. This cannot be changed.
feed: Optional, the url of the RSS feed.
channel: Optional, the discord ID of the channel to post in.
role: Optional, the discord ID of the role to notify when posting.'''
        feed, channel, role = [None]*3
        for i, arg in enumerate(args):
            if i == 0:
                name = arg
            elif i == 1:
                feed = arg
            elif i == 2:
                channel = arg
            else:
                role = arg
        if self.get_branch(name) is not None:
            return f'Branch {name} already exists!'
        newbranch = RPHBranch(name=name)
        if feed is not None:
            newbranch.rss_feed = feed
        if channel is not None:
            newbranch.discord_channel = channel
        if role is not None:
            newbranch.discord_role = role
        newbranch.save()
        return f'Created branch {newbranch.name}'

    def read(self, args):
        if len(args) == 0:
            return '''Usage:
`%branch show name`
name: Required, the name of the branch to show information on.'''
        name = args[0]
        request = self.get_branch(name)
        if request is not None:
            return f'\nBranch {request.name}:\nRSS Feed: {request.rss_feed}\nDiscord Channel: ' + \
                f'{request.discord_channel}\nDiscord Role: {request.discord_role}'
        else:
            return f'Could not find a branch named {name}!'

    def update(self, args):
        usage = '''Usage:
`%branch update name key=value`
name: Required, the name of the branch to update
key: Required, the information about the branch to update
\t\tOptions: rss_feed, discord_channel, discord_role
value: Required, the new value

eg. `%branch update lewisham rss_feed=https://rphaven.co.uk/rphavenrss/lewisham-branch/`'''
        try:
            assert len(args) == 2
            name = args[0]
            key = args[1].split('=')[0]
            value = args[1].split('=')[-1]
            assert key != value
        except (AssertionError, IndexError) as error:
            return usage
        branch = self.get_branch(name)
        if branch is None:
            return f'Could not find a branch named {name}!'
        
        branch.update({getattr(RPHBranch, key): value}).execute()
        return f'Updated {name}.\n{key} is now {value}.'

    def delete(self, args):
        if len(args) == 0:
            return '''Usage:
`%branch delete name`
name: Required, the name of the branch to delete. Note: this is irreversible!'''
        name = args[0]
        request = self.get_branch(name)
        if request is not None:
            request.delete().execute()
            return f'Deleted {name}!'
        else:
            return f'Could not find a branch named {name}!'

    def run(self, command):
        subcommands = self.subcommands
        if len(command) == 0 or command[0] not in subcommands.keys():
            return f'Available subcommands: {", ".join(subcommands.keys())}'
        return subcommands[command[0]](self, command[1:])

    subcommands = {
        'create': create,
        'show': read,
        'update': update,
        'delete': delete
    }
