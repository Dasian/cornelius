'''
  Functionality for server commands
'''
import time
import random
from main import bot
from discord.ext import commands
from random import randint

# Preset Messages
messages = ["Hellooo", "^-^", 'these nuts',
    "Your alpha hears you.",
    "I had a pintful of nut.",
    "Maaaaan.",
    "However comma.",
    "Does anyone know what 9 inches looks like?",
    "I am feeling the effects of estrogen!",
    "Let's interlock toes.",
    "I hate toes.",
    "Give me those, you've lost ball privileges.",
    "I'm gonna play jacks with them. I'll go bowling with these.",
    "I put the 'bad' in 'badussy'.",
    "It's not satanic, it's just a hospital.",
    "I look like a man baby with huge t*ts.",
    "I'm not emotionally stable enough for this moment.",
    "2 inches is huge, don't you think 2 inches is huge?",
    "I lost my balls.",
    "Oh my God I f*cking spilled my balls all over the place.",
    "One time I shat on my teacher's lap.",
    "Hey traveler, you want some p*nis enlargement pills?",
    "These lines are as straight as me.",
    "I'm doing glad.",
    "Su español es muy bueno. Ah, arigato!",
    "If you call me Elsa, I'm gonna make out with your mom, then kiss you in order to make you kiss your mom.",
    "I'm gonna pop my hamburger cherry with some McDonalds. It's my first American meat in my mouth.",
    "What's an internet footprint?"
]

# Initialization
random.seed(int(time.time()))

# sends a help message for server commands
async def help(message):
  help = '''
corn?help - Displays this message
corn?hey - Get a random val quote
corn?revive - Ping everyone with a necromancer role to revive this channel
corn?imitate [voice] [message] - Send a tts message into a vc
corn?voice_search [query] - Search for a tts voice
  '''
  await message.channel.send(help)
  return

# (helper) returns a random message from a list
def random_message():
  return messages[random.randint(0, len(messages))]

# sends a random val quote
async def hey(message):
  await message.channel.send(random_message())
  return


'''decorated cmds'''

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
    r = randint(0, len(degrading_msgs))
    cooldown_msg += '\n' + degrading_msgs[r]
    await ctx.send(cooldown_msg)


def setup(bot):
  '''Adds functions to be used in multiple files'''
  bot.add_command(revive)