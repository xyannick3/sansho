import discord
import config
from discord.ext import commands, tasks
import services.database as db
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Moderation cog initialized.")
        self.log_channel = None
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.log_channel = self.bot.get_channel(config.LOG_CHANNEL)
        self.check_mutes.start()
        self.check_shame.start()
        print("Moderation cog ready. Mute check loop running :", self.check_mutes.is_running())
        print("Moderation cog ready. Shame check loop running:", self.check_shame.is_running())

    
    #################PURGE#################################

    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount:int):
        """
        Deletes a specified number of messages from the channel
        """
        await ctx.channel.purge(limit = amount)
        await ctx.send(f"purged {amount} messages.")
        log_channel = self.bot.get_channel(config.LOG_CHANNEL)  
        await log_channel.send(f"{ctx.author.name} has ordered the purge of {amount} messages in {ctx.channel}")
    
    
    #################VERIFY################################

    @commands.command(name="verify")
    @commands.has_permissions(administrator=True)
    async def verify_user(self, ctx, member: discord.Member):
        guild = ctx.guild
        member_role = guild.get_role(config.MEMBER_ROLE)
        presentation_role = guild.get_role(config.PRESENTATION_ROLE)
        log_channel = guild.get_channel(config.LOG_CHANNEL)

        if not member_role or not presentation_role or not log_channel:
            return await ctx.send("❌ Error: One or more roles/log channel not found in settings!")
        
        if presentation_role in member.roles:
            await member.remove_roles(presentation_role)
        
        await member.add_roles(member_role)

        await ctx.send(f" {member.mention} has been verified!")

        await log_channel.send(f"{member.name} has been verified by **{ctx.author.name}**")
    
    #############################MUTE######################

    @commands.command(name="mute")
    @commands.has_permissions(manage_roles=True)
    async def mute_user(self, ctx, member: discord.Member, duration="10m"):
        """
        Mutes a user for a given duration.
        Usage: .mute @user 1h
        """
        guild = ctx.guild
        member_role = guild.get_role(config.MEMBER_ROLE)
        shameboxed_role = guild.get_role(config.MUTE_ROLE)

        if not member_role or not shameboxed_role: 
            return await ctx.send("Error: One or more roles not found in settings!")
        time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = duration[-1]
        if unit not in time_units or not duration[:-1].isdigit():
            return await ctx.send("Invalid duration format! Use `1h`, `30m`, `2d`, etc..")
        duration_seconds = int(duration[:-1]) * time_units[unit]

        #Apply mute
        await member.remove_roles(member_role)
        await member.add_roles(shameboxed_role)

        #Store in database

        db.add_mute(member.id, guild.id, duration_seconds)

        await ctx.send(f"{member.mention} has been muted for {duration}")
        log_channel = guild.get_channel(config.LOG_CHANNEL)
        if log_channel :
            await log_channel.send(f"{member.name} has been muted by **{ctx.author.name}** for {duration}")
    
    ################UNMUTE#################################


    @commands.command(name="unmute")
    @commands.has_permissions(manage_roles=True)
    async def unmute_user(self, ctx, member: discord.Member):
        """Unmutes a user manually. Usage: .unmute @user"""
        guild = ctx.guild
        member_role = guild.get_role(config.MEMBER_ROLE)
        shameboxed_role = guild.get_role(config.MUTE_ROLE)

        if not member_role or not shameboxed_role:
            return await ctx.send("❌ Error: One or more roles not found!")

        # Ensure member exists (user could have left)
        if not member:
            return await ctx.send("❌ Error: User not found in the server!")

        try:
            await member.remove_roles(shameboxed_role)
            await member.add_roles(member_role)
            db.remove_mute(member.id)
        except Exception as e:
            return await ctx.send(f"⚠ Error unmuting user: {e}")

        await ctx.send(f"{member.mention} has been unmuted!")
        
        log_channel = guild.get_channel(config.LOG_CHANNEL)
        if log_channel:
            await log_channel.send(f"{member.name} was unmuted by {ctx.author.name}.")

    ##################AUTOMATIC UNMUTE PROCESSS############

    @tasks.loop(minutes=1)
    async def check_mutes(self): 
        """
        Background task that checks expired mutes and unmutes users.
        Runs every 60 seconds.
        """
        expired_mutes = db.get_expired_mutes()
        for user_id, guild_id in expired_mutes:
            guild = self.bot.get_guild(guild_id)
            if guild:
                member = guild.get_member(user_id)
                if member:
                    member_role = guild.get_role(config.MEMBER_ROLE)
                    shameboxed_role = guild.get_role(config.MUTE_ROLE)

                    if member_role and shameboxed_role:
                        await member.remove_roles(shameboxed_role)
                        await member.add_roles(member_role)
                        db.remove_mute(user_id)

                        log_channel = guild.get_channel(config.LOG_CHANNEL)
                        if log_channel:
                            await log_channel.send(f"{member.name} was automatically unmuted.")
                else: 
                    print("member not found, removing the mute from database")
                    db.remove_mute(user_id)
            else :
                print("guild not found")



        

    ###########################SHAME#######################

    @commands.command(name="shame")
    @commands.has_permissions(manage_roles=True)
    async def shame_user(self, ctx, member: discord.Member, duration="10m"):
        """
        shames a user for a given duration.
        Usage: .mute @user 1h
        """
        guild = ctx.guild
        member_role = guild.get_role(config.MEMBER_ROLE)
        shame_role = guild.get_role(config.SHAME_ROLE)

        if not member_role or not shame_role: 
            return await ctx.send("Error: One or more roles not found in settings!")
        time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = duration[-1]
        if unit not in time_units or not duration[:-1].isdigit():
            return await ctx.send("Invalid duration format! Use `1h`, `30m`, `2d`, etc..")
        duration_seconds = int(duration[:-1]) * time_units[unit]

        #Apply mute
        await member.add_roles(shame_role)

        #Store in database

        db.add_shame(member.id, guild.id, duration_seconds)

        await ctx.send(f"{member.mention} has been shamed for {duration}")
        log_channel = guild.get_channel(config.LOG_CHANNEL)
        if log_channel :
            await log_channel.send(f"{member.name} has been shamed by **{ctx.author.name}** for {duration}")
    

    ########################MEGASHAME######################

    @commands.command(name="megashame")
    @commands.has_permissions(manage_roles=True)
    async def megashame_user(self, ctx, member: discord.Member, duration="10m"):
        """
        megashames a user for a given duration.
        this removes the user's media permissions.
        Usage: .mute @user 1h
        """
        guild = ctx.guild
        member_role = guild.get_role(config.MEMBER_ROLE)
        shame_role = guild.get_role(config.MEGASHAME_ROLE)

        if not member_role or not shame_role: 
            return await ctx.send("Error: One or more roles not found in settings!")
        time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = duration[-1]
        if unit not in time_units or not duration[:-1].isdigit():
            return await ctx.send("Invalid duration format! Use `1h`, `30m`, `2d`, etc..")
        duration_seconds = int(duration[:-1]) * time_units[unit]

        #Apply mute
        await member.add_roles(shame_role)

        #Store in database

        db.add_shame(member.id, guild.id, duration_seconds)

        await ctx.send(f"{member.mention} has been shamed for {duration}")
        log_channel = guild.get_channel(config.LOG_CHANNEL)
        if log_channel :
            await log_channel.send(f"{member.name} has been shamed by **{ctx.author.name}** for {duration}")
    


################UNSHAME####################################


    @commands.command(name="unshame")
    @commands.has_permissions(manage_roles=True)
    async def unshame_user(self, ctx, member: discord.Member):
        """unshame a user manually. 
        Usage: .unmute @user"""
        guild = ctx.guild
        member_role = guild.get_role(config.MEMBER_ROLE)
        shame_role = guild.get_role(config.SHAME_ROLE)
        megashame_role = guild.get_role(config.MEGASHAME_ROLE)
        if not member_role or not shame_role or not megashame_role:
            return await ctx.send("❌ Error: One or more roles not found!")

        # Ensure member exists (user could have left)
        if not member:
            return await ctx.send("❌ Error: User not found in the server!")

        try:
            await member.remove_roles(shame_role)
            await member.remove_roles(megashame_role)
            db.remove_shame(member.id)
        except Exception as e:
            return await ctx.send(f"⚠ Error unshaming user: {e}")

        await ctx.send(f"{member.mention} has been unshamed!")
        
        log_channel = guild.get_channel(config.LOG_CHANNEL)
        if log_channel:
            await log_channel.send(f"{member.name} was unshamed by {ctx.author.name}.")

    ##################AUTOMATIC UNSHAME PROCESSS###########

    @tasks.loop(minutes=1)
    async def check_shame(self): 
        """
        Background task that checks expired shame and unshame users.
        Runs every 60 seconds.
        """
        expired_mutes = db.get_expired_shames()
        for user_id, guild_id in expired_mutes:
            guild = self.bot.get_guild(guild_id)
            if guild:
                member = guild.get_member(user_id)
                if member:
                    member_role = guild.get_role(config.MEMBER_ROLE)
                    shame_role = guild.get_role(config.SHAME_ROLE)
                    megashame_role = guild.get_role(config.MEGASHAME_ROLE)

                    if member_role and shame_role and megashame_role:
                        await member.remove_roles(shame_role)
                        await member.remove_roles(megashame_role)
                        db.remove_shame(user_id)

                        log_channel = guild.get_channel(config.LOG_CHANNEL)
                        if log_channel:
                            await log_channel.send(f"{member.name} was automatically unshamed.")
                else: 
                    print("member not found, removing the shame from database")
                    db.remove_mute(user_id)
            else :
                print("guild not found")




###################SETUP###################################
async def setup(bot):
    db.setup_database()
    await bot.add_cog(Moderation(bot))