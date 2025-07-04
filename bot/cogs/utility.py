import discord
import config
import re
import datetime
import ephem
import random
import os
from discord.ext import commands, tasks
class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Utiliy cog initialized.")
        self.keywords = ["kms", "killing myself", "kys", "kill myself"]
        self.instagram = ["instagram"]
        self.annoy_yan.start()
        print("Utility cog ready. QOTW check loop running:", self.annoy_yan.is_running()) 
        self.DON_RANTS = [
    "Manager Esquire, dost thou knowst about the grim fate of the penguins of Antartica...",
    "ああああああああああああああああああああああああああああああああああああああああああっ!!",
    "The audacity of asking me that... unbelievable! >:c utter falsehood.",
    "Every time someone asks 'is this true?', I lose brain cells. Of course it ain't."
    "You want truth? Go outside and touch some grass first.",
    "No it isn't,",
    "Maybe it is maybe not.",
    "...sharks.... They know... Go ask them..",
    "I hate this job. Yea probably true.",
    "True? YOU CANT HANDLE THE TRUTH!", 
    "Just use Google you troglodyte, it's true >:c",
    "Fact check by true sleep deprived propagandist, True!",
    "I'm not a fucking 8 ball fortune teller.",
    "ig so.",
    "non.",
    "ask sib.",
    "ask ade.",
    "don't ask yan.",
    "nuhuh.",
    "yuhuh.",
    "no idea mate.",
    "Something went wrong, warn yan",
    "&shamenuke"
    ]
    async def anti_suicide_prevention(self, message) : 
        """
        This is a feature that is intended to send a motivational video.
        """
        file_path = 'bot/services/media/neverKYS.mp4'
        try: 
            await message.reply("never kys ^^", file=discord.File(file_path))
        except:
            await message.channel.send("Oops, I couldn't find the file!")

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
            fixed_url = cleaned_url.replace("x.com", "fixupx.com").replace("twitter.com", "fixupx.com")
            if not fixed_url.endswith("/en"):

                fixed_url += "/en"
            message = message.replace(url, fixed_url)

        return message

    


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        message_lower = message.content.lower()

        if any(word in message_lower for word in self.instagram) :
            await message.edit(suppress=True)
            return

        if any(word in message_lower for word in self.keywords) and  not(message.channel.id == config.HEAVY_CHANNEL):
            await self.anti_suicide_prevention(message)
            return


        fixed_content = self.fix_twitter_urls(message.content)
        
        if fixed_content != message.content:
            print("something was actually done")
            await message.reply(fixed_content, mention_author = False)
            await message.edit(suppress=True)
        #don is that true check
        if ((("is that true ?" in message.content.lower()) 
        or ("is this true ?" in message.content.lower())
        or ("is that true?" in message.content.lower())
        or ("is this true?" in message.content.lower())) 
        and self.bot.user in message.mentions):
            await message.reply(random.choice(self.DON_RANTS))


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


    @commands.command(name="pat")
    async def pat(self, ctx, member: discord.Member = None):
        """
        Sends a random pat image or create a pat gif with mentioned user's avatar
        Usage: &pat or &pat @user
        """
        if member is None:
            pat_dir = 'bot/services/media/pat'
            try:
                #Get all images files from the directory 
                image_files = [f for f in os.listdir(pat_dir) if f.lower().endswith(('.png', '.jpg', '.gif'))]
                if not image_files:
                    await ctx.send("No pat images found in the directory!")
                    return
                #Select random image
                random_image = random.choice(image_files)
                file_path = os.path.join(pat_dir, random_image)

                #send the image
                await ctx.send("awawawawa", file=discord.File(file_path))
            except Exception as e:
                await ctx.send(f"Error loading pat image: {str(e)}")
        else : 
            await ctx.send(f"amma be real with you chief that one's annoying to do so it'll be done later, {member.mention} consider yourself patted.")

    @tasks.loop(minutes=60)
    async def annoy_yan(self) :
        """
        fonction who's aim is to PING YAN on a certain time to tell him to come up with a QOTW
        """
        log_channel = self.bot.get_channel(config.LOG_CHANNEL)
        if log_channel :
            role = log_channel.guild.get_role(config.QOTW_RESPONSIBLE)
            if role : 
                now = datetime.datetime.now()
                if now.weekday() == 5 and now.hour == 13 :
                    await log_channel.send(f"YANNNIIIKCK DO THE FUCKING QOTW THING {role.mention}")
            


async def setup(bot) :
    await bot.add_cog(Utility(bot))
