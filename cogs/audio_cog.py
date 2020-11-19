from discord.ext import commands




class audio(commands.Cog):
    def __init__(self, bot):
        print('audio cog loaded')
        self.bot = bot
   
        
    @commands.command()
    async def audio_test(self,ctx):
        """Re-enables Mr. O's playing intro songs."""
        await ctx.send('Audio work')