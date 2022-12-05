'''
  Runs the bot
  Loads and syncs cmds from other files
  Contains general bot functions
'''

import os
import discord 
import datetime
from discord.ext import commands
from dotenv import load_dotenv

class Cornelius(commands.Bot):
  """Bot wrapper; allows for hybrid commands"""
  def __init__(self):
    super().__init__(command_prefix='!', intents=discord.Intents.all())
    self.gid = 954166428674707526 # test server

  async def on_ready(self):
    """Runs when bot is starting"""
    # load cmds from other files
    await self.load_extension('server_cmds')
    await self.load_extension('admin_cmds')
    print("Logged in as {0.user}".format(bot),' on ', datetime.datetime.now())

  async def on_command_error(self, ctx, error):
    """When any cmd raises an error"""
    if isinstance(error, discord.ext.commands.CommandNotFound) or isinstance(error, discord.ext.commands.CheckFailure):
      img_url = 'https://media1.tenor.com/images/c111231424bfa61d015c9dc9a3a81f7f/tenor.gif?itemid=19268094'
      title_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'

      desc = '"' + ctx.message.content + '" isn\'t a command idiot lmao'
      e = discord.Embed(title='You sussy baka bitch.', description=desc, color=0xf30404, url=title_url)
      e.set_thumbnail(url = img_url)
      e.set_footer(text='type corn?help for help tho')
      await ctx.reply(embed=e, ephemeral=True)
    else:
      await ctx.reply(error, ephemeral=True)


def main():
  """Guess what this function is"""
  load_dotenv()
  TOKEN = os.environ['TOKEN']

  global bot
  bot = Cornelius()
  bot.run(TOKEN)

if __name__ == '__main__':
  main()