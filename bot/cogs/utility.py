import discord
import config
import re
from discord.ext import commands, tasks
class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Utiliy cog initialized.")
    
    def fix_twitter_urls(self, message):
        message = re.sub(r"https?://(www\.)?(x|twitter)\.com", "https://vxtwitter.com", message)
        message = re.sub(r"\?.*", "", message)
        return message
    


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        fixed_content = self.fix_twitter_urls(message.content)
        
        if fixed_content != message.content:
            print("something was actually done")
            await message.reply(fixed_content, mention_author = False)
            await message.edit(suppress=True)

async def setup(bot) :
    await bot.add_cog(Utility(bot))