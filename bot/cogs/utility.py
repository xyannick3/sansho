import discord
import config
import re
from discord.ext import commands, tasks
class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Utiliy cog initialized.")
    
    def fix_twitter_urls(self, message):
        # Match only Twitter/X URLs
        pattern = r"(https?://(?:www\.)?(?:x|twitter)\.com[^\s]*)"
        matches = re.findall(pattern, message)

        for url in matches:
            # Remove query parameters (everything after ?)
            cleaned_url = re.sub(r"\?.*", "", url)
            fixed_url = cleaned_url.replace("twitter.com", "vxtwitter.com").replace("x.com", "vxtwitter.com")
            message = message.replace(url, fixed_url)

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