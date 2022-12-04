'''
  Functionality for server commands
'''
import time
import random
import discord
from discord.ext import commands
from random import randint
import embedder
import aiohttp
import tempfile
import subprocess
import asyncio
from io import BytesIO
import json
import time
import re
import requests
import os

# cursed "functionality"
# from discord import app_commands

class Server_Cmds(commands.Cog, name="Server Commands"):
  
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

  def __init__(self):
     
    global API_KEY, API_ROOT, API_SECRET
    API_ROOT = 'https://api.uberduck.ai'
    API_KEY = os.environ['UBERDUCK_API_KEY']
    API_SECRET = os.environ['UBERDUCK_API_SECRET']
    global voice_client
    voice_client = None
    random.seed(int(time.time()))

  @commands.command(description="Prints server help menu")
  async def server_help(self, message):
    """Displays help msg for server cmds"""
    help = '''
  corn?server_help - Displays server help msg
  corn?hey - Get a random val quote
  corn?revive - Ping everyone with a necromancer role to revive this channel
  corn?imitate [voice] [message] - Send a tts message into a vc
  corn?voice_search [query] - Search for a tts voice
    '''
    await message.channel.send(help)
    return

  @commands.command(aliases=['quote', 'quotes', 'hello'], description="Sends a random Valentina quote")
  async def hey(self, ctx):
    """Sends a random val quote"""
    await ctx.send(self.messages[random.randint(0, len(self.messages)-1)])
    return

  @commands.command(description="Pings users with a necromancer role to revive a dead chat. Has a global cooldown")
  @commands.cooldown(1, 10, commands.BucketType.user)
  async def revive(self, ctx):
    """
    Pings the necromancer role to revive a channel
    Has global cooldown for all users
    """
    # TODO restrict this to the production server
    rid = None
    for role in ctx.guild.roles:
      if role.name.lower() == 'necromancer':
        rid = role.id
        break

    if rid is None:
      await ctx.send("Oh fuck i messed up the code somewhere uhh oh fuck my bad")
      await ctx.send("Is there a necromancer role in this server?")

    revival_msg = '<@&' + str(rid) + '>'
    await ctx.send(revival_msg)
  @revive.error
  async def revive_error(self, ctx, error):
    degrading_msgs = ['Touch some grass', 'Get some bitches']
    if isinstance(error, commands.CommandOnCooldown):
      r = randint(0, len(degrading_msgs))
      cooldown_msg = degrading_msgs[r]
      await ctx.send(cooldown_msg)

  @commands.command(description="Sends a text to speech message in a voice channel with a selected voice")
  async def imitate(self, ctx, voice, *, message):
    """Sends a tts message with chosen voice in vc"""
    global voice_client
    voice_client = ctx.author.voice
    if voice_client:
      voice_client = await voice_client.channel.connect()
      
      # uberduck copied code
      # await ctx.response.defer(ephemeral=True, with_message=True)
      audio_data = await self.query_uberduck(message, voice)
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
  @imitate.error
  async def imitate_error(self, ctx, error):
    await ctx.send('Usage: corn?imitate [voice] [message]')
    if type(voice_client) == discord.voice_client.VoiceClient:
      await voice_client.disconnect()

  async def query_uberduck(self, text, voice="zwf"):
    """
    Query uberduck for tts voice file (helper)
    copied from uberduck blog
    """
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

  #@app_commands.command(name="voice_search", description="Search voices usable by the imitate cmd")
  @commands.command(aliases=['voices_search', 'search_voice', 'search_voices'], description="Searches available voices to be used with the imitate command")
  async def voice_search(self, ctx, *, query:str):
    """Search voices usable by imitate"""
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
  @voice_search.error
  async def voice_search_error(self, ctx, error):
    await ctx.send('Usage: corn?voice_search [search query]')

async def setup(bot):
  """Adds commands to bot"""
  await bot.add_cog(Server_Cmds(bot))