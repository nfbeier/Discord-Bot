from discord.ext import commands




class images(commands.Cog):
    def __init__(self, bot):
        print('Cog Loaded: images')
        self.bot = bot
        
    @commands.command()
    async def images_test(self,ctx):
        """Re-enables Mr. O's playing intro songs."""
        await ctx.send('Images work')
        
