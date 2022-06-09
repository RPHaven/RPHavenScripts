#!/usr/bin/env python3

import datetime
import feedparser
import hashlib
import json
import os
import peewee

db = peewee.SqliteDatabase(os.path.dirname(os.path.realpath(__file__)) + '/rphbot.db')
db.connect()

class RPHBranch(peewee.Model):
    class Meta:
        database = db
    day_constraints = [peewee.Check('check_day < 8'), peewee.Check('check_day > 0')]
    name = peewee.TextField(unique=True)
    rss_feed = peewee.TextField(null=True)
    discord_channel = peewee.IntegerField(null=True)
    discord_role = peewee.IntegerField(null=True)
    check_time = peewee.TimeField(null=True)
    check_day = peewee.IntegerField(null=True, constraints=day_constraints)
    last_update_hash = peewee.TextField(null=True)
    last_update_date = peewee.DateTimeField(null=True)

    def check_games_update(self):
        if self.rss_feed is None:
            return False, "No RSS feed to check!"
        data = feedparser.parse(self.rss_feed)
        latest = data['entries'][0]['summary_detail']['value']
        entry_hash = hashlib.sha256(latest.encode()).hexdigest()
        if entry_hash == self.last_update_hash:
            return False, "No update since last posting"
        self.last_update_hash = entry_hash
        self.last_update_date = datetime.datetime.now()
        self.save()
        return True, entry_hash
    
db.create_tables([RPHBranch])

class Branch:
    def get_branch(self, name):
        return RPHBranch.select().where(RPHBranch.name == name).first()

    def create(self, args):
        if len(args) == 0:
            return '''Usage:
`%branch create name {"option1": "value1", ...}`
name: Required, the name of the branch to create. This cannot be changed.
options:
rss_feed: The url of the RSS feed.
discord_channel: The discord ID of the channel to post in.
discord_role: The discord ID of the role to notify when posting.
check_time: The time of day to check for games updates to send. UTC.
check_day: The day of the week to check for games updates to send. 1-7 where 1 is Monday.
'''
        name = args[0]
        if self.get_branch(name) is not None:
            return f'Branch {name} already exists!'
        newbranch = RPHBranch(name=name)

        try:
            creation_data = {}
            if len(args) > 1:
                creation_data = json.loads(" ".join(args[1:]))
        except ValueError as e:
            return f'Something went wrong unpacking your arguments:\n```{e}```'

        for update in creation_data.keys():
            if update in ['name', 'rss_feed', 'discord_channel', 'discord_role', 'check_time', 'check_day']:
                setattr(newbranch, update, creation_data[update])
            else:
                return f'{update} is not a valid key!'

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
    
    def show_all(self, args):
        names = []
        for item in RPHBranch.select():
            names.append(item.name)
        names = "\n".join(names)
        return f'All branches:\n{names}'

    def execute_feeds(self, args):
        if len(args) > 0 and args[0] == 'help':
            return '''Usage:
%branch feeds [name]
Runs the checker for the RSS feeds.
name: Optional, if given, only checks the feed of this branch.
'''
        for item in RPHBranch.select():
            return item.check_games_update()
        return "Command is currently under construction - see log file for more info"

    def run(self, command):
        subcommands = self.subcommands
        if len(command) == 0 or command[0] not in subcommands.keys():
            return f'Available subcommands: {", ".join(subcommands.keys())}'
        return subcommands[command[0]](self, command[1:])

    subcommands = {
        'create': create,
        'show': read,
        'update': update,
        'delete': delete,
        'list': show_all,
        'feeds': execute_feeds
    }
