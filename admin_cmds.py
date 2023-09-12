'''
Commands that are run by admins from the bot dms
Editing messages, publishing messages, misc
'''

import discord
from discord.ext import commands
import embedder
import asyncio
from dotenv import load_dotenv
import os
import random
import json
import copy

class Admin_Cmds(commands.Cog, name='Admin Commands'):

    def __init__(self, bot):
        self.bot = bot
        self.admins = []
        load_dotenv()
        NUM_ADMINS = int(os.environ['NUM_ADMINS'])
        for i in range(0, NUM_ADMINS):
            s = "ADMIN" + str(i)
            self.admins.append(int(os.environ[s]))

    async def cog_check(self, ctx):
        """Check if admin conditions are met before running cmd (admin and pm)"""
        return ctx.author.id in self.admins and not ctx.guild

    '''
        Editing Messages
    '''
    @commands.hybrid_command(with_app_command=True,description="Create a new embedded msg")
    async def new(self, ctx):
        """Create a new embedded msg"""
        embedder.new()
        await ctx.reply("Current message:", embed=embedder.preview())

    @commands.hybrid_command(with_app_command=True,description="View current embedded msg")
    async def preview(self, ctx):
        """View current embedded msg"""
        await ctx.send("Current message:", embed=embedder.preview())
    @preview.error
    async def preview_error(self, ctx, error):
        await ctx.send('No msg to preview, create a new msg or load from a template')

    @commands.hybrid_command(with_app_command=True,description="Adds/Updates attribute to the current embedded msg",aliases=['update'])
    async def add(self, ctx, attr, *, value):
        """Adds an embed attr to the current embedded msg"""
        if embedder.add(attr, value):
            msg = embedder.preview()
            await ctx.send(embed=msg)
        else:
            await ctx.send("Unable to add content. Make sure the property exists.")
            # TODO show list of attributes
    @add.error
    async def add_error(self, ctx, error):
        await ctx.send("Usage: corn?add [attribute] [value]")

    @commands.hybrid_command(with_app_command=True,description="Removes attribute from loaded embedded msg")
    async def remove(self, ctx, attr):
        """Removes attr from embedded msg"""
        if embedder.remove(attr):
            await ctx.send("Current message:", embed=embedder.preview())
        else:
            await ctx.send("Unable to remove content. Make sure the property exists")
            # TODO show list of attributes
    @remove.error
    async def remove_error(self, ctx, error):
        await ctx.send("Usage: corn?remove [attribute]")

    @commands.hybrid_command(with_app_command=True,description="Sends all embed templates with their names")
    async def templates(self, ctx):
        "Preview all saved templates"
        temps = embedder.templates()
        for t in temps:
            n = t[0]
            n = n[11:n.find('.json')]
            name = "Name: " + n
            await ctx.send(name, embed=t[1])
        if temps == []:
            await ctx.send("There are no saved templates :((")

    @commands.hybrid_command(with_app_command=True,description="Sets a saved embedded msg as the current msg")
    async def load(self, ctx, *, fname):
        """Loads emedded msg from a template"""
        if embedder.load(fname):
            await ctx.send("Current message:", embed=embedder.preview())
        else:
            await ctx.send("Couldn't load template. Is the name correct?")
            # TODO show template names
    @load.error
    async def load_error(self, ctx, error):
        await ctx.send("Usage: corn?load [template_name]")
        await ctx.send("Use corn?templates to view saved templates")

    @commands.hybrid_command(with_app_command=True,description="Saves current msg as an embed template")
    async def save(self, ctx, *, fname):
        """
        Save embedded msg as a template
        Overwrites existing names
        """
        if embedder.save(fname):
            await ctx.send("Saved message as template")
        else:
            await ctx.send("Couldn't save message as template, try again or contact ya boi")
    @save.error
    async def save_error(self, ctx, error):
        await ctx.send("Usage: corn?save [template_name]")

    @commands.hybrid_command(with_app_command=True,description="Deletes a saved template")
    async def delete(self, ctx, *, fname):
        """Deletes saved template"""
        if embedder.delete(fname):
            await ctx.send("Successfully deleted template")
        else:
            await ctx.send("Couldn't delete template. Is the name correct?")
    @delete.error
    async def delete_error(self, ctx, error):
        await ctx.send("Usage: corn?delete [template_name]")
        await ctx.send("Use corn?templates to view saved templates")

    '''
        Publishing Messages
        TODO replace channel selection with ui stuff
    '''
    def get_channels(self):
        """Get a list of accessible servers and channels (helper)"""
        channels = []
        for server in self.bot.guilds:      
            for channel in server.text_channels:
                channels.append((server, channel))
        return channels

    @commands.hybrid_command(with_app_command=True,name='channels', aliases=['show_channels', 'get_channels'], description="Get a list of all channels you can post to")
    async def show_channels(self, ctx):
        """List accessible servers and channels"""
        channels = self.get_channels()
        await ctx.send(embed = embedder.channels(channels))

    @commands.hybrid_command(with_app_command=True,description="Post current embedded msg to a channel")
    async def publish(self, ctx, cid:int):
        """Publishes embedded msg to target channel"""
        # verify usage
        accessible_channels = self.get_channels()
        if cid >= len(accessible_channels) or cid < 0:
            await ctx.send('Invalid channel_id')
            return

        # get publish information
        sname = accessible_channels[cid][0].name
        s = "\nServer: " + sname
        publish_channel = accessible_channels[cid][1]
        c = "\nChannel: " + publish_channel.name
        msg = s  + c

        # show what will be published where
        e = embedder.preview()
        await ctx.send("Message to Publish:",embed = e)
        await ctx.send(msg)
        
        # confirmation
        await ctx.send("Is this information correct? (yes/no)")
        try:
            conf_msg = await self.bot.wait_for('message', timeout=30)
            if conf_msg.content.lower() == 'yes':
                await ctx.send('poggies')
                await publish_channel.send(embed=e)
            else:
                await ctx.send('get some bitches')
        except asyncio.TimeoutError:
            await ctx.send('You took too long to respond bro')
        return
    @publish.error
    async def publish_error(self, ctx, error):
        await ctx.send('Usage: corn?publish [channel_id]')
        await ctx.send('Use corn?show_channels to see channel ids')

    @commands.hybrid_command(with_app_command=True,description="Post a normal message to a channel", usage="corn?speak [channel_id] [message]")
    async def speak(self, ctx, cid:int, *, msg):
        """Posts normal message to channel"""
        # verify usage
        accessible_channels = self.get_channels()
        if cid >= len(accessible_channels) or cid < 0:
            await ctx.send('invalid channel_id')
            return

        # get publish information
        sname = accessible_channels[cid][0].name
        s = "\nServer: " + sname
        publish_channel = accessible_channels[cid][1]
        c = "\nChannel: " + publish_channel.name
        msg_location = s  + c

        # show message to publish
        await ctx.send("Message to Publish: " + msg)
        await ctx.send(msg_location)

        # confirmation
        await ctx.send("Is this information correct? (yes/no)")
        try:
            conf_msg = await self.bot.wait_for('message', timeout=30)
            if conf_msg.content.lower() == 'yes':
                await ctx.send('cum')
                await publish_channel.send(msg)
            else:
                await ctx.send('why waste time i have things to do')
        except asyncio.TimeoutError:
            await ctx.send("i doubt you're busy wtf")
        return
    @speak.error
    async def speak_error(self, ctx, error):
        await ctx.send('Usage: corn?speak [channel_id] [message]')

    def get_roles(self):
        """Return list of pingable roles (server, role) (helper)"""
        print('get_roles()')
        roles = []
        for server in self.bot.guilds:       
            for role in server.roles:
                roles.append((server, role))
        return roles

    @commands.hybrid_command(with_app_command=True,name='roles', aliases=['show_roles', 'get_roles', 'pingable_roles'], description="Get a list of all roles you can ping")
    async def show_roles(self, ctx):
        """Show list of pingable roles"""
        print('show_roles()')
        roles = self.get_roles()
        await ctx.send(embed=embedder.role_list(roles))
        return

    @commands.hybrid_command(with_app_command=True, description="Ping a role and publishes current embedded msg")
    async def ping(self, ctx, rname:str, cid:int):
        """Pings a role and publishes current embedded msg"""
        accessible_channels = self.get_channels()
        if cid >= len(accessible_channels) or cid < 0:
            await ctx.send('invalid channel_id')
            return
        
        # create a list of roles for a given server
        sname = accessible_channels[cid][0].name
        roles = self.get_roles()
        # list of tuples with the correct server name
        roles = filter(lambda r: r[0].name == sname, roles)
        # remove server name from tuples
        roles = [r[1] for r in roles]
        target_role = None

        # get target role info
        for role in roles:
            if role.name.lower() == rname.lower():
                target_role = role
                break
        if target_role is None:
            await ctx.send('invalid role name for server "' + sname +'"')
            return
        
        # get publish information
        sname = accessible_channels[cid][0].name
        s = "\nServer: " + sname
        publish_channel = accessible_channels[cid][1]
        c = "\nChannel: " + publish_channel.name
        msg_location = s  + c
        
        # preview currently loaded embed
        ping_embed = embedder.preview()

        # confirmation
        await ctx.send("Preview:")
        await ctx.send('@' + target_role.name + '', embed=ping_embed)
        await ctx.send(msg_location)
        await ctx.send("Is this information correct? (yes/no)")
        try:
            conf_msg = await self.bot.wait_for('message', timeout=30)
            if conf_msg.content.lower() == 'yes':
                await ctx.send('victory royale!')
                await publish_channel.send('<@&'+str(target_role.id)+'>',embed=ping_embed)
            else:
                await ctx.send('you need to interact with your fans bestie')
        except asyncio.TimeoutError:
            await ctx.send('The incels are waiting val')
        return
    @ping.error
    async def ping_error(self, ctx, error):
        await ctx.send('Usage: corn?ping [role] [channel_id]\nUse corn?roles and corn?channels to get the arguments\nEx: corn?ping twitter 11')

    # TODO add status changer
    @commands.hybrid_command(with_app_command=True, description="Updates Cornelius' status")
    async def status(self, ctx, stype, *, status=None):
        """Updates the status of this bot (sidebar)"""
        # https://stackoverflow.com/questions/59126137/how-to-change-activity-of-a-discord-py-bot
        # usage: corn?status [stype] [status]

        # verify valid status
        status_types = ['playing', 'streaming', 'listening', 'watching']
        if stype.lower() not in status_types:
            await ctx.send(stype + ' is not a valid event name')
            await ctx.send('valid names: ' + str(status_types))
            return
        if status is None:
            await ctx.send('status can\'t be empty!')
            return
        
        # set up status object (activity)
        activity = None
        if stype.lower() == 'playing':
            activity = discord.Game(name=status)
        elif stype.lower() == 'streaming':
            # this also takes a url arg?
            activity = discord.Streaming(name=status, url='https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        elif stype.lower() == 'listening':
            activity = discord.Activity(type=discord.ActivityType.listening, name=status)
        elif stype.lower() == 'watching':
            activity = discord.Activity(type=discord.ActivityType.watching, name=status)

        # changes status
        await ctx.bot.change_presence(activity=activity)
        await ctx.send('status updated')
        return
    @status.error
    async def status_error(self, ctx, error):
        await ctx.send('Usage: corn?status [status_type] [status]')
        await ctx.send('Status Types: playing, streaming, listening, watching')
        await ctx.send(error)

    @commands.hybrid_command(with_app_command=True, description="Set the current embed to send during a server event (boost, welcome, etc.)")
    async def set(self, ctx, ename, *, msg=None):
        """Set the current embed to send during a server event (boost, welcome, etc.)"""
        # usage: corn?set boost; corn?set boost-msg [msg]

        # verify valid event
        event_names = ['boost-embed', 'max-boost', 'boost-msg']
        if ename.lower() not in event_names:
            await ctx.send(ename + ' is not a valid event name')
            await ctx.send('valid names: ' + str(event_names))
            return
        is_embed = ename.lower() !='boost-msg'
        if not is_embed and msg is None:
            await ctx.send('boost-msg can\'t be empty!')
            return

        # fill out example fields with test data
        embed = None
        if is_embed:
            print('in set, loading curr embed')
            embed = embedder.preview()
        uname = 862948136121270312
        num_boosts = random.randint(0, 13)
        next_lvl = -1
        if num_boosts < 2:
            next_lvl = 2 - num_boosts
        elif num_boosts < 7:
            next_lvl = 7 - num_boosts
        elif num_boosts < 14:
            next_lvl = 14 - num_boosts

        # fill boost attributes
        attr = {'num_boosts': num_boosts, 'next_lvl': next_lvl, 'uname': uname}
        if is_embed:
            print('filling curr embed in set')
            test_embed = embedder.fill_fields(copy.deepcopy(embed), attr)
            print('embed filling complete!')
        else:
            test_msg = embedder.fill_fields(msg, attr)
        
        # ask confirmation and save
        await ctx.send("Preview:")
        await ctx.send(f"{{uname}} replaced with <@{uname}>")
        await ctx.send(f"{{num_boosts}} replaced with {num_boosts}")
        await ctx.send(f"{{next_lvl}} replaced with {next_lvl}")
        if is_embed:
            await ctx.send(embed=test_embed)
        else:
            await ctx.send(test_msg)
        await ctx.send("Channel: <#1109592692113022996>")
        await ctx.send("Is this information correct? (yes/no)")
        try:
            conf_msg = await self.bot.wait_for('message', timeout=30)
            # save event response in /bot_embeds/{event_name}.{ext}
            if conf_msg.content.lower() == 'yes':
                dir = 'bot_embeds/'
                content = None
                ext = None
                if is_embed:
                    content = json.dumps(embed.to_dict())
                    ext = '.json'
                else:
                    content = msg
                    ext = '.txt'
                f = open(dir + ename.lower() + ext, 'r+')
                f.truncate(0)
                f.write(content)
                f.close()
                await ctx.send('now this is truly a victory royale')
            else:
                await ctx.send('gun')
        except asyncio.TimeoutError:
            await ctx.send('You real busy arent u... This is all I have val, I only exist to serve u...')
        return
    @set.error
    async def set_error(self, ctx, error):
        await ctx.send('Usage: corn?set [event_name] [optional:msg]')
        await ctx.send('Use corn?help publish for more info on this cmd')
        await ctx.send('Use corn?help attributes for info on fillable fields')
        await ctx.send(error)

    '''
        Misc
    '''
    @commands.hybrid_command(with_app_command=True,description="Get a list of embed attributes used for editing", aliases=['get_attributes'])
    async def attributes(self, ctx):
        """Prints list of embed attributes"""
        await ctx.send(embed=embedder.help('attributes'))

    @commands.hybrid_command(with_app_command=True,description="Reloads all functions to implement changes without a full restart")
    async def reload(self, ctx):
        """Updates cmds without restarting (bot development)"""
        if ctx.author.id != self.admins[0]:
            await ctx.send("You can't run this")
            return
        await self.bot.reload_extension('admin_cmds')
        await self.bot.reload_extension('server_cmds')
        await ctx.send('Reload complete')

    @commands.hybrid_command(with_app_command=True, description="Resync cmds with discord")
    async def resync(self, ctx):
        """Resync cmds with discord (bot development)"""
        if ctx.author.id != self.admins[0]:
            await ctx.send("You can't run this")
            return
        await self.bot.tree.sync(guild=discord.Object(id=self.bot.gid))
        await ctx.send("Resync complete")


async def setup(bot):
    """Adds commands to bot"""
    await bot.add_cog(Admin_Cmds(bot))