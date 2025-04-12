import discord
import config
import re
import datetime
import ephem
from discord.ext import commands, tasks
class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Utiliy cog initialized.")
    
    def amount_of_full_moons(self, date_start) :
        """
        calculates the amount of full moons since the date put in input til today

        Args: 
            date_start (datetime.date or str) : date of the beginning in format 'YYYY-MM-DD' or datetime.date object
        Returns:
            int: amount of full moons that happened since the date.
        """
        if isinstance(date_start, str) :
            try:
                date_start = datetime.datetime.strptime(date_start, '%Y-%m-%d').date()
            except:
                raise ValueError("Le format de date doit être 'YYYY-MM-DD'")
        today_date = datetime.date.today()
        if date_start > today_date:
            raise ValueError("The date must be inferior to today's date")
        
        full_moon = ephem.next_full_moon(date_start - datetime.timedelta(days=30))
        date_full_moon = full_moon.datetime().date()

        if date_full_moon > date_start :
            full_moon = ephem.previous_full_moon(date_start)
            date_full_moon = full_moon.datetime().date()

        count = 0

        if date_full_moon == date_start :
            count=1
        
        while True:
            full_moon = ephem.next_full_moon(full_moon)
            date_full_moon = full_moon.datetime().date()

            if date_full_moon <= today_date:
                count += 1
            else:
                break
        return count


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

    @commands.command(name="full_moons")
    async def full_moon_command(self, ctx, date_str: str):
        """
        Command to calculate the amount of full moon since a given date.
        Usage: &full_moon YYYY-MM-DD
        """
        try:
            amount_full_moons = self.amount_of_full_moons(date_str)
            await ctx.reply(f"Since the {date_str}, there has been {amount_full_moons} full moons.", mention_author=False)
        except ValueError as e:
            await ctx.reply(f"Error: {str(e)}", mention_author=False)
        except Exception as e:
            await ctx.reply(f"An error happened: {str(e)}", mention_author=False)

async def setup(bot) :
    await bot.add_cog(Utility(bot))