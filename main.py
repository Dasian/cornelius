'''
  Runs the bot
  Calls functions (from bot class) based on the command
  Debug info for the log as well
'''

import os
import discord
import datetime
from dotenv import load_dotenv
# local files
import embedder
import server_bot
import admin_cmds as cmd

# retrieve secrets
load_dotenv()
TOKEN = os.environ['TOKEN']
PERMS = os.environ['PERMS']
NUM_ADMINS = int(os.environ['NUM_ADMINS'])
admins = []
for i in range(0, NUM_ADMINS):
  s = "ADMIN" + str(i)
  admins.append(int(os.environ[s]))

# generate command list
cmd_start = '!' # CHANGE THIS BEFORE MERGING WITH MAIN
server_cmds = ['help', 'hey']
admin_cmds =['help', 'new', 'preview', 'publish', 'add', 'remove', 'templates', 'load', 'save', 'delete', 'channels']
for i in range(len(server_cmds)):
  server_cmds[i] = cmd_start + server_cmds[i]
for i in range(len(admin_cmds)):
  admin_cmds[i] = cmd_start + admin_cmds[i]

# publishing vars
confirmation = False
publish_channel = None

# Connect to client (all intents enabled but could specify if you care)
client = discord.Client(intents=discord.Intents.all())

# Run when the bot is starting up
@client.event
async def on_ready():
  print("Logged in as {0.user}".format(client),' on ', datetime.datetime.now())

# Run whenever a message is received in any channel/dm (commands)
@client.event
async def on_message(message):
  # ignore messages from the bot
  if message.author == client.user:
    return

  # debug info
  print()
  print('*******************DEBUG******************')
  print("User ID:", message.author.id)
  print("Author:", message.author)
  print("Msg Content:", message.content, type(message.content))
  print("Msg Guild:", message.guild, type(message.guild))
  print('******************************************')
  print()

  # Admin Commands
  # admin is recognized and cmds are sent through pm
  if message.author.id in admins and not message.guild:
    print("*************ADMIN COMMAND*************")
    print("User:", message.author)
    print("Command:",message.content)

    # publish confirmation
    global confirmation, publish_channel
    if confirmation:
      if message.content.lower() == 'yes':
        await message.channel.send('poggies')
        await publish_channel.send(embed=embedder.preview())
      else:
        await message.channel.send('stop wasting my time bihtc')
      confirmation = False
      return

    # generate and publish embedded messages
    try:
      if message.content.startswith(admin_cmds[0]): # help
        await cmd.help(message)
      elif message.content.startswith(admin_cmds[1]): # new
        await cmd.new(message)
      elif message.content.startswith(admin_cmds[2]): # preview
        await cmd.preview(message)
      elif message.content.startswith(admin_cmds[3]): # publish
        confirmation, publish_channel = await cmd.publish(message, client)
      elif message.content.startswith(admin_cmds[10]): # channels
        await cmd.show_channels(message, client)
      elif message.content.startswith(admin_cmds[4]): # add
        await cmd.add(message)
      elif message.content.startswith(admin_cmds[5]): # remove
        await cmd.remove(message)
      elif message.content.startswith(admin_cmds[6]): # templates
        await cmd.templates(message)
      elif message.content.startswith(admin_cmds[7]): # load
        await cmd.load(message)
      elif message.content.startswith(admin_cmds[8]): # save
        await cmd.save(message)
      elif message.content.startswith(admin_cmds[9]): # delete
        await cmd.delete(message)
      else:
        await cmd.invalid(message)
    except Exception as e:
      print("Exception:", e)
      await message.channel.send("Something went wrong :(((")
      await message.channel.send("here some nerd shit: " + str(e))
      
  # Server commands
  elif message.guild:
    # send a random message anywhere
    if message.content.startswith(server_cmds[0]): # help
      help = server_bot.help()
      await message.channel.send(help)
    elif message.content.startswith(server_cmds[1]): # hey
      msg = server_bot.random_message()
      await message.channel.send(msg)
  
  # Random patron dm
  else:
    await message.channel.send("why we talk in secret?")
    await message.channel.send(server_bot.random_message())
    
# Run client
client.run(TOKEN)
