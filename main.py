'''
  Runs the bot
  Calls functions (from bot class) based on the command
  Debug info for the log as well
'''

import os
from random import randint
import discord
import datetime
from dotenv import load_dotenv
from discord.ext import commands
# local files
import embedder
import admin_cmds
import server_cmds


# global vars
cmd_start = '!' # change this at will bro
server_prefix = ['help', 'hey', 'revive']
admin_prefix =['help', 'new', 'preview', 'publish', 'add', 'remove', 'templates', 'load', 'save', 'delete', 'channels', 'speak', 'roles', 'ping']
admins = []
publish_confirmation = False
speak_confirmation = False
ping_conf = False
speak_msg = ''
role_id = 0
ping_embed = None
publish_channel = None
# bot obj for bot commands (all intents enabled but could specify if you want)
# extended off of client
bot = commands.Bot(command_prefix=cmd_start, intents=discord.Intents.all())

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
  bot.run(TOKEN)


# Run when the bot is starting up
@bot.event
async def on_ready():
  print("Logged in as {0.user}".format(bot),' on ', datetime.datetime.now())

# Run whenever a message is received in any channel/dm (commands)
@bot.event
async def on_message(message):
  # ignore messages from the bot
  if message.author == bot.user:
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
    global publish_confirmation, publish_channel
    if publish_confirmation:
      if message.content.lower() == 'yes':
        await message.channel.send('poggies')
        await publish_channel.send(embed=embedder.preview())
      else:
        await message.channel.send('stop wasting my time bihtc')
      publish_confirmation = False
      return

    # speak confirmation
    global speak_confirmation, speak_msg
    if speak_confirmation:
      if message.content.lower() == 'yes':
        await message.channel.send('epic')
        await publish_channel.send(speak_msg)
      else:
        await message.channel.send('i will end you, whore')
      speak_confirmation = False
      return

    # ping confirmation
    global ping_conf, ping_embed, role_id
    if ping_conf:
      if message.content.lower() == 'yes':
        await message.channel.send('cum')
        await publish_channel.send('<@&'+str(role_id)+'>',embed=ping_embed)
      else:
        await message.channel.send('get some bitches')
      ping_conf = False
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
        publish_confirmation, publish_channel = await admin_cmds.publish(message, bot)
      elif message.content.startswith(admin_prefix[10]): # channels
        await admin_cmds.show_channels(message, bot)
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
      elif message.content.startswith(admin_prefix[11]): # speak
        speak_confirmation, publish_channel, speak_msg = await admin_cmds.speak(message, bot)
      elif message.content.startswith(admin_prefix[12]): # roles
        await admin_cmds.show_roles(message, bot)
      elif message.content.startswith(admin_prefix[13]): # ping
        ping_conf, publish_channel, role_id, ping_embed = await admin_cmds.ping(message, bot)
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
    # elif message.content.startswith(server_prefix[2]): # revive
    #  await server_cmds.revive(message, client)
  
  # Random patron dm
  else:
    await message.channel.send("why we talk in secret?")
    await message.channel.send(server_cmds.random_message())

  # allow for other commands from the @bot.command() decorator to run
  await bot.process_commands(message)

# chat revival command
# ping a role when the command is run in a server to revive a channel
# has a cooldown for all users
@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def revive(ctx):
  # find the necromancer role
  # TODO restrict this to the production server
  rid = None
  for server in bot.guilds:
    for role in server.roles:
      if role.name.lower() == 'necromancer':
        rid = role.id
        break

  if rid is None:
    await ctx.send("Oh fuck i messed up the code somewhere uhh oh fuck my bad")

  revival_msg = '<@&' + str(rid) + '>'
  await ctx.send(revival_msg)

@bot.event
async def on_command_error(ctx, error):
  degrading_msgs = ['Touch some grass', 'Get some bitches']
  if isinstance(error, commands.CommandOnCooldown):
    cooldown_msg = 'This cmd is on cooldwon for ' + str(int(error.retry_after)) + ' more seconds'
    r = randint(0, len(degrading_msgs))
    cooldown_msg += '\n' + degrading_msgs[r]
    await ctx.send(cooldown_msg)

if __name__ == '__main__':
  main()