from discord.ext import commands
import os
import discord


class images(commands.Cog):
    def __init__(self, bot):
        print('Cog Loaded: images')
        self.bot = bot
        

    async def post_image(self,ctx,fileName):
        if os.path.isfile(fileName):
            #print(ctx.message.content)
            try:
                await ctx.message.delete()
            except discord.errors.NotFound:
                print('not found')
            #print(ctx.message.content)
            await ctx.send(file=discord.File(fileName)) 


    @commands.command()
    async def airhorn(self,ctx):
        await self.post_image(ctx,'images/airhorn.png')


    @commands.command()
    async def banhammer(self,ctx):
        await self.post_image(ctx,'images/banhammer.png')


    @commands.command()
    async def basard(self,ctx):
        await self.post_image(ctx,'images/basard.png')


    @commands.command()
    async def caprese(self,ctx):
        await self.post_image(ctx,'images/Caprese.png')


    @commands.command()
    async def catboy(self,ctx):
        await self.post_image(ctx,'images/catboy.png')


    @commands.command()
    async def coldone(self,ctx):
        await self.post_image(ctx,'images/ColdOne.png')


    @commands.command()
    async def drift(self,ctx):
        await self.post_image(ctx,'images/drift.png')


    @commands.command()
    async def fact(self,ctx):
        await self.post_image(ctx,'images/fact.png')


    @commands.command()
    async def friendship(self,ctx):
        await self.post_image(ctx,'images/Friendship.png')


    @commands.command()
    async def guillotine(self,ctx):
        await self.post_image(ctx,'images/guillotine.png')


    @commands.command()
    async def gungan(self,ctx):
        await self.post_image(ctx,'images/gungan.png')


    @commands.command()
    async def hanzmeter(self,ctx):
        await self.post_image(ctx,'images/HanzMeter.png')


    @commands.command()
    async def hazers(self,ctx):
        await self.post_image(ctx,'images/hazers.png')


    @commands.command()
    async def icon_xl(self,ctx):
        await self.post_image(ctx,'images/icon_xl.png')


    @commands.command()
    async def kataki27(self,ctx):
        await self.post_image(ctx,'images/kataki27.png')


    @commands.command()
    async def letsgochamp(self,ctx):
        await self.post_image(ctx,'images/letsgochamp.png')


    @commands.command()
    async def meowdy(self,ctx):
        await self.post_image(ctx,'images/meowdy.png')


    @commands.command()
    async def nice(self,ctx):
        await self.post_image(ctx,'images/nice.png')


    @commands.command()
    async def rolfo(self,ctx):
        await self.post_image(ctx,'images/RolfO.png')


    @commands.command()
    async def salt(self,ctx):
        await self.post_image(ctx,'images/salt.png')


    @commands.command()
    async def same(self,ctx):
        await self.post_image(ctx,'images/Same.png')


    @commands.command()
    async def soup(self,ctx):
        await self.post_image(ctx,'images/soup.png')


    @commands.command()
    async def thiscodyassmotherfucker(self,ctx):
        await self.post_image(ctx,'images/thiscodyassmotherfucker.png')


    @commands.command()
    async def trash(self,ctx):
        await self.post_image(ctx,'images/trash.png')


    @commands.command()
    async def tuffin(self,ctx):
        await self.post_image(ctx,'images/tuffin.png')


    @commands.command()
    async def win(self,ctx):
        await self.post_image(ctx,'images/WIN.png')


    @commands.command()
    async def yoona(self,ctx):
        await self.post_image(ctx,'images/yoona.png')


    @commands.command()
    async def yougotta(self,ctx):
        await self.post_image(ctx,'images/yougotta.png')


    @commands.command()
    async def zoeyell(self,ctx):
        await self.post_image(ctx,'images/zoeyell.png')



