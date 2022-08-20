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
import admin_cmds
import server_cmds


# global vars
cmd_start = '!' # CHANGE THIS BEFORE MERGING WITH MAIN
server_prefix = ['help', 'hey']
admin_prefix =['help', 'new', 'preview', 'publish', 'add', 'remove', 'templates', 'load', 'save', 'delete', 'channels']
admins = []
confirmation = False
publish_channel = None
# Connect to client (all intents enabled but could specify if you care)
client = discord.Client(intents=discord.Intents.all())

# guess what this function is
def main():
  # retrieve secrets
  global admins
  load_dotenv()
  TOKEN = os.environ['TOKEN']
  PERMS = os.environ['PERMS']
  NUM_ADMINS = int(os.environ['NUM_ADMINS'])
  for i in range(0, NUM_ADMINS):
    s = "ADMIN" + str(i)
    admins.append(int(os.environ[s]))

  # generate cmd prefix list
  global admin_prefix, server_prefix, cmd_start
  for i in range(len(server_prefix)):
    server_prefix[i] = cmd_start + server_prefix[i]
  for i in range(len(admin_prefix)):
    admin_prefix[i] = cmd_start + admin_prefix[i]

  # Run client
  client.run(TOKEN)


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
      if message.content.startswith(admin_prefix[0]): # help
        await admin_cmds.help(message)
      elif message.content.startswith(admin_prefix[1]): # new
        await admin_cmds.new(message)
      elif message.content.startswith(admin_prefix[2]): # preview
        await admin_cmds.preview(message)
      elif message.content.startswith(admin_prefix[3]): # publish
        confirmation, publish_channel = await admin_cmds.publish(message, client)
      elif message.content.startswith(admin_prefix[10]): # channels
        await admin_cmds.show_channels(message, client)
      elif message.content.startswith(admin_prefix[4]): # add
        await admin_cmds.add(message)
      elif message.content.startswith(admin_prefix[5]): # remove
        await admin_cmds.remove(message)
      elif message.content.startswith(admin_prefix[6]): # templates
        await admin_cmds.templates(message)
      elif message.content.startswith(admin_prefix[7]): # load
        await admin_cmds.load(message)
      elif message.content.startswith(admin_prefix[8]): # save
        await admin_cmds.save(message)
      elif message.content.startswith(admin_prefix[9]): # delete
        await admin_cmds.delete(message)
      else:
        await admin_cmds.invalid(message)
    except Exception as e:
      print("Exception:", e)
      await message.channel.send("Something went wrong :(((")
      await message.channel.send("here some nerd shit: " + str(e))
      
  # Server commands
  elif message.guild:
    # send a random message anywhere
    if message.content.startswith(server_prefix[0]): # help
      await server_cmds.help(message)
    elif message.content.startswith(server_prefix[1]): # hey
      await server_cmds.hey(message)
  
  # Random patron dm
  else:
    await message.channel.send("why we talk in secret?")
    await message.channel.send(server_cmds.random_message())
    
if __name__ == '__main__':
  main()