# RPHaven Scripts
This is a collection of scripts used to administrate RPHaven's systems.

## env.py
Create this file if you want to use the scripts in here.
Many of the other scripts import secrets from here.

## migration.py
A complex script used to migrate RPH from one email host to another. Don't mess
with it unless you know what you're doing.

## email_setup.py
Used to tell people about their email accounts. Cannot create them due to
backend limitations. Will generate a password for you if you leave the password
field blank.

To use, create a new RPHUser object in the main block at the end of the script.
