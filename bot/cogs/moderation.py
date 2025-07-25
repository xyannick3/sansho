import discord
import config
import asyncio
from discord.ext import commands, tasks
import services.database as db
import datetime, pytz
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
        self.daily_mute.start()
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

    ###################SHAMEALL############################

    @commands.command(name="shamenuke")
    @commands.has_permissions(manage_roles=True)
    async def shamenuke(self, ctx, duration="10m") :
        """
        to use if very upset >:v with everyone (might break the bot)
        """
        ctx.send("nuke request acknowledged, please await")
        guild = ctx.guild
        shame_role = guild.get_role(config.SHAME_ROLE)
        if not shame_role:
            return await ctx.send("Error: Shame role not found!")
        
        time_units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = duration[-1]
        if unit not in time_units or not duration[:-1].isdigit():
            return await ctx.send("Invalid duration format! Use `1h`, `30m`, `2d`, etc.")
        duration_seconds = int(duration[:-1]) * time_units[unit]

        shamed_count = 0
        
        members_to_shame = [
            member for member in guild.members
        ]
        shamed_count = len(members_to_shame)

        await asyncio.gather(*[member.add_roles(shame_role) for member in members_to_shame])

        for member in members_to_shame:
            db.add_shame(member.id, guild.id, duration_seconds)
        
        await ctx.send(f" **SHAME NUKE ACTIVATED!** {shamed_count} users have been shamed for {duration}.")

        log_channel = guild.get_channel(config.LOG_CHANNEL)
        if log_channel :
            log_channel.send(f" **Shame Nuke Activated by {ctx.author.name}!**")

    ###################UNSHAMEALL##########################

    @commands.command(name="unshameall")
    @commands.has_permissions(manage_roles=True)
    async def unshameall(self, ctx):
        """
        removes shame for all users in the server.
        """
        guild = ctx.guild
        shame_role = guild.get_role(config.SHAME_ROLE)
        megashame_role = guild.get_role(config.MEGASHAME_ROLE)

        if not shame_role or not megashame_role :
            return await ctx.send("Error: shame roles not found!")
        
        member_to_unshame = [
            member for member in guild.members
        ]

        unshamed_count = len(member_to_unshame)

        await asyncio.gather(*[member.remove_roles(shame_role, megashame_role) for member in member_to_unshame])

        for member in member_to_unshame:
            db.remove_shame(member.id)

        await ctx.send(f"**Shame Purge Complete!** {unshamed_count} users have been freed.")
        
        log_channel = guild.get_channel(config.LOG_CHANNEL)
        if log_channel:
            await log_channel.send(f" **Shame purge by {ctx.author.name}!**")


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


    @tasks.loop(minutes=1)
    async def daily_mute(self) :
        """
        mute someone because he's been bad and needs his bed time
        """
        est_tz = pytz.timezone("America/New_York")
        now_est = datetime.datetime.now(est_tz)
        log_channel = self.bot.get_channel(config.LOG_CHANNEL)
        member_role = log_channel.guild.get_role(config.MEMBER_ROLE)
        shameboxed_role = log_channel.guild.get_role(config.MUTE_ROLE)


        if now_est.hour == 2 and now_est.minute == 0 :
            if log_channel : 
                member = log_channel.guild.get_member(config.BEDTIME_MEMBER)
                await log_channel.send(f"{member.name}'s bedtime is now")

            await member.remove_roles(member_role)
            await member.add_roles(shameboxed_role)

            #Store in database

            db.add_mute(member.id, log_channel.guild.id, 6*60*60) # 6h in seconds
            if log_channel :
                await log_channel.send(f"{member.name} has been muted for 6h")



###################SETUP###################################
async def setup(bot):
    db.setup_database()
    await bot.add_cog(Moderation(bot))