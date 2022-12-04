'''
Commands that are run by admins from the bot dms
Editing messages, publishing messages, misc
'''

import discord
from discord.ext import commands
import embedder
import asyncio

class Admin_Cmds(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    '''
        Editing Messages
    '''
    @commands.command()
    async def new(self, ctx):
        """Create a new embedded msg"""
        embedder.new()
        await ctx.send("Current message:", embed=embedder.preview())

    @commands.command()
    async def preview(self, ctx):
        """View current embedded msg"""
        await ctx.send("Current message:", embed=embedder.preview())
    @preview.error
    async def preview_error(self, ctx, error):
        await ctx.send('No msg to preview, create a new msg or load from a template')

    @commands.command(aliases=['update'])
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

    @commands.command()
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

    @commands.command()
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

    @commands.command()
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

    @commands.command()
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

    @commands.command()
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

    @commands.command(name='channels', aliases=['show_channels', 'get_channels'])
    async def show_channels(self, ctx):
        """List accessible servers and channels"""
        channels = self.get_channels()
        await ctx.send(embed = embedder.channels(channels))

    @commands.command()
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

    @commands.command()
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

    @commands.command(name='roles', aliases=['show_roles', 'get_roles', 'pingable_roles'])
    async def show_roles(self, ctx):
        """Show list of pingable roles"""
        print('show_roles()')
        roles = self.get_roles()
        await ctx.send(embed=embedder.role_list(roles))
        return

    @commands.command()
    async def ping(self, ctx, rname:str, cid:int, *, ping_msg):
        """Pings a role and posts embedded msg"""
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
        
        # create embed
        color_map = {'twitter': 0x00acee, 'patreon': 0xff424D, 'youtube': 0xff0000, 'tiktok': 0xff0050}
        if role.name.lower() in color_map.keys():
            color = color_map[role.name.lower()]
        else:
            color = 0x36393F
        ping_embed = discord.Embed(color=color, description=ping_msg)

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
        await ctx.send('Usage: corn?ping [role] [channel_id] [msg]')

    '''
        Misc
    '''
    @commands.command()
    async def admin_help(ctx, group:str = None):
        """Prints admin help menu"""
        await ctx.send(embed=embedder.help(group))    

async def setup(bot):
    """Adds commands to bot"""
    await bot.add_cog(Admin_Cmds(bot))