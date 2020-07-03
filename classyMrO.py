#https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py
import asyncio
import os
import discord
from dotenv import load_dotenv
import glob
import numpy as np
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
        self.muted = True
        self.players = h5py.File('settings/players.h5','a')
        self.owner_name = 'thadis'
        self.mutetime = time.time()
        
     #~~~~~~~~~~Bot Commands~~~~~~~~~~~
    #Commands directly interacting with the bot's settings.
    @commands.command()
    async def mute(self,ctx):
        """Enables theme song player"""
        self.muted = True
        self.mutetime = 1.0

    @commands.command()
    async def unmute(self,ctx,duration=-1):
        """Disables theme song player. Additional augment will disable it for that many seconds"""
        self.muted = False
        if duration > 0:
            self.mutetime = time.time() + duration
        else:
            self.mutetime = -1.0
            
    @commands.command()
    async def join(self,ctx):
        """Tells Mr. O to join a specified voice chat"""
        await self.join_chat(ctx)    



    
    @commands.command()
    async def gotobed(self,ctx):
        """Turns Mr. O off."""
        if ctx.author.name == 'thadis':
            await ctx.bot.logout()
   
    @commands.command()
    async def test(self,ctx,message):
        """Test"""
        print(message)
        print(ctx.author.id)
        print(message.split('!')[-1].split('>')[0])
        print(bot.get_all_members())
        #print(discord.utils.get(bot.get_all_members(),id=int(message.split('!')[-1].split('>')[0])).split('#')[0])
    @commands.command()
    async def dc(self, ctx):
        """Stops and disconnects the bot from oice"""

        await ctx.voice_client.disconnect()
    @commands.Cog.listener()
    async def on_voice_state_update(self,member: discord.Member,before, after):
        #print(after.channel)      
        #print(bot.voice_clients)
        print(member.name)

        player = self.user_settings(member.name)        
        print(player.keys())
        volume = player['volume']
        length = player['length']
        print(volume)
        print(length) 
        if time.time() > self.mutetime and self.mutetime>0:
            self.muted = True
        else:
            self.muted = False

        if self.muted == True:

            if not(after.channel == None) and not(after.channel == before.channel) and not(member.name == 'Mr. O') and self.bot.voice_clients == []:
                audiofile = self.find_audio(member)

                print(after.channel,after)
                await self.play_clip(after.channel,audiofile,volume,length)
     def find_voicechat(self,ctx):
        for channel in ctx.guild.voice_channels:
            for member in channel.members:
                if member==ctx.author:
                    return channel
        return None               
    #~~~~~~~~~~~Player Profile Commands    
    @commands.command()
    async def volume(self, ctx,volume: float, player=''):
        """Changes the player's volume. Value relative to 1.0"""
        if len(player) == 0:
            name = ctx.author.name
        else:
            name = player
        print(name)
        self.update_profile(name)
        try:
            self.players[name]
        except KeyError:
            self.create_profile(name)
        self.players[name+'/volume'][...] = volume
        await ctx.send('Volume set to %0.2f for %s'%(self.players[name+'/volume'].value,name))


    @commands.command()
    async def length(self, ctx,length: float, player=''):
        """Changes length of song played"""
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






        #voice = await after.channel.move_to)     

                
    @commands.command()
    async def mod(self,ctx,player,status=1):
        """Mods a player"""
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





                
    #~~~~~~~Player Functions~~~~~~~~~~~~
    #Functions that have minimal interaction with the rest of the program
    #and are mainly standalone functions.
    @commands.command()
    async def ban(self,ctx, otherName=''):
        """He knows what he did."""
        if ctx.author.name == "Kataki" and otherName == '':
            await ctx.send('Good that you know your place')
        else:
            await ctx.send('Kataki Banned')
            
    @commands.command()
    async def ban_count(self,ctx):
        self.update_profile('Kataki')
        print(self.players['Kataki/ban_count'])        
        

    
    @commands.command()
    async def roll(self,ctx,*args):
        print(args)  
        diceString = ''
        for ele in args:
            diceString += ele
        import numpy as np

        def diceRoller(diceString):
            a = diceString.split('d')
            numDice = int(a[0])
            diceSize = int(a[1])

            roll = np.random.randint(1,diceSize+1,numDice)
            return roll
        diceString = diceString.replace(' ','')
        splitstr = diceString.split('+')
        for ii in range(len(splitstr)):
            splitstr[ii] = splitstr[ii].split('-')
        output = ''
        result = 0
        
        for ii, dicelist in enumerate(splitstr):
            for jj, dicestring in enumerate(dicelist):
                if dicestring.find('d') != -1:
                    roll = diceRoller(dicestring)
                else:
                    roll = np.array([int(dicestring)])
                if jj == 0:
                    result += np.sum(roll)
                    if ii == 0:
                        for kk,num in enumerate(roll):
                            if kk == 0:
                                output+='(%d'%num
                            else:
                                output += ' + %d'%num
                        output += ')'

                    else:
                        for kk,num in enumerate(roll):
                            if kk == 0:
                                output+=' + (%d'%num
                            else:
                                output += ' + %d'%num
                        output += ')'

                else:
                    result -= np.sum(roll)
                    if ii == 0:
                        for kk,num in enumerate(roll):
                            if kk == 0:
                                output+='(%d'%num
                            else:
                                output += ' + %d'%num
                        output += ')'

                    else:
                        for kk,num in enumerate(roll):
                            if kk == 0:
                                output+=' - (%d'%num
                            else:
                                output += ' + %d'%num
                        output += ')'
        print(str(result) + ' = ' + output)
 
        await ctx.send('Total: %d    Breakdown: %s'%(result,output))

    
    #~~~~~~~Audio Clip Commands~~~~~~~~~
    #any command that mainly just plays audio files
    @commands.command()
    async def play(self,ctx,playerID=None):
        """Players theme song for user or whoever they @"""
        if playerID is not None:
            player = discord.utils.get(ctx.guild.members,id=int(playerID.split('!')[-1].split('>')[0]))
        else:
            player = ctx.author
        print(player)
        
        player_settings = self.user_settings(player.name)        
        #print(player.keys())
        volume = player_settings['volume']
        length = player_settings['length']
        
        audiofile = self.find_audio(player)
        #print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
        #print(channel) 
        if channel is not None:
            await self.play_clip(channel,audiofile,volume=volume,length=length)
            
    @commands.command()
    async def ska(self,ctx,volume=0.25):
        """Ska 4 Lyfe!"""
        audiofile = 'Brooklyn 99 - Ska interview.mp3' 
        print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
        print(channel) 
        if channel is not None:
            await self.play_clip(channel,audiofile,min_members=-1,length=5,volume=volume)

    @commands.command()
    async def baddad(self,ctx):
        """Learn to be a good father Maggie"""
        audiofile = 'Maggie, Bad Dad_n.mp3' 
        print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
        print(channel) 
        if channel is not None:
            await self.play_clip(channel,audiofile,min_members=-1)





    @commands.command()
    async def nice(self,ctx):
        """Nice"""
        audiofile = 'CLICK Nice.mp3' 
        print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
        print(channel) 
        if channel is not None:
            await self.play_clip(channel,audiofile,min_members=-1)

    @commands.command()
    async def coldone(self,ctx):
        """Poppin' one open"""
        await self.nice(ctx)
    
   


 #   @commands.command()
#    async def shoutout(self,ctx):
        
    @commands.command()
    async def shoutout(self,ctx,duration=1.5):
        """Gives Mr. O a shoutout"""
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


    #~~~~~~~~~~~~~~~Helper Commands~~~~~~~~~~~~~~~~~~~~~

    def find_audio(self,member):

        audiofile = ''
        print(member.name)
        print(member.display_name)
        if not(member.name == 'Mr. O'):
            if not(glob.glob('audio/' + member.name + '.mp3') == []):
                audiofile = member.name + '.mp3'

            elif not(glob.glob('audio/' + member.display_name + '_n.mp3') == []):
                audiofile = member.display_name + '_n.mp3'
            else:
                myobj = gTTS(text=member.display_name,lang='en',slow=False)
                myobj.save('audio/' + member.display_name + '_n.mp3')
                audiofile = member.display_name + '_n.mp3'
        
            if audiofile == 'Mr. T.mp3':
                sleeptime = 8
            else:
                sleeptime = 3
        return audiofile

    async def play_clip(self,channel,audiofile,volume=0.25,length=3.0,min_members=1):
        print(len(channel.members))
        if len(channel.members) > min_members:
            print('playing clip ' + audiofile)
            voice = await channel.connect(timeout=1.0)


            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('audio/' + audiofile),volume=volume)
            voice.play(source, after=lambda e: print('player error: %s' % e) if e else None)
            await asyncio.sleep(length)
            await voice.disconnect()



    async def join_chat(self, ctx):
        """Joins a voice channel"""
        print(ctx.voice_client)
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(self.find_voicechat(ctx))
        channel = self.find_voicechat(ctx)
        await channel.connect()

    def create_key(self,name, key, default):
        try:
            self.players.create_dataset(name+'/' + key,data=default)
        except RuntimeError:
            print('Key already exists')
    

    def create_profile(self,name):
        self.create_key(name,'volume',0.5)
        self.create_key(name,'mod',False)
        self.create_key(name,'length',3.0)
        self.create_key(name,'ban',False)
        self.create_key(name,'ban_count',0)
        print('New Proile Created for %s'%name)        


    def user_settings(self,name):
        try: 
            self.players[name]
        except KeyError:
            print('New User. Profile Created')
            self.create_profile(name)
        dic = {}
        for key in self.players[name].keys():
            print(key)
            dic[key] = self.players[name][key].value
        return dic

    def update_profile(self,name):
        old_settings = self.user_settings(name)

        self.create_profile(name)
        
        for key in old_settings.keys():
            self.players[name+'/'+key][...] = dic[key]    





@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')




        

TOKEN = os.getenv('DISCORD_TOKEN')

bot.add_cog(intros(bot))
bot.run(TOKEN)
