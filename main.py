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
import requests

# local files
import embedder
import admin_cmds
import server_cmds

# custom voice
import aiohttp
import tempfile
import subprocess
import asyncio
from io import BytesIO
import json
import time
import re

# global vars
cmd_start = 'corn?' # change this at will bro
server_prefix = ['help', 'hey']
admin_prefix =['help', 'new', 'preview', 'publish', 'add', 'remove', 'templates', 'load', 'save', 'delete', 'channels', 'speak', 'roles', 'ping']
admins = []
publish_confirmation = False
speak_confirmation = False
ping_conf = False
speak_msg = ''
role_id = 0
ping_embed = None
publish_channel = None
voice_client = None
# bot obj for bot commands (all intents enabled but could specify if you want)
# extended off of client
bot = commands.Bot(command_prefix=cmd_start, intents=discord.Intents.all())

# guess what this function is
def main():
  # retrieve secrets
  global admins
  global API_KEY, API_ROOT, API_SECRET
  load_dotenv()
  TOKEN = os.environ['TOKEN']
  PERMS = os.environ['PERMS']
  API_ROOT = 'https://api.uberduck.ai'
  API_KEY = os.environ['UBERDUCK_API_KEY']
  API_SECRET = os.environ['UBERDUCK_API_SECRET']
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
  # load cmds from other files
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

@revive.error
async def revive_error(ctx, error):
  degrading_msgs = ['Touch some grass', 'Get some bitches']
  if isinstance(error, commands.CommandOnCooldown):
    cooldown_msg = 'This cmd is on cooldown for ' + str(int(error.retry_after)) + ' more seconds'
    r = randint(0, len(degrading_msgs)-1)
    cooldown_msg += '\n' + degrading_msgs[r]
    await ctx.send(cooldown_msg)

# send a custom tts (text to speech) message with a custom voice
@bot.command()
async def imitate(ctx, voice, *, message):
  global voice_client
  voice_client = ctx.author.voice
  if voice_client:
    voice_client = await voice_client.channel.connect()
    
    # uberduck copied code
    # await ctx.response.defer(ephemeral=True, with_message=True)
    audio_data = await query_uberduck(message, voice)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_f, tempfile.NamedTemporaryFile(suffix=".opus") as opus_f:
      wav_f.write(audio_data.getvalue())
      wav_f.flush()
      subprocess.check_call(["ffmpeg", "-y", "-i", wav_f.name, opus_f.name])
      source = discord.FFmpegOpusAudio(opus_f.name) # ffmpeg executable needs to be in path env variable to work
      voice_client.play(source, after=None)
      while voice_client.is_playing():
        await asyncio.sleep(0.5)
        
    await voice_client.disconnect()
  else:
    await ctx.send("You need to be connected to a voice channel")
  return

async def query_uberduck(text, voice="zwf"):
  # copied from uberduck blog
  max_time = 90
  async with aiohttp.ClientSession() as session:
    url = f"{API_ROOT}/speak"
    data = json.dumps(
      {
        "speech": text,
        "voice": voice,
      }
    )

    start = time.time()
    async with session.post(
      url,
      data=data,
      auth=aiohttp.BasicAuth(API_KEY, API_SECRET),
    ) as r:
      if r.status != 200:
        raise Exception("Error synthesizing speech", await r.json())
      uuid = (await r.json())["uuid"]
    while True:
      if time.time() - start > max_time:
        raise Exception("Request timed out!")
      await asyncio.sleep(1)
      status_url = f"{API_ROOT}/speak-status"
      async with session.get(status_url, params={"uuid": uuid}) as r:
        if r.status != 200:
          continue
        response = await r.json()
        if response["path"]:
          async with session.get(response["path"]) as r:
            return BytesIO(await r.read())

@imitate.error
async def imitate_error(ctx, error):
  await ctx.send(error)
  await ctx.send('Usage: corn?imitate [voice] [message]')
  if type(voice_client) == discord.voice_client.VoiceClient:
    await voice_client.disconnect()

@bot.command()
async def voice_search(ctx, *, query):

  # get list of voices
  url = "https://api.uberduck.ai/voices?mode=tts-basic&language=english"
  headers = {"accept": "application/json"}
  response = requests.get(url, headers=headers).json()
  voices = []
  for r in response:
    voices.append(r['name'])

  # search list
  query = query.split(' ')
  expr = '.*'
  for q in query:
    expr += q + '|'
  r = re.compile(expr[0:-1])
  voices = list(filter(r.match, voices))
  if len(voices) == 0:
    await ctx.send("No matching voices")
  else:
    await ctx.send(embed=embedder.voice_search_embed(voices))

  return

@voice_search.error
async def voice_search_error(ctx, error):
  await ctx.send(error)
  await ctx.send('Usage: corn?voice_search [search query]')

@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, discord.ext.commands.CommandNotFound):
    await ctx.send('Invalid Command')

if __name__ == '__main__':
  main()