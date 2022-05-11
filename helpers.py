#!/usr/bin/env python3

from env import admin_email_user
import email.message
import secrets

class RPHUser(object):
    def __setup_message__(self, verbose):
        messagetext = f'''\
Dear {self.name},

Your email settings are detailed below:

Username:           {self.rph_email}
Password:           {self.rph_pass}
Webmail:            https://rphaven.co.uk/webmail/
Incoming Server:    rphaven.co.uk
IMAP Port:          993
POP3 Port:          995
Outgoing Server:    rphaven.co.uk
SMTP Port:          465

Please be aware that although your password is not saved on the system \
that generated it, you should still change it as soon as possible for your \
security.
If you have any problems, please open a ticket on discord.

Regards,
Sanchit
'''
        self.message = email.message.EmailMessage()
        self.message['From'] = admin_email_user
        self.message['To'] = self.email_addr
        self.message['Subject'] = 'RPHaven Email Account'
        self.message.set_content(messagetext)
        if verbose:
            print("Created email")

    def __init__(self, email_addr, name, rph_pass=None, rph_email=None, verbose=True):
        valid_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&()*+,-./:;<=>?@[\]^_{|}~"
        if rph_email is None:
            rph_email = f'{name.lower()}@rphaven.co.uk'
        if rph_pass is None:
            rph_pass = ''.join(secrets.choice(valid_chars) for i in range(15))
        self.email_addr = email_addr
        self.name = name
        self.rph_email = rph_email
        self.rph_pass = rph_pass
        if verbose:
            print("Created user")
        self.__setup_message__(verbose)

    def send_email(self, server, verbose=True):
        if verbose:
            print(f"Sending email to {self.email_addr}")
            print(f"\n{self.message.as_string()}")
        server.sendmail("sanchit@rphaven.co.uk", self.email_addr, self.message.as_string())
    
    def __repr__(self) -> str:
        return f'RPHUser object at {hex(id(self))}: Email: {self.rph_email} Personal Email: {self.email_addr}'

class RPHBranch(object):
    def __init__(self, name, **kwargs):
        self._name = name

        if 'rss_feed' in kwargs:
            self.rss_feed = kwargs['rss_feed']
            self.feed_base_url = 'https://rphaven.co.uk/rphavenrss'
        else:
            self._rss_feed = None
            self.feed_base_url = None
        
        self._discord_channel, self._discord_role = None, None
        if 'discord_channel' in kwargs:
            self.discord_channel = kwargs['discord_channel']
        if 'discord_role' in kwargs:
            self.discord_role = kwargs['discord_role']
    
    @property
    def name(self):
        return self._name
    
    @property
    def rss_feed(self):
        return f'{self.feed_base_url}/{self._rss_feed}/'
    @rss_feed.setter
    def rss_feed(self, new_url):
        if new_url[:3] in ['http', 'rss:']:
            self._rss_feed = new_url.split('/')[-1]
        else:
            self._rss_feed = new_url.strip('/')
    
    @property
    def discord_channel(self):
        return self._discord_channel
    @discord_channel.setter
    def discord_channel(self, newval):
        if type(newval) is not int:
            raise TypeError("discord_channel must be of type int")
        self._discord_channel = newval
    
    @property
    def discord_role(self):
        return self._discord_role
    @discord_role.setter
    def discord_role(self, newval):
        if type(newval) is not int:
            raise TypeError("discord_role must be of type int")
        self._discord_role = newval
