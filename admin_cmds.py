'''
Commands that are run by admins from the bot dms
Editing messages, publishing messages, misc
'''

import discord
from discord.ext import commands
import embedder
from main import bot

'''
    Editing Messages
'''
@commands.command()
async def new(ctx):
    """Create a new embedded msg"""
    embedder.new()
    await ctx.send("Current message:", embed=embedder.preview())

@commands.command()
async def preview(ctx):
    """View current embedded msg"""
    await ctx.send("Current message:", embed=embedder.preview())

@commands.command()
async def add(ctx, attr, *, value):
    """Adds an embed attr to the current embedded msg"""
    if embedder.add(attr, value):
        msg = embedder.preview()
        await ctx.send(embed=msg)
    else:
        await ctx.send("Unable to add content. Make sure the property exists.")
        # TODO show list of attributes
@add.error
async def add_error(ctx, error):
    await ctx.send("Usage: corn?add [attribute] [value]")

@commands.command()
async def remove(ctx, attr):
    """Removes attr from embedded msg"""
    if embedder.remove(attr):
        await ctx.send("Current message:", embed=embedder.preview())
    else:
        await ctx.send("Unable to remove content. Make sure the property exists")
        # TODO show list of attributes
@remove.error
async def remove_error(ctx, error):
    await ctx.send("Usage: corn?remove [attribute]")

@commands.command()
async def templates(ctx, message):
    "Preview all saved templates"
    temps = embedder.templates()
    for t in temps:
        n = t[0]
        n = n[11:n.find('.json')]
        name = "Name: " + n
        await ctx.send(name, embed=t[1])
    if temps == []:
        await ctx.send("There are no saved templates :((")

@commands.command()
async def load(ctx, *, fname):
    """Loads emedded msg from a template"""
    if embedder.load(fname):
        await ctx.send("Current message:", embed=embedder.preview())
    else:
        await ctx.send("Couldn't load template. Is the name correct?")
        # TODO show template names
@load.error
async def load_error(ctx, error):
    await ctx.send("Usage: corn?load [template_name]")
    await ctx.send("Use corn?templates to view saved templates")

@commands.command()
async def save(ctx, *, fname):
    """
    Save embedded msg as a template
    Overwrites existing names
    """
    if embedder.save(fname):
        await ctx.send("Saved message as template")
    else:
        await ctx.send("Couldn't save message as template, try again or contact ya boi")
@save.error
async def save_error(ctx, error):
    await ctx.send("Usage: corn?save [template_name]")

@commands.command()
async def delete(ctx, *, fname):
    """Deletes saved template"""
    if embedder.delete(fname):
        await ctx.send("Successfully deleted template")
    else:
        await ctx.send("Couldn't delete template. Is the name correct?")
@delete.error
async def delete_error(ctx, error):
    await ctx.send("Usage: corn?delete [template_name]")
    await ctx.send("Use corn?templates to view saved templates")

'''
    Publishing Messages
    TODO replace channel selection with ui stuff
'''
def get_channels():
    """Get a list of accessible servers and channels (helper)"""
    channels = []
    for server in bot.guilds:       
        for channel in server.text_channels:
            channels.append((server, channel))
    return channels

@commands.command()
async def show_channels(ctx):
    """List accessible servers and channels"""
    channels = get_channels()
    await ctx.send(embed = embedder.channels(channels))

# sets up publish paramaters
# returns tuple (confirmation, publish_channel)
# confirmation is True if conf is needed, False otherwise
# publish_channel is the channel to publish to
# publishing handled in on_message
async def publish(message, client):
    # verify usage
    words = message.content.split(' ')
    if len(words) < 2:
        await ctx.send('usage: corn?publish [channel_id]')
        await show_channels(message, client)
        return (False, -1)
    try:
        id = int(words[1])
    except:
        await ctx.send('invalid channel_id')
        await show_channels(message, client)
        return (False, -1) 
    accessible_channels = get_channels(client)
    if id >= len(accessible_channels) or id < 0:
        await ctx.send('invalid channel_id')
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
    await ctx.send("Message to Publish:",embed = e)
    await ctx.send(msg)
    
    # ask for confirmation (handled in on_message)
    await ctx.send("Is this information correct? (yes/no)")
    return (True, publish_channel)

# post normal message 
# returns tuple (speak_confirmation, publish_channel, speak_msg)
async def speak(message, client):
    # verify usage
    words = message.content.split(' ')
    if len(words) < 3:
        await ctx.send('usage: corn?speak [channel_id] [message]')
        await show_channels(message, client)
        return (False, -1, None)
    try:
        id = int(words[1])
    except:
        await ctx.send('invalid channel_id')
        await show_channels(message, client)
        return (False, -1, None) 
    accessible_channels = get_channels(client)
    if id >= len(accessible_channels) or id < 0:
        await ctx.send('invalid channel_id')
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
    await ctx.send("Message to Publish: " + speak_msg)
    await ctx.send(msg_location)

    # confirmation (handled in onmessage)
    await ctx.send("Is this information correct? (yes/no)")
    return (True, publish_channel, speak_msg)

# (helper) returns a list of tuples (server, role obj)
# global mapping of rolenames to ids?
def get_roles(client):
    print('get_roles()')
    roles = []
    for server in client.guilds:       
        for role in server.roles:
            roles.append((server, role))
    return roles

# prints a list of pingable roles
async def show_roles(message, client):
    print('show_roles()')
    roles = get_roles(client)
    await ctx.send(embed=embedder.role_list(roles))
    return

# usage: corn?ping [role] [channel_id] [msg?]
# posts an embedded msg in a channel while pinging a role
# returns a tuple (ping_conf, publish_id, ping_msg)
async def ping(message, client):
    
    # verification/parse
    words = message.content.split(' ')
    if len(words) < 4:
        await ctx.send('usage: corn?ping [role] [channel_id] [message]')
        await show_channels(message, client)
        return (False, -1, None)

    # publish channel
    try:
        id = int(words[2])
    except:
        await ctx.send('invalid channel_id')
        await show_channels(message, client)
        return (False, -1, -1, None) 
    accessible_channels = get_channels(client)
    if id >= len(accessible_channels) or id < 0:
        await ctx.send('invalid channel_id')
        await show_channels(message, client)
        return (False, -1, -1, None)
    
    # create a list of roles for a given server
    sname = accessible_channels[id][0].name
    roles = get_roles(client)
    # list of tuples with the correct server name
    roles = filter(lambda r: r[0].name == sname, roles)
    # remove server name from tuples
    roles = [r[1] for r in roles]
    rname = words[1]
    target_role = None

    # get target role info
    for role in roles:
        if role.name.lower() == rname.lower():
            target_role = role
            break
    if target_role is None:
        await ctx.send('invalid role name for server "' + sname +'"')
        await show_roles(message, client)
        return (False, -1, -1, None)
    
    # ping msg 
    rid = target_role.id
    ping_msg = ''
    for w in words[3:]:
        ping_msg += w + ' '
    
    # get publish information
    sname = accessible_channels[id][0].name
    s = "\nServer: " + sname
    publish_channel = accessible_channels[id][1]
    c = "\nChannel: " + publish_channel.name
    msg_location = s  + c
    
    # create embed
    color_map = {'twitter': 0x00acee, 'patreon': 0xff424D, 'youtube': 0xff0000, 'tiktok': 0xff0050}
    if role.name.lower() in color_map.keys():
        color = color_map[role.name.lower()]
    else:
        color = 0x36393F
    ping_embed = discord.Embed(color=color, description=ping_msg)

    # show publish info
    await ctx.send("Preview:")

    await ctx.send('@' + target_role.name + '', embed=ping_embed)
    await ctx.send(msg_location)

    # confirmation (handled in onmessage)
    await ctx.send("Is this information correct? (yes/no)")
    return (True, publish_channel, rid, ping_embed)

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

    await ctx.send(embed=embedder.help(group))

async def invalid(message):
    img_url = 'https://media1.tenor.com/images/c111231424bfa61d015c9dc9a3a81f7f/tenor.gif?itemid=19268094'
    title_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'

    desc = '"' + message.content + '" isn\'t a command idiot lmao'
    e = discord.Embed(title='You sussy baka bitch.', description=desc, color=0xf30404, url=title_url)
    e.set_thumbnail(url = img_url)
    e.set_footer(text='type corn?help for help tho')
    await ctx.send(embed=e)



async def setup(bot):
    bot.add_command(help)
    bot.add_command(new)
    bot.add_command(preview)
    # bot.add_command(publish)
    bot.add_command(channels)
    bot.add_command(add)
    bot.add_command(remove)
    bot.add_command(templates)
    bot.add_command(load)
    bot.add_command(save)
    bot.add_command(delete)
    # bot.add_command(speak)
    bot.add_command(roles)
    # bot.add_command(ping)