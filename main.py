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

# secrets
load_dotenv()
TOKEN = os.environ['TOKEN']
PERMS = os.environ['PERMS']
NUM_ADMINS = int(os.environ['NUM_ADMINS'])
admins = []
for i in range(0, NUM_ADMINS):
  s = "ADMIN" + str(i)
  admins.append(int(os.environ[s]))

# command list
cmd_start = '!' # CHANGE THIS BEFORE MERGING WITH MAIN
server_cmds = ['help', 'hey']
admin_cmds =['help', 'new', 'preview', 'publish', 'add', 'remove', 'templates', 'load', 'save', 'delete', 'channels']
for i in range(len(server_cmds)):
  server_cmds[i] = cmd_start + server_cmds[i]
for i in range(len(admin_cmds)):
  admin_cmds[i] = cmd_start + admin_cmds[i]
accessible_channels = []

# Connect to client (all intents enabled but could specify if you care)
client = discord.Client(intents=discord.Intents.all())

# used to confirm a message publication
confirmation = False
publish_channel = None

# Run when the bot is starting up (startup)
@client.event
async def on_ready():
  print("Logged in as {0.user}".format(client),' on ', datetime.datetime.now())
  # generate channels for publishing; can be updated by calling corn?channels
  for server in client.guilds:
    for channel in server.text_channels:
      accessible_channels.append((server, channel))

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
  # Embed creation commands
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

    try:
      if message.content.startswith(admin_cmds[0]): # help
        help = embedder.help()
        await message.channel.send(embed = help)
      elif message.content.startswith(admin_cmds[1]): # new
        embedder.new()
        await message.channel.send("Current message:", embed=embedder.preview())
      elif message.content.startswith(admin_cmds[2]): # preview
        await message.channel.send("Current message:", embed=embedder.preview())
      elif message.content.startswith(admin_cmds[3]): # publish

        # get channel information
        words = message.content.split(' ')
        id = int(words[1])
        if id >= len(accessible_channels) or id < 0:
          await message.channel.send('invalid channel')
          # show accessible channels here?
          return
        sname = accessible_channels[id][0].name
        s = "\nServer: " + sname

        publish_channel = accessible_channels[id][1]
        c = "\nChannel: " + publish_channel.name
        msg = "Publishing to: " + s  + c

        # show what will be published where
        e = embedder.preview()
        await message.channel.send("Message to Publish:",embed = e)
        await message.channel.send(msg)
        
        # confirmation
        confirmation = True
        await message.channel.send("Is this information correct? (yes/no)")

      elif message.content.startswith(admin_cmds[10]): # channels
        # generate a list of accessible channels and associated servers
        accessible_channels.clear()
        for server in client.guilds:       
          for channel in server.text_channels:
            accessible_channels.append((server, channel))
        # print list of accessible servers and channels
        await message.channel.send(embed = embedder.channels(accessible_channels))
      elif message.content.startswith(admin_cmds[4]): # add
        if embedder.add(message.content):
          msg = embedder.preview()
          await message.channel.send(embed=msg)
        else:
          await message.channel.send("Unable to add content. Make sure the property exists")
      elif message.content.startswith(admin_cmds[5]): # remove
        if embedder.remove(message.content):
          await message.channel.send("Current message:", embed=embedder.preview())
        else:
          await message.channel.send("Unable to remove content. Make sure the property exists")
      elif message.content.startswith(admin_cmds[6]): # templates
        temps = embedder.templates()
        for t in temps:
          n = t[0]
          n = n[11:n.find('.json')]
          name = "Name: " + n
          await message.channel.send(name, embed=t[1])
        if temps == []:
          await message.channel.send("There are no saved templates :((")
      elif message.content.startswith(admin_cmds[7]): # load
        if embedder.load(message.content):
          await message.channel.send("Current message:", embed=embedder.preview())
        else:
          await message.channel.send("Couldn't load template. Is the name correct?")
      elif message.content.startswith(admin_cmds[8]): # save
        if embedder.save(message.content):
          await message.channel.send("Saved message as template")
        else:
          await message.channel.send("Couldn't save message as template, contact ya boi")
      elif message.content.startswith(admin_cmds[9]): # delete
          if embedder.delete(message.content):
            await message.channel.send("Successfully deleted template")
          else:
            await message.channel.send("Couldn't delete template. Is the name correct?")
      else:
        img_url = 'https://gifimage.net/wp-content/uploads/2017/07/angry-anime-gif-18.gif'
        title_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'

        desc = '"' + message.content + '" isn\'t a command idiot lmao'
        e = discord.Embed(title='You sussy baka bitch.', description=desc, color=0xf30404, url=title_url)
        e.set_thumbnail(url = img_url)
        e.set_footer(text='type corn?help for help tho')
        await message.channel.send(embed=e)
    except Exception as e:
      print("Exception:", e)
      await message.channel.send("Something went wrong :((( plz create/load a new message")
      
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
    await message.channel.send("I'm a bot, not Valentina")
    await message.channel.send(server_bot.random_message())
    
# Run client
client.run(TOKEN)
