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
import json
import embedder

class Cornelius(commands.Bot):
  """Bot wrapper; allows for hybrid commands"""
  def __init__(self):
    super().__init__(command_prefix='corn?', intents=discord.Intents.all())

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
  
  async def on_member_update(self, before, after):
    """When a server member's role is updated; Used for server boosting msg"""
    # publishing info
    boost_rid = 868591762812305448  # server booster role id used to determine if a user boosted the server
    boost_channel = 1109592692113022996
    gid = 862949747396837386

    # member has just boosted the server
    before_roles = [r.id for r in before.roles]
    after_roles = [r.id for r in after.roles]
    if boost_rid not in before_roles and boost_rid in after_roles:
      channel = bot.get_channel(boost_channel)
      guild = bot.get_guild(gid)

      # num boosts to next server level
      num_boosts = guild.premium_subscription_count
      next_lvl = -1
      if num_boosts < 2:
        next_lvl = 2 - num_boosts
      elif num_boosts < 7:
        next_lvl = 7 - num_boosts
      elif num_boosts < 14:
        next_lvl = 14 - num_boosts

      # fillable boost attributes
      max_boosts = next_lvl <= 0
      uname = after.id
      boost_attr = {'num_boosts': num_boosts, 'next_lvl': next_lvl, 'uname': uname}

      # thank @user
      f = open('bot_embeds/boost-msg.txt')
      msg = f.read()
      f.close()
      boost_msg = embedder.fill_fields(msg, boost_attr)

      # load boost template
      fname = ''
      if max_boosts:
        fname = 'bot_embeds/max-boost.json'
      else:
        fname = 'bot_embeds/boost-embed.json'
      f = open(fname, 'r')
      e = json.load(f)
      f.close()

      # fill out custom boost vars (next_lvl num_boosts, uname)
      e = embedder.fill_fields(discord.Embed.from_dict(e), boost_attr)

      # send boost msgs
      await channel.send(boost_msg, embed=e)

def main():
  """Guess what this function is"""
  load_dotenv()
  TOKEN = os.environ['TOKEN']

  global bot
  bot = Cornelius()
  bot.remove_command('help')
  bot.run(TOKEN)

if __name__ == '__main__':
  main()
