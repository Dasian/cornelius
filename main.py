'''
  Runs the bot
  Calls functions (from bot class) based on the command
  Debug info for the log as well
'''

import os
import discord 
import datetime
from discord.ext import commands
from dotenv import load_dotenv

cmd_start = '!'
bot = commands.Bot(command_prefix=cmd_start, intents=discord.Intents.all())

# guess what this function is
def main():
  # retrieve secrets
  load_dotenv()
  TOKEN = os.environ['TOKEN']
  PERMS = os.environ['PERMS']

  # Run client
  bot.run(TOKEN)

@bot.event
async def on_ready():
  """Runs when bot is starting"""
  # load cmds from other files
  await bot.load_extension('server_cmds')
  await bot.load_extension('admin_cmds')
  print("Logged in as {0.user}".format(bot),' on ', datetime.datetime.now())

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