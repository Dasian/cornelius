# Cornelius
Custom discord bot made for VTuber Valentina Chisei. Creates and posts embedded messages to a server by
running commands through private messages. Additional server features added on request such as AI text to speech
in voice channels and sending notifications for server events. Made with love and [discord.py](https://github.com/Rapptz/discord.py)

## Features
- All privileged commands are controlled through pms with a recognized admin (env file)
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
This file contains a list of values which need to be filled in order to activate full bot functionality.

## Running
Once the .env file is filled you can run the bot using the command
```bash
python3 main.py
```

## Usage
There are a lot of commands. Run corn?help in a server to get a list of available server commands. Run
corn?help in a private message to get a list of admin commands (if authorized to do so)

# TODO
- Implement list template name and preview template
- Improve readme
- Make confirmation code into own helper function
- Make formatting consistent
