# Cornelius
Custom discord bot made for VTuber Valentina Chisei. Creates and posts embedded messages to a server by
running commands through private messages. Additional server features added on request such as AI text to speech
in voice channels and sending notifications for server events. Made with love and [discord.py](https://github.com/Rapptz/discord.py)

## Features
- All privileged commands are controlled through pms with a recognized admin (`.env` file)
- Create, save, and send custom embedded messages
- Send regular messages through the bot to a server
- Ping roles with with an embedded message
- Chat revival command with cooldown
- Custom voice tts (text to speech) using uberduck ai
- Sends custom embeds when server is boosted
- Custom status message

## Installation
### Python Virtual Environment (optional)
Isolates packages from the rest of your system. The environment needs to be activated before you can run the scripts.
> First command creates a venv, second command activates it.
#### Windows
```cmd
python -m venv .cornelius
call .cornelius/scripts/activate.bat
```
#### Linux
```bash
python3 -m venv .cornelius  
source .cornelius/bin/activate
```
### Install Python Libraries
```bash
pip3 install -r requirements.txt
```
### .env File
This file is necessary to fill sensitive values and unlock the bot's full capabilities.
A template file `env-template.txt` is provided and should be renamed to `.env`
```
# template .env file
# copy or rename to .env and fill with the appropriate values

# discord bot values
# values generated in the discord developer portal
# https://discord.com/developers/applications
TOKEN=
PERMS=

# admin setup
# determines how many/who has privileged command access
# increase to desired number and add that number of tokens
NUM_ADMINS=1
ADMIN0=
#ADMIN1= user discord token here
#ADMIN2= this is the third admin user

# uberduck api (ai text to speech) [optional]
# https://www.uberduck.ai/
UBERDUCK_API_KEY=
UBERDUCK_API_SECRET=
```

## Running
Once the `.env` file is filled you can run the bot using the command
```bash
python3 main.py
```

## Usage
Bot commands are prefixed with `corn?`

### Admin Commands
Run `corn?help all` in a direct
message to get a list of admin commands (if authorized in the `.env` file)
```
Misc:
corn?help - displays this message

Editing Commands
corn?new - start new embedded message
corn?preview - view a preview of the message
corn?add [attribute] [value]- adds/updates attribute to the current msg
corn?remove [attribute] - removes attribute from the current msg

Template Commands
corn?templates - shows the saved embedded messages with their name
corn?load [name]- loads a saved embedded message as the current message
corn?save [name]- saves the embedded message on the server, for future use
corn?delete [name] deletes template

Publishing Commands
corn?channels - get a list of all channel_ids you can post to
corn?publish [channel_id] - publishes the current msg to the channel_id
corn?speak [channel_id] [message] - send a normal discord message to the channel id
corn?roles - get a list of all roles you can ping
corn?ping [role_name] [channel_id] - ping a role and publish current embedded msg
corn?set [event_name] [optional:msg] - set the current embedded message to send when a server event is triggered
corn?status [status_type] [status] - set the status of the bot (sidebar)

Single Attributes
title - text
color - hex
description - text
title-url - url
type - text
Possible values for type: rich, image, video, gifv, article, link

Grouped Attributes
author-[name/url/icon_url] - text, url, url
fields-[name/value/inline] - text, text, True/False; Not implemented yet srry
footer-[text/icon_url] - text, url
image-[url/proxy_url/width/height] - url, url, number
thumbnail-[url/proxy_url/width/height] - url, url, number, number
video-[url/width/height] - url, number, number
```

### Server Commands
Run `corn?help` in a server to get a list of available server commands
```
corn?hey
Get a random val quote

corn?revive
Ping the 'chat revive' role to revive this channel [15 min global cooldown]

corn?pic
Gives info on the Pic Perms role

corn?voice_search [query]
Search for available text to speech voices [admin only]

corn?imitate [voice] [message]
Send a text to speech message into a vc [admin only]

corn?help
Display this msg
```

# TODO
- [ ] Implement list template name and preview template
- [ ] Make confirmation code into own helper function
- [X] Improve readme
