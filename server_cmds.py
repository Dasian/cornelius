'''
  Functionality for server commands
'''
import discord
import time
import random

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

# pings everyone with the necromancer role to bring a channel back from the dead
cooldown = False
async def revive(message, client):
  global cooldown
  print('cooldown value: ', cooldown)
  
  # degrade
  if cooldown:
    await message.channel.send("On cooldown don't bug me")
    await message.channel.send("Try again in x time")
    return
  
  # begin cooldown for x time
  cooldown = True
  print('cooldown starting')

  # find the necromancer role
  # TODO restrict this to the production server
  rid = None
  for server in client.guilds:
    for role in server.roles:
      if role.name.lower() == 'necromancer':
        rid = role.id
        break

  if rid is None:
    await message.channel.send("Oh fuck i messed up uhh oh fuck my bad")

  revival_msg = '<@&' + str(rid) + '>'
  await message.channel.send(revival_msg)

  # set cooldown for x time
  time.sleep(10)
  print('cooldown ending')
  cooldown = False

  return