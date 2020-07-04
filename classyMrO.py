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
    async def unmute(self,ctx):
        """Re-enables Mr. O's playing intro songs."""
        self.muted = True
        self.mutetime = 1.0

    @commands.command()
    async def mute(self,ctx,duration=-1):
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
        if ctx.author.name == 'thadis':
            print(message)
            print(ctx.author.id)
            print(message.split('!')[-1].split('>')[0])
            print(bot.get_all_members())
        #print(discord.utils.get(bot.get_all_members(),id=int(message.split('!')[-1].split('>')[0])).split('#')[0])

    @commands.command()
    async def dc(self, ctx):
        """Stops and disconnects the bot from voice"""
        await ctx.voice_client.disconnect()

    @commands.Cog.listener()
    async def on_voice_state_update(self,member: discord.Member,before, after):
        #print(after.channel)      
        #print(bot.voice_clients)
        #print(member.name)

        player = self.user_settings(member.name)        
        #print(player.keys())
        volume = player['volume']
        length = player['length']
        #print(volume)
        #print(length) 
        if time.time() > self.mutetime and self.mutetime>0:
            self.muted = True
        else:
            self.muted = False

        if self.muted == True:

            if not(after.channel == None) and not(after.channel == before.channel) and not(member.name == 'Mr. O') and self.bot.voice_clients == []:
                audiofile = self.find_audio(member)

       #         print(after.channel,after)
                await self.play_clip(after.channel,audiofile,volume,length)
                
                
    def find_voicechat(self,ctx):
        for channel in ctx.guild.voice_channels:
            for member in channel.members:
                if member==ctx.author:
                    return channel
        return None               
    #~~~~~~~~~~~Player Profile Commands    
 

    @commands.command()
    async def currentvolume(self, ctx, playerID=None):
        """
            Inputs: @player"""
        player = self.find_name(ctx,playerID=playerID)
      #  print(player.name)
        self.update_profile(player.name)
        self.update_profile(ctx.author.name)       
        await ctx.send('Volume set to %0.3f for %s'%(self.players[player.name+'/volume'][...],player.name))

    @commands.command()
    async def volume(self, ctx,volume: float, playerID=None):
        """ Inputs: <desired volume> <@player>optional"""
        player = self.find_name(ctx,playerID=playerID)
      #  print(player.name)
        self.update_profile(player.name)
        self.update_profile(ctx.author.name)       
        modStatus = self.players[ctx.author.name + '/mod'][...]
        if modStatus or (ctx.author.name == player.name):
            oldVolume = self.players[player.name+'/volume'][...]
            self.players[player.name+'/volume'][...] = volume
            await ctx.send('Volume set from %0.3f to %0.3f for %s'%(oldVolume,self.players[player.name+'/volume'][...],player.name))
        else:
            await ctx.send("Need mod status to change someone else's volume")

    @commands.command()
    async def length(self, ctx,length: float, playerID=None):
        """Inputs: <desired length> <@player>optional   MODS ONLY"""
        player = self.find_name(ctx,playerID=playerID)
        self.update_profile(player.name)
        self.update_profile(ctx.author.name)       
        modStatus = self.players[ctx.author.name + '/mod'][...]

        if modStatus:
            self.update_key(player.name,'length',length)
            await ctx.send('Play Length set to %0.1f seconds for %s'%(self.players[player.name+'/length'][...],player.name))
        else:
            await ctx.send('Need mod privileges to change clip length')
               
    @commands.command()
    async def mod(self,ctx,playerID=None,status=1):
        """Inputs: <@player> <status>optional """
        player = self.find_name(ctx,playerID=playerID)
        self.update_profile(player.name)
        self.update_profile(ctx.author.name)
            
        modStatus = self.players[ctx.author.name + '/mod'][...]
        if status == 1:
            if ctx.author.name == self.owner_name:
                try:
     #               print(self.players[player.name + '/mod'][...])
                     self.update_key(player.name,'mod',1)
                except KeyError:
                    await ctx.send('Invalid username')
        else:
            if modStatus == 1 or ctx.author.name == self.owner_name:
                try:
                    self.update_key(player.name,'mod',0)
                except KeyError:
                    await ctx.send('Invalid username')
                
    #~~~~~~~Player Functions~~~~~~~~~~~~
    #Functions that have minimal interaction with the rest of the program
    #and are mainly standalone functions.
    @commands.command()
    async def ban(self,ctx, playerID=None):
        """Inputs: <@player>optional"""
        player = self.find_name(ctx,playerID=playerID)
        self.update_profile(player.name)
        self.players[player.name + '/bancount'][...] += 1

        if ctx.author.name == "Kataki" and otherName == '':
            await ctx.send('Good that you know your place')
        else:
            await ctx.send('%s Banned'%player.name)
            
    @commands.command()
    async def bancount(self,ctx,playerID=None):
        """Inputs: <@playerID>optional""" 
        name = self.find_name(ctx,playerID).name
        self.update_profile(name)
        await ctx.send('%s has been banned %d times.'%(name,self.players[name + '/bancount'][...]))                

    
    @commands.command()
    async def roll(self,ctx,*args):
        """Inputs: Dice roll represented in terms of XdY+AxB-Z"""  
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
    #print(str(result) + ' = ' + output)
 
        await ctx.send('Total: %d    Breakdown: %s'%(result,output))

    
    #~~~~~~~Audio Clip Commands~~~~~~~~~
    #any command that mainly just plays audio files
    @commands.command()
    async def play(self,ctx,playerID=None):
        """Inputs: <@player>optional"""
        player_settings = self.find_profile(ctx,playerID=playerID)       
        #print(player.keys())
        volume = player_settings['volume']
        length = player_settings['length']
        player = self.find_name(ctx,playerID) 
        audiofile = self.find_audio(player)
        #print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
        #print(channel) 
        if channel is not None:
            await self.play_clip(channel,audiofile,volume=volume,length=length,min_members=-1)
            
    @commands.command()
    async def ska(self,ctx,volume=0.25):
        """Ska 4 Lyfe!"""
        audiofile = 'Brooklyn 99 - Ska interview.mp3' 
       # print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
       # print(channel) 
        if channel is not None:
            await self.play_clip(channel,audiofile,min_members=-1,length=5,volume=volume)

    @commands.command()
    async def baddad(self,ctx):
        """Learn to be a good father Maggie"""
        audiofile = 'Maggie, Bad Dad_n.mp3' 
        #print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
        #print(channel) 
        if channel is not None:
            await self.play_clip(channel,audiofile,volume=0.4,min_members=-1)





    @commands.command()
    async def nice(self,ctx):
        """Nice"""
        audiofile = 'CLICK Nice.mp3' 
       # print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
       # print(channel) 
        if channel is not None:
            await self.play_clip(channel,audiofile,min_members=-1)


    @commands.command()
    async def hazers(self,ctx):
        """Nice"""
        audiofile = 'Hazers for the win.mp3' 
        #print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
       # print(channel) 
        audiofile = self.create_audio('Hazers for the win')
        if channel is not None:
            await self.play_clip(channel,audiofile,min_members=-1)

    @commands.command()
    async def coldone(self,ctx):
        """Poppin' one open"""
        await self.nice(ctx)
        
    @commands.command()
    async def shoutout(self,ctx,duration=1.5):
        """Gives Mr. O a shoutout"""
        #print(ctx.channel)
        #print(ctx.guild)
        #print(ctx.guild.voice_channels)
        if self.players[ctx.author.name + '/mod'][...] == 0 and duration > 3.0:
            duration = 3.0
        if duration >39.0:
            duration = 39.0
        
        channel = self.find_voicechat(ctx)
 
        voice = await channel.connect(timeout=1.0)
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('audio/Mr. O.mp3' ),volume=0.5)
        voice.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
           
        await asyncio.sleep(duration)
        await voice.disconnect()

    #~~~~~~~~~~~~~~Testing commands ~~~~~~~~~~~~~~~~~~~
    #commands to help test code

    @commands.command()
    async def displaySettings(self,ctx,playerID=None):
        player_settings = self.find_profile(ctx,playerID)
        modStatus = self.is_mod(ctx.author.name) 
        name = self.find_name(ctx,playerID).name
        if playerID == None:
            message = '.\n'
            message += 'Settings for %s\n'%name 
            for key in player_settings.keys():
                message += '%s: %s\n'%(key,str(player_settings[key]))         
            await ctx.author.send(message)
        elif modStatus == True or ctx.author.name == name:
            message = '.\n'
            message += 'Settings for %s\n'%name 
            for key in player_settings.keys():
                message += '%s: %s\n'%(key,str(player_settings[key]))         
            await ctx.author.send(message)

    @commands.command()
    async def update(self,ctx,playerID=None):
        if self.is_mod(ctx.author.name):
            name = self.find_name(ctx,playerID).name
            self.update_profile(name)
            print("Updated %s's profile"%name)

    #~~~~~~~~~~~~~~~Helper Commands~~~~~~~~~~~~~~~~~~~~~
    
    def find_name(self,ctx,playerID=None):
        if playerID is not None:
            name = discord.utils.get(ctx.guild.members,id=int(playerID.split('!')[-1].split('>')[0]))
        else:
            name = ctx.author
        return name
    
    def find_profile(self,ctx,playerID=None):
        #Finds the correct profile name for the player that was @ed
        player = self.find_name(ctx,playerID=playerID)        
        player_settings = self.user_settings(player.name) 
        return player_settings

    def create_audio(self,message):

        myobj = gTTS(text=message,lang='en',slow=False)
        myobj.save('audio/' + message + '.mp3')
        audiofile = message + '.mp3'
        return audioFile
    
    def find_audio(self,member):
        #Finds the audio file associated with the correct player
        audiofile = ''
        #print(member.name)
        #print(member.display_name)
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
        #players an audio clip to the correct channel 
        #print(len(channel.members))
        if len(channel.members) > min_members:
          #  print('playing clip ' + audiofile)
            voice = await channel.connect(timeout=1.0)


            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('audio/' + audiofile),volume=volume)
            voice.play(source, after=lambda e: print('player error: %s' % e) if e else None)
            await asyncio.sleep(length)
            await voice.disconnect()



    async def join_chat(self, ctx):
        #Joins a voice channel
        #print(ctx.voice_client)
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(self.find_voicechat(ctx))
        channel = self.find_voicechat(ctx)
        await channel.connect()

    def create_key(self,name, key, default):
        #adds a new setting to a player's settings. If it already 
        self.update_key(name,key,default)
            
    def update_key(self,name,key,value):
        #try:    
        
        #print(name+'/'+key)

        if name + '/' + key in self.players:
            location = self.players[name+'/'+key]
            location[...] = value
        else:
            self.players[name + '/' + key] = value
        #except RuntimeError:
        #    self.players.create_dataset(name+'/'+key,data=value)

    def create_profile(self,name):
        # Creates a profile for the user
        self.create_key(name,'volume',0.5)
        self.create_key(name,'mod',False)
        self.create_key(name,'length',3.0)
        self.create_key(name,'ban',False)
        self.create_key(name,'bancount',0)
        self.create_key(name,'enable_play',1)
        #print('New Proile Created for %s'%name)        

    def is_mod(self,name):
        return self.players[name+'/mod'][...]

    def user_settings(self,name):
        #returns all of the users settings in a dictionary
    #    self.update_profile(name)
        dic = {}
        for key in self.players[name].keys():
         #   print(key)
            dic[key] = self.players[name][key][...]
        return dic

    def update_profile(self,name):
        # Updates a profile to contain all new default settings.
        # Preserves all old keys
        old_settings = self.user_settings(name)
        #print(name)
        self.create_profile(name)
        
        for key in old_settings.keys():
            self.players[name+'/'+key][...] = old_settings[key]    





@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')




        

TOKEN = os.getenv('DISCORD_TOKEN')

bot.add_cog(intros(bot))
bot.run(TOKEN)
