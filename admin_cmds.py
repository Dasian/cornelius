'''
Commands that are run by admins from the bot dms
Editing messages, publishing messages, misc
'''

import discord
import embedder


'''
    Editing Messages
'''
async def new(message):
    embedder.new()
    await message.channel.send("Current message:", embed=embedder.preview())

async def preview(message):
    await message.channel.send("Current message:", embed=embedder.preview())

async def add(message):
    if embedder.add(message.content):
        msg = embedder.preview()
        await message.channel.send(embed=msg)
    else:
        await message.channel.send("Usage: corn?add [attribute] [value]")
        await message.channel.send("Unable to add content. Make sure the property exists.")
        # TODO add list of attributes

async def remove(message):
    if embedder.remove(message.content):
        await message.channel.send("Current message:", embed=embedder.preview())
    else:
        await message.channel.send("Usage: corn?remove [attribute]")
        await message.channel.send("Unable to remove content. Make sure the property exists")
        # TODO add list of attributes

async def templates(message):
    temps = embedder.templates()
    for t in temps:
        n = t[0]
        n = n[11:n.find('.json')]
        name = "Name: " + n
        await message.channel.send(name, embed=t[1])
    if temps == []:
        await message.channel.send("There are no saved templates :((")

async def load(message):
    if embedder.load(message.content):
        await message.channel.send("Current message:", embed=embedder.preview())
    else:
        await message.channel.send("Usage: corn?load [template_name]")
        await message.channel.send("Use corn?templates to view saved templates")
        await message.channel.send("Couldn't load template. Is the name correct?")

async def save(message):
    if embedder.save(message.content):
        await message.channel.send("Saved message as template")
    else:
        await message.channel.send("Couldn't save message as template, contact ya boi")

async def delete(message):
    if embedder.delete(message.content):
        await message.channel.send("Successfully deleted template")
    else:
        await message.channel.send("Usage: corn?delete [template_name]")
        await message.channel.send("Use corn?templates to view saved templates")
        await message.channel.send("Couldn't delete template. Is the name correct?")

'''
    Publishing Messages
'''
# (helper) generate a list of accessible channels and associated servers
def get_channels(client):
    channels = []
    for server in client.guilds:       
        for channel in server.text_channels:
            channels.append((server, channel))

    return channels

# print list of accessible servers and channels
async def show_channels(message, client):
    channels = get_channels(client)
    await message.channel.send(embed = embedder.channels(channels))

# sets up publish paramaters
# returns tuple (confirmation, publish_channel)
# confirmation is True if conf is needed, False otherwise
# publish_channel is the channel to publish to
# publishing handled in on_message
async def publish(message, client):
    # verify usage
    words = message.content.split(' ')
    if len(words) < 2:
        await message.channel.send('usage: corn?publish [channel_id]')
        await show_channels(message, client)
        return (False, -1)
    try:
        id = int(words[1])
    except:
        await message.channel.send('invalid channel_id')
        await show_channels(message, client)
        return (False, -1) 
    accessible_channels = get_channels(client)
    if id >= len(accessible_channels) or id < 0:
        await message.channel.send('invalid channel_id')
        await show_channels(message, client)
        return (False, -1)

    # get publish information
    sname = accessible_channels[id][0].name
    s = "\nServer: " + sname
    publish_channel = accessible_channels[id][1]
    c = "\nChannel: " + publish_channel.name
    msg = s  + c

    # show what will be published where
    e = embedder.preview()
    await message.channel.send("Message to Publish:",embed = e)
    await message.channel.send(msg)
    
    # ask for confirmation (handled in on_message)
    await message.channel.send("Is this information correct? (yes/no)")
    return (True, publish_channel)

# post normal message 
# returns tuple (speak_confirmation, publish_channel, speak_msg)
async def speak(message, client):
    # verify usage
    words = message.content.split(' ')
    if len(words) < 3:
        await message.channel.send('usage: corn?speak [channel_id] [message]')
        await show_channels(message, client)
        return (False, -1, None)
    try:
        id = int(words[1])
    except:
        await message.channel.send('invalid channel_id')
        await show_channels(message, client)
        return (False, -1, None) 
    accessible_channels = get_channels(client)
    if id >= len(accessible_channels) or id < 0:
        await message.channel.send('invalid channel_id')
        await show_channels(message, client)
        return (False, -1, None)

    # get publish information
    sname = accessible_channels[id][0].name
    s = "\nServer: " + sname
    publish_channel = accessible_channels[id][1]
    c = "\nChannel: " + publish_channel.name
    msg_location = s  + c

    # get speak msg (every word after first 2)
    speak_msg = ''
    for w in words[2:]:
        speak_msg += w + ' '

    # show message to publish
    await message.channel.send("Message to Publish: " + speak_msg)
    await message.channel.send(msg_location)

    # confirmation (handled in onmessage)
    await message.channel.send("Is this information correct? (yes/no)")
    return (True, publish_channel, speak_msg)

'''
    Misc
'''
# prints help menu
# usage: corn?help [group]
async def help(message):

    words = message.content.split(' ')
    group = None
    if len(words) == 2:
        group = words[1].lower()

    await message.channel.send(embed=embedder.help(group))

async def invalid(message):
    img_url = 'https://media1.tenor.com/images/c111231424bfa61d015c9dc9a3a81f7f/tenor.gif?itemid=19268094'
    title_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'

    desc = '"' + message.content + '" isn\'t a command idiot lmao'
    e = discord.Embed(title='You sussy baka bitch.', description=desc, color=0xf30404, url=title_url)
    e.set_thumbnail(url = img_url)
    e.set_footer(text='type corn?help for help tho')
    await message.channel.send(embed=e)