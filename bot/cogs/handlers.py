import discord
from discord.ext import commands
import config
class Handlers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Handlers cog initialized.")
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')
        log_channel = self.bot.get_channel(config.LOG_CHANNEL)
         
        if log_channel:
            await log_channel.send(f"✅ **{self.bot.user.name} is now online!** 🚀")
        else:
            print("⚠ Log channel not found. Check your config.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        Handles errors.
        """
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Uknown command! Use `.help` to see available commands.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command!")
        else :
            await ctx.send(f"Unhandled error, warn yan.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        print(f"Message received: {message.content}")
        #await self.bot.process_commands(message)
    
async def setup(bot) :
    await bot.add_cog(Handlers(bot))