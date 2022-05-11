#!/usr/bin/env python3

import smtplib, ssl, time
from env import admin_email_user, admin_email_pass
from helpers import RPHUser

def from_datafile(server):
    with open('data.txt', 'r') as f:
        for line in f:
            # This just gives us a basic comment system
            if line[0] == '#':
                continue
            data = list(filter(None, line.strip().split('\t')))
            newuser = RPHUser(data[0], data[1], data[3], data[2])
            # personal email, first name, password, account name
            newuser.send_email(server, verbose=False)
            time.sleep(1)

if __name__ == '__main__':
    port = 465
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("rphaven.co.uk", port, context=context) as server:
        server.login(admin_email_user, admin_email_pass)
        print("Logged in!")

        # If we're sending emails to everyone in the datafile, use this instead
        from_datafile(server)
