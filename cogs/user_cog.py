from discord.ext import commands




class users(commands.Cog):
    def __init__(self, bot):
        print('users cog loaded')
        
        
    @commands.command()
    async def users_test(self,ctx):
        """Re-enables Mr. O's playing intro songs."""
        await ctx.send('Users work')