#https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py
import asyncio
import os
import discord
from dotenv import load_dotenv
import glob
load_dotenv()
from discord.ext import commands
from gtts import gTTS
import h5py
import time
# Suppress noise about console usage from errors
ffmpeg_options = {
    'options': '-vn'
}

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),
                   description='Relatively simple music bot example')


class intros(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.enabled = True
        self.players = h5py.File('settings/players.h5','a')
        self.owner_name = 'thadis'
        self.enabletime = time.time()
   
    @commands.command()
    async def enable(self,ctx):
        self.enabled = True
        self.enabletime = 1.0

    @commands.command()
    async def ban(self,ctx):
        await ctx.send('Kataki Banned')


    @commands.command()
    async def disable(self,ctx,duration=-1):
        self.enabled = False
        if duration > 0:
            self.enabletime = time.time() + duration
        else:
            self.enabletime = -1.0
    @commands.command()
    async def join(self,ctx):
        await self.join_chat(ctx)    
        

    async def join_chat(self, ctx):
        """Joins a voice channel"""
        print(ctx.voice_client)
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(self.find_voicechat(ctx))
        channel = self.find_voicechat(ctx)
        await channel.connect()
    

    @commands.command()
    async def gotobed(self,ctx):
        if ctx.author.name == 'thadis':
            await ctx.bot.logout()
   

    @commands.command()
    async def volume(self, ctx,volume: float, player=''):
        """Changes the player's volume"""
        if len(player) == 0:
            name = ctx.author.name
        else:
            name = player
        print(name)
        try:
            self.players[name]
        except KeyError:
            self.create_profile(name)
        self.players[name+'/volume'][...] = volume
        await ctx.send('Volume set to %0.2f for %s'%(self.players[name+'/volume'].value,name))



    @commands.command()
    async def length(self, ctx,length: float, player=''):
        if len(player) == 0:
            name = ctx.author.name
        else:
            name = player
        
        try:
            self.players[name]
        except KeyError:
            self.create_profile(name)
        if self.players[ctx.author.name+'/mod'].value == True:
            self.players[name+'/length'][...] = length
            await ctx.send('Play Length set to %0.1f seconds for %s'%(self.players[name+'/length'].value,name))
        else:
            await ctx.send('Need mod privileges to change clip length')


    @commands.command()
    async def dc(self, ctx):
        """Stops and disconnects the bot from oice"""

        await ctx.voice_client.disconnect()




        #voice = await after.channel.move_to)     

    
    def find_voicechat(self,ctx):
        for channel in ctx.guild.voice_channels:
            for member in channel.members:
                if member==ctx.author:
                    return channel
        return None

        #await channel.connect()
    def create_profile(self,name):
        self.players.create_dataset(name + '/volume',data=0.5)
        self.players.create_dataset(name + '/mod', data=False)
        self.players.create_dataset(name + '/length',data=3.0)
        self.players.create_dataset(name + '/ban',data=False)
        print('New Proile Created for %s'%name)        

 #   @commands.command()
#    async def shoutout(self,ctx):
        
    @commands.command()
    async def shoutout(self,ctx,duration=1.5):
        print(ctx.channel)
        print(ctx.guild)
        print(ctx.guild.voice_channels)
        if self.players[ctx.author.name + '/mod'].value == 0 and duration > 3.0:
            duration = 3.0
        if duration >39.0:
            duration = 39.0
        
        channel = self.find_voicechat(ctx)
 
        voice = await channel.connect(timeout=1.0)
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('audio/Mr. O.mp3' ),volume=0.5)
        voice.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
           
        await asyncio.sleep(duration)
        await voice.disconnect()
                
    @commands.command()
    async def mod(self,ctx,player,status=1):
        if len(player) == 0:
            await ctx.send('No player name given')
        try:
            self.players[player]
        except KeyError:
            self.create_profile(player)


        try:
            modStatus = self.players[ctx.author.name+'/mod'].value
            if ctx.author.name == self.owner_name:
                modStatus = True
        except KeyError:
            self.create_profile(ctx.author.name)
            modStatus = False
        print('%s Mod Status: ',ctx.author.name,modStatus)
        if modStatus:
            try:
                self.players[player+'/mod'][...] = (status == 1)
            except KeyError:
                await ctx.send('Invalid username')
        print(self.players[player+'/mod'].value)

    @commands.Cog.listener()
    async def on_voice_state_update(self,member: discord.Member,before, after):
        #print(after.channel)      
        #print(bot.voice_clients)
        print(member.name)
        try:
            self.players[member.name]
        except KeyError:
            self.create_profile(member.name)
        
        print(self.players[member.name].keys())
        volume = self.players[member.name + '/volume'].value
        length = self.players[member.name + '/length'].value
        
        if time.time() > self.enabletime and self.enabletime>0:
            self.enabled = True
        else:
            self.enabled = False

        if self.enabled == True:
            audiofile = ''
            if not(member.name == 'Mr. O'):
                if not(glob.glob('audio/' + member.name + '.mp3') == []):
                    audiofile = member.name + '.mp3'

                elif not(glob.glob('audio/' + member.display_name + '_n.mp3') == []):
                    audiofile = member.display_name + '_n.mp3'
                else:
                    myobj = gtts(text=member.display_name,lang='en',slow=false)
                    myobj.save('audio/' + member.display_name + '_n.mp3')
                    audiofile = member.display_name + '_n.mp3'
                print(member)
                if audiofile == 'Mr. T.mp3':
                    sleeptime = 8
                else:
                    sleeptime = 3
                print(after.channel,after)
            


            if not(after.channel == None) and not(after.channel == before.channel) and not(member.name == 'Mr. O') and bot.voice_clients == []:

                print(len(after.channel.members))
                if len(after.channel.members) > 1:
                    print('playing clip ' + audiofile)
                    voice = await after.channel.connect(timeout=1.0)


                    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('audio/' + audiofile),volume=volume)
                    voice.play(source, after=lambda e: print('player error: %s' % e) if e else None)
                    await asyncio.sleep(length)
                    await voice.disconnect()



@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')




        

TOKEN = os.getenv('DISCORD_TOKEN')

bot.add_cog(intros(bot))
bot.run(TOKEN)
