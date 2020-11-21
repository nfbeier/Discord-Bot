from discord.ext import commands
import os
import sys
sys.path.append('functions')
import profile_fun as pf


class general(commands.Cog):
    def __init__(self, bot):
        print('Cog Loaded: general')
        self.bot = bot

    @commands.command()
    async def roll(self,ctx,*args):
        await ctx.send(pf.roll_dice(args))