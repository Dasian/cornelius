'''
  Runs the bot
  Calls functions (from bot class) based on the command
  Debug info for the log as well
'''

import os
import discord 
import datetime
from dotenv import load_dotenv
from discord.ext import commands

# local files
import embedder
import admin_cmds

# global vars
cmd_start = '!' # change this at will bro
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
  NUM_ADMINS = int(os.environ['NUM_ADMINS'])
  for i in range(0, NUM_ADMINS):
    s = "ADMIN" + str(i)
    admins.append(int(os.environ[s]))

  # Run client
  bot.run(TOKEN)

@bot.event
async def on_ready():
  """Runs when bot is starting"""
  # load cmds from other files
  await bot.load_extension('server_cmds')
  await bot.load_extension('admin_cmds')
  print("Logged in as {0.user}".format(bot),' on ', datetime.datetime.now())

@bot.command()
async def reload(ctx):
  """For development, updates all cmds"""
  await bot.reload_extension('admin_cmds')
  await bot.reload_extension('server_cmds')
  await ctx.send('Reload complete')

@bot.event
async def on_message(message):
  """Debug for now ig"""
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

  # allow for other commands from the @bot.command() decorator to run
  await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, discord.ext.commands.CommandNotFound):
    img_url = 'https://media1.tenor.com/images/c111231424bfa61d015c9dc9a3a81f7f/tenor.gif?itemid=19268094'
    title_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'

    desc = '"' + ctx.message.content + '" isn\'t a command idiot lmao'
    e = discord.Embed(title='You sussy baka bitch.', description=desc, color=0xf30404, url=title_url)
    e.set_thumbnail(url = img_url)
    e.set_footer(text='type corn?help for help tho')
    await ctx.send(embed=e)
  else:
    await ctx.send(error)

if __name__ == '__main__':
  main()