import discord
from discord.ext import commands

class audioplayer(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def testcog(self,ctx,b=''):
        if b != '':
            print(b)
        else:
            print('cog test worked')
