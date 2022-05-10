#!/usr/bin/env python3

# System libs
import argparse
import csv
import os
import re
import requests
import smtplib
import ssl
import subprocess
# Local files
from email_setup import RPHUser
import env

##################################################
#                       Be Aware!                #
#                                                #
# This file is only for functions relating to an #
# actual migration! If the function can be used  #
# outside of this (for rph stuff), put it in a   #
# different file and import it!                  #
#                                                #
# Don't make the server puppy have to bite you!  #
##################################################

def get_cli_args():
    parser = argparse.ArgumentParser(description="Migrate RPHaven emails to a new host")
    parser.add_argument("csvfile", action='store', help="the path to the CSV file containing user data")
    parser.add_argument("--dry-run", action='store_true', default=False, help="don't make changes")
    parser.add_argument("--verbose", action='store_true', default=False, help="more verbose output")
    return parser.parse_args()

def subprocess_ssh(args):
    cmd = subprocess.run(["ssh", "gadmmimy@rphaven.net", "uapi", "--output=json"] + args)
    if cmd.returncode != 0:
        raise SystemError(f'Full response:\n{cmd.args}\n{cmd.stdout}\n{cmd.stderr}')

class User(object):
    def __init__(self, data: list, email_regex: re.Pattern):
        # This check ensures that rows without valid data in them are skipped
        if not email_regex.match(data[3]):
            raise ValueError("Data incomplete")
        self.fullname = data[1]
        self.rph_user = RPHUser(data[2], self.fullname.split(" ")[0], rph_email=data[3], verbose=False)
        self.branch = data[5]
        self.rfrom = [ data[6].lower(), data[7].lower(), data[8].lower(), \
                        data[10].lower(), data[11].lower(), data[12].lower() ]
        self.rfrom = [ x for x in self.rfrom if x != '' ]
        self.GST = True
        if data[18] != "Yes":
            self.GST = False
        self.active = True
        if data[19] != "Active":
            self.active = False
    
    def __repr__(self) -> str:
        return f'User object at {hex(id(self))}: {self.fullname}\nBranch: {self.branch}\nForwarders: ' + \
            f'{self.rfrom}\nGST: {self.GST}\nActive:{self.active}'
    
    def create_email_account(self, dry_run=False, verbose=False):
        if dry_run:
            print(f'Create email account {self.rph_user.rph_email} with password {self.rph_user.rph_pass}')
        else:
            self.rph_user.create_account(verbose)
            if not self.active:
                subprocess_ssh(["Email", "suspend_login", f"email='{self.rph_user.rph_email}'"])
                if verbose:
                    print(f'Suspended login for {self.rph_user.rph_email}')

    def setup_forwarders(self, dry_run=False, verbose=False):
        if any(self.rfrom):
            for address in self.rfrom:
                if dry_run:
                    print(f'Create forwarder from {address} to {self.rph_user.rph_email}')
                else:
                    subprocess_ssh([
                        "Email",
                        "add_forwarder",
                        "domain='rphaven.co.uk'",
                        f"email='{address}'",
                        "fwdopt=fwd",
                        f"fwdemail={self.rph_user.rph_email}"
                    ])
        else:
            if verbose:
                print(f'User {self.rph_user.rph_email} has no forwarders configured.')

    def send_email(self, server: smtplib.SMTP_SSL, dry_run=False, verbose=False):
        if dry_run:
            print(f'Send email to user {self.rph_user.email_addr} for acc {self.rph_user.rph_email}')
            if verbose:
                print(f'User password: {self.rph_user.rph_pass}')
        else:
            self.send_email(server, verbose)
    
    def setup_permissions(self, dry_run=False, verbose=False):
        if dry_run:
            if verbose:
                print(f'Set GST scanning for {self.rph_user.rph_email} to {self.GST}')
                print('Add volunteer role')
        else:
            # TODO GST
            base = "https://rphaven.co.uk/wp/v2/users/"
            user_id = requests.get(f'{base}/')

def parse_csv(infile):
    # Exceptions first
    if infile.split(".")[-1] != "csv":
        raise ValueError(f'{infile} is not a CSV file!')
    if not os.path.exists(infile):
        raise OSError(2, "File not found", args.csvfile)

    email = re.compile("^\S+@\S+$")
    # Create a (giant) list that we can use later in the migration
    userData = []
    with open(infile, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                userData.append(User(row, email))
            except ValueError:
                pass
    return userData

if __name__ == '__main__':
    # Get info
    global args
    args = get_cli_args()
    userData = parse_csv(args.csvfile)

    # Process
    server = smtplib.SMTP_SSL("mail.rphaven.co.uk", 465, context=ssl.create_default_context())
    server.login(env.admin_email_user, env.admin_email_pass)
    for user in userData:
        if args.verbose:
            print(str(user))

        user.create_email_account(dry_run=True, verbose=args.verbose)
        user.setup_forwarders(dry_run=True, verbose=args.verbose)
        input("Once you've entered this information, press enter to continue")
        user.send_email(server, dry_run=args.dry_run, verbose=args.verbose)
        user.setup_permissions(dry_run=True, verbose=args.verbose)
        # Set up discord permissions?
        # Send discord invites?
