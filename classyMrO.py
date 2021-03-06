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
from datetime import datetime
import argparse

parser = argparse.ArgumentParser(description='Parses arguments')
parser.add_argument('--TEST_MODE',type=int,default=0)
parser.add_argument('--UPDATE_ALL',type=int,default=1)
parser.add_argument('--DISABLE_WAKEUP',type=int,default=0)
args = parser.parse_args()

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
        self.serversettings = {}
        self.logging_channels = ['bot-lab','voice_chat','general','smap','petchat']
        with h5py.File('settings/serversettings.h5','r') as hf:
            for key in hf.keys():
                self.serversettings[key] = hf[key][...]
        #await channel.send("Mr. O is well rested from his nap.")

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
        await ctx.message.delete()
        if ctx.author.name == 'thadis':
  
            
            if not(args.TEST_MODE): 
                guild = discord.utils.get(self.bot.guilds,name='Play to Win')
                channel = discord.utils.get(guild.text_channels, name='mr-o-status')
                await channel.send('Mr. O is sleepy sleep. Nighty night.')
            time.sleep(0.5)
            await ctx.bot.logout()
   
    @commands.command()
    async def test(self,ctx):
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
        self.update_profile(member.name)
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
    async def ignore_logging(self,ctx,channelName=''):
        old_ignore = self.players[ctx.author.name+'/ignore_logging'][...]
    
        if channelName == 'RESET':
            self.update_key(ctx.author.name,'ignore_logging',np.array('TEMP',dtype='S'))
        elif not(channelName == '') and not(channelName in old_ignore):
            self.update_key(ctx.author.name,'ignore_logging',np.append(old_ignore, channelName.encode()))
           
    @commands.command()
    async def opt_in_list(self,ctx):
        await ctx.message.delete()
        templist = []
        if self.owner_name == ctx.author.name:

            for guild in self.bot.guilds:
                for member in guild.members:
                    if self.players[member.name + '/enable_logging'][...] == True:
                        if not(member.name in templist):
                            print(member.name + ' has enabled logging')
                            templist.append(member.name)

    @commands.command()
    async def opt_in(self,ctx):
        await ctx.message.delete()
        self.update_key(ctx.author.name,'enable_logging',True)
        await ctx.author.send('You have opted in for message logging. To opt out send the message !opt_out in any channel Mr. O can see.')


    @commands.command()
    async def opt_out(self,ctx):
        await ctx.message.delete()
        self.update_key(ctx.author.name,'enable_logging',False)
        await ctx.author.send('You have opted out for message logging. To confirm use !displaySettings in a channel Mr. O can see and check the "enable_logging" value is False.')



    @commands.command()
    async def currentvolume(self, ctx, playerID=None):
        """
            Inputs: @player"""
       # await bot.delete_message(ctx)

        await ctx.message.delete()
        player = self.find_name(ctx,playerID=playerID)
      #  print(player.name)
        self.update_profile(player.name)
        self.update_profile(ctx.author.name)       
        await ctx.send('Volume set to %0.3f for %s'%(self.players[player.name+'/volume'][...],player.name))

    @commands.command()
    async def volume(self, ctx,volume: float, playerID=None):
        """ Inputs: <desired volume> <@player>optional"""
        await ctx.message.delete()
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
        await ctx.message.delete()
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
            #print('in status==1')
            if ctx.author.name == self.owner_name:
             #   print('in if statement')
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
        await ctx.message.delete()
        player = self.find_name(ctx,playerID=playerID)
        self.update_profile(player.name)
        if player.name == 'thadis':
            if ctx.author.name == 'thadis':
                self.players[player.name + '/bancount'][...] += 1

                await ctx.send('%s Banned by %s'%(player.name,ctx.author.name))
            else:
                self.players[ctx.author.name + '/bancount'][...] += 1
                await ctx.send('%s Banned by %s'%(ctx.author.name,ctx.author.name)) 
        else:    
            self.players[player.name + '/bancount'][...] += 1

            if ctx.author.name == "Kataki" and player.name == 'Kataki':
                await ctx.send('Good that you know your place Kataki')
            else:
                await ctx.send('%s Banned by %s'%(player.name,ctx.author.name))
            
    @commands.command()
    async def bancount(self,ctx,playerID=None):
        """Inputs: <@playerID>optional""" 
        await ctx.message.delete()
        name = self.find_name(ctx,playerID).name
        self.update_profile(name)
        await ctx.send('%s has been banned %d times.'%(name,self.players[name + '/bancount'][...]))                

    @commands.command()
    async def nicknames(self,ctx,playerID=None,length=5):
        await ctx.message.delete()
        name = self.find_name(ctx,playerID).name
        message = '~~~~~\n'
        message += 'Nicknames for '+name + '\n'
        fileName = 'logs/nicknames/'+name.replace(' ','_') +'_nicknames_'+ctx.guild.name.replace(' ','_') + '.dat'
        #print(fileName,name)
        if os.path.exists(fileName):
            with open(fileName,'r') as f:
                lines = f.readlines()
                if len(lines) < length:
                    length = len(lines)
            
                for ii in range(length):
                    splitline = lines[-(ii+1)].replace('\n','').split('\t')

                    message += splitline[0] + '\t' + splitline[2] +'\n'
            await ctx.send(message)
        

        
    @commands.command()
    async def roll(self,ctx,*args):
        """Inputs: Dice roll represented in terms of XdY+AxB-Z"""  
        #await ctx.message.delete()
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
        await ctx.message.delete()
        player = self.find_name(ctx,playerID)
        #print(player.name)
        self.update_profile(player.name)
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
    async def marbles(self,ctx,team,volume=1.0):
        await ctx.message.delete()
        audiofile = glob.glob('audio/marbles/*'+team+'*_marbles.mp3')
        if len(audiofile) > 0:
            audiofile = audiofile[0]
            imagefile = audiofile.replace('audio/','images/').replace('.mp3','.png')
            #print(imagefile) 
            channel = self.find_voicechat(ctx)
        #print(after.channel,after)
       # print(channel) 
            if os.path.isfile(imagefile): 
                await self.post_image(ctx,imagefile.replace('images/',''))
            if channel is not None:
                await self.play_clip(channel,audiofile,min_members=-1,length=2,volume=volume)



    @commands.command()
    async def ska(self,ctx,volume=0.25):
        """Ska 4 Lyfe!"""
        await ctx.message.delete()
        audiofile = 'audio/Brooklyn 99 - Ska interview.mp3' 
       # print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
       # print(channel) 
        if channel is not None:
            await self.play_clip(channel,audiofile,min_members=-1,length=5,volume=volume)

    @commands.command()
    async def baddad(self,ctx):
        """Learn to be a good father Maggie"""
        await ctx.message.delete()
        audiofile = 'audio/Maggie, Bad Dad_n.mp3' 
        #print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
        #print(channel) 
        if channel is not None:
            await self.play_clip(channel,audiofile,volume=0.4,min_members=-1)


    @commands.command()
    async def gooddad(self,ctx):
        """Learn to be a good father Maggie"""
        await ctx.message.delete()
        audiofile = 'audio/Maggie, Good Dad_n.mp3' 
        #print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
        #print(channel) 
        if channel is not None:
            await self.play_clip(channel,audiofile,volume=0.4,min_members=-1)

    @commands.command()
    async def boat(self,ctx):
        """I'm on a boat"""
        await ctx.message.delete()
        audiofile = 'audio/I am on a boat.mp3' 
        #print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
        #print(channel) 
        if channel is not None:
            await self.play_clip(channel,audiofile,volume=0.4,min_members=-1)


    @commands.command()
    async def demonwall(self,ctx):
        await self.wall(ctx)

    @commands.command()
    async def wall(self,ctx,longwall=0):
        """Learn to be a good father Maggie"""
        await ctx.message.delete()
        if longwall == 0:
            length = 6
            audiofile = 'audio/shortwall.mp3'
        else:
            length = 270
            audiofile = 'audio/longwall.mp3'

        #print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
        #print(channel) 
        if channel is not None:
            await self.play_clip(channel,audiofile,volume=0.4,min_members=-1,length=length)

    @commands.command()
    async def nice(self,ctx):
        """Nice"""
        #await ctx.message.delete()
        await self.post_image(ctx, 'nice.png')
        audiofile = 'audio/CLICK Nice.mp3' 
       # print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
       # print(channel) 
        if channel is not None:
            await self.play_clip(channel,audiofile,min_members=-1)




    @commands.command()
    async def hornyonmain(self,ctx):
        await self.hunt(ctx)

    @commands.command()
    async def hunt(self,ctx):
        """Nice"""
        await ctx.message.delete()
        audiofile = 'audio/hunt.mp3' 
       # print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
       # print(channel) 
        if channel is not None:
            await self.play_clip(channel,audiofile,min_members=-1)

    @commands.command()
    async def horn(self,ctx):
        """Nice"""
        await ctx.message.delete()
        audiofile = 'audio/horn.mp3' 
       # print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
       # print(channel) 
        if channel is not None:
            await self.play_clip(channel,audiofile,min_members=-1)

    @commands.command()
    async def tuff(self,ctx):
        """Nice"""
        await ctx.message.delete()
        audiofile = 'audio/tuff.mp3' 
       # print(audiofile)
        channel = self.find_voicechat(ctx)
        #print(after.channel,after)
       # print(channel)
         
        await self.post_image(ctx, 'tuffin.png')
        if channel is not None:
            await self.play_clip(channel,audiofile,length=4,volume=0.5,min_members=-1)



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
       
        await ctx.message.delete()
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

    #~~~~~~~~~~~~~~Image/GIF Commands ~~~~~~~~~~~~~~~~~~~~~~

    @commands.command()
    async def hazers(self,ctx):
        await self.post_image(ctx,'hazers.png')


    @commands.command()
    async def catboy(self,ctx):
        await self.post_image(ctx,'catboy.png')

    @commands.command()
    async def yoona(self,ctx):
        await self.post_image(ctx,'yoona.png')

    @commands.command()
    async def airhorn(self, ctx):
        await self.post_image(ctx, 'airhorn.png')


    @commands.command()
    async def banhammer(self, ctx):
        await self.post_image(ctx, 'banhammer.png')


    @commands.command()
    async def basard(self, ctx):
        await self.post_image(ctx, 'basard.png')


    @commands.command()
    async def Caprese(self, ctx):
        await self.post_image(ctx, 'Caprese.png')


    @commands.command()
    async def ColdOne(self, ctx):
        await self.post_image(ctx, 'ColdOne.png')



    @commands.command()
    async def drift(self, ctx):
        await self.post_image(ctx, 'drift.png')


    @commands.command()
    async def fact(self, ctx):
        await self.post_image(ctx, 'fact.png')


    @commands.command()
    async def Friendship(self, ctx):
        await self.post_image(ctx, 'Friendship.png')


    @commands.command()
    async def gitgud(self, ctx):
        await self.post_image(ctx, 'gitgud.jpg')


    @commands.command()
    async def guillotine(self, ctx):
        await self.post_image(ctx, 'guillotine.png')


    @commands.command()
    async def gungan(self, ctx):
        await self.post_image(ctx, 'gungan.png')


    @commands.command()
    async def HanzMeter(self, ctx):
        await self.post_image(ctx, 'HanzMeter.png')


    @commands.command()
    async def Heirloom(self, ctx):
        await self.post_image(ctx, 'Heirloom.jpg')


    @commands.command()
    async def icon_xl(self, ctx):
        await self.post_image(ctx, 'icon_xl.png')


    @commands.command()
    async def kataki27(self, ctx):
        await self.post_image(ctx, 'kataki27.png')


    @commands.command()
    async def letsgochamp(self, ctx):
        await self.post_image(ctx, 'letsgochamp.png')


    @commands.command()
    async def meowdy(self, ctx):
        await self.post_image(ctx, 'meowdy.png')


#    @commands.command()
#    async def nice(self, ctx):
#        await self.post_image(ctx, 'nice.png')


    @commands.command()
    async def RolfO(self, ctx):
        await self.post_image(ctx, 'RolfO.png')


    @commands.command()
    async def salt(self, ctx):
        await self.post_image(ctx, 'salt.png')


    @commands.command()
    async def Same(self, ctx):
        await self.post_image(ctx, 'Same.png')


    @commands.command()
    async def same2(self, ctx):
        await self.post_image(ctx, 'same2.jpeg')


    @commands.command()
    async def soup(self, ctx):
        await self.post_image(ctx, 'soup.png')


    @commands.command()
    async def thiscodyassmotherfucker(self, ctx):
        await self.post_image(ctx, 'thiscodyassmotherfucker.png')


    @commands.command()
    async def trash(self, ctx):
        await self.post_image(ctx, 'trash.png')


    @commands.command()
    async def tuffin(self, ctx):
        await self.post_image(ctx, 'tuffin.png')


    @commands.command()
    async def WIN(self, ctx):
        await self.post_image(ctx, 'WIN.png')


    @commands.command()
    async def yougotta(self, ctx):
        await self.post_image(ctx, 'yougotta.png')


    @commands.command()
    async def zoeyell(self, ctx):
        await self.post_image(ctx, 'zoeyell.png')



    @commands.command()
    async def trash(self,ctx,gifnum=-1):
        await self.post_gif(ctx,'trash',gifnum)


    @commands.command()
    async def dwagon(self,ctx,gifnum=-1):
        await self.post_gif(ctx,'dwagon',gifnum)

    @commands.command()
    async def dragon(self,ctx,gifnum=-1):
        
        await self.post_gif(ctx,'dragon',gifnum)

  
    @commands.command()
    async def gif(self,ctx,gifName,gifnum=-1):
        await self.post_gif(ctx,gifName,gifnum)
    #~~~~~~~~~~~~~~Testing commands ~~~~~~~~~~~~~~~~~~~
    #commands to help test code

    @commands.command()
    async def displaySettings(self,ctx,playerID=None):
        
        await ctx.message.delete()
        player_settings = self.find_profile(ctx,playerID)
        #print('here')
        modStatus = self.is_mod(ctx.author.name) 
        name = self.find_name(ctx,playerID).name
        if playerID == None:
            message = '```\n'
            message += 'Settings for %s\n'%name 
            for key in player_settings.keys():
                message += '%s: %s\n'%(key,str(player_settings[key]))         
            await ctx.author.send(message+'```')
        elif modStatus == True or ctx.author.name == name:
            message = '```.\n'
            message += 'Settings for %s\n'%name 
            for key in player_settings.keys():
                message += '%s: %s\n'%(key,str(player_settings[key]))         
            await ctx.author.send(message+'```')

    @commands.command()
    async def spam(self,ctx,playerID=None,number=-1):
        if number < 0:
            length = int(np.random.rand(1)*10+4)
        message ='SPAM\n'
        for ii in range(length):
            await ctx.author.send(message)


    @commands.command()
    async def update(self,ctx,playerID=None):
        
        await ctx.message.delete()
        if self.is_mod(ctx.author.name):
            name = self.find_name(ctx,playerID).name
            self.update_profile(name)
            print("Updated %s's profile"%name)

    
    def update_all(self):
        #print(self.bot.guilds)
        for guild in self.bot.guilds:
            for member in guild.members:
                print('Updating ' + member.name)
                self.update_profile(member.name)
                #self.update_key(member.name,'ignore_logging',np.array('TEMP',dtype='S'))
 
    @commands.command()
    async def reset_profile(self,ctx,playerID=None):
        await ctx.message.delete()
       # print(self.is_mod(ctx.author.name))
        if self.is_mod(ctx.author.name):
            name = self.find_name(ctx,playerID).name
        #    print(name)
            self.remove_profile(name)
            self.update_profile(name)


    @commands.command()
    async def reset_nickname(self,ctx,playerID=None):
        player = self.find_name(ctx,playerID)
        if self.is_mod(ctx.author.name) or player.name == ctx.author.name:        
            self.update_profile(player.name)
            nick = self.players[player.name+'/default_nickname'][...]
            await player.edit(nick=str(nick))


    @commands.command()
    async def default_nickname(self,ctx,playerID=None,*args):
        if playerID != None:
            
            nickname = "".join(args[:])
            #print(nickname)
            name = self.find_name(ctx,playerID).name 
            author = self.find_name(ctx,None).name

            if name == author or self.is_mod(ctx.author.name):
                if nickname == '':
                    nickname = name
                self.update_key(name,'default_nickname',nickname)

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
        return 'audio/'+audiofile

    async def play_clip(self,channel,audiofile,volume=0.25,length=3.0,min_members=1):
        #players an audio clip to the correct channel 
        #print(len(channel.members))
        if len(channel.members) > min_members:
          #  print('playing clip ' + audiofile)
            voice = await channel.connect(timeout=1.0)


            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(audiofile),volume=volume)
            voice.play(source, after=lambda e: print('player error: %s' % e) if e else None)
            await asyncio.sleep(length)
            await voice.disconnect()



    async def post_image(self,ctx,fileName):
        filelist = glob.glob('images/'+fileName)
        if len(filelist) > 0:
            #print(ctx.message.content)
            try:
                await ctx.message.delete()
            except discord.errors.NotFound:
                print('not found')
            #print(ctx.message.content)
            await ctx.send(file=discord.File(filelist[0]))

    async def post_gif(self, ctx,gifname,gifnum = -1):
        #print(gifnum) 
        giflist = glob.glob('gifs/'+gifname + '*.gif')
        gifnum = int(gifnum)
        if len(giflist)>0:
            giffile = glob.glob('gifs/'+gifname+'_%d.gif'%gifnum)
            if len(giffile) < 1:
                giffile = [giflist[np.random.randint(0,len(giflist))]]
            if gifname == 'dragon':
                if np.random.random()>0.95:
                    giffile = glob.glob('gifs/dwagon*.gif')
            await ctx.message.delete()
            await ctx.send(file=discord.File(giffile[0]))
        else:
            print('Invalid gif name')

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
        #self.players[name+'/'+key] = value
        if name + '/' + key in self.players:
            del self.players[name+'/'+key]
        self.players[name+'/'+key] = value
        '''
        if name + '/' + key in self.players:
            print(name+'/'+key)
            location = self.players[name+'/'+key]
            location[...] = value
            print(self.players[name+'/'+key][...])
        else:
            self.players[name + '/' + key] = value
        '''
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
        self.create_key(name,'default_nickname',name) 
        self.create_key(name,'enable_logging',False) 
        self.create_key(name,'ignore_logging',np.array('TEMP',dtype='S'))
        #print('New Proile Created for %s'%name)        

    def is_mod(self,name):
        if self.owner_name == name:
            return True
        else:
            return self.players[name+'/mod'][...]

    def user_settings(self,name):
        #returns all of the users settings in a dictionary
        self.update_profile(name)
        dic = {}
        for key in self.players[name].keys():
         #   print(key)
            dic[key] = self.players[name][key][...]
        return dic

    #def delete_message(self,ctx):
    #    await ctx.message.delete()

    def remove_profile(self,name):
        #print(name)
        del self.players[name]

    def update_profile(self,name):
        # Updates a profile to contain all new default settings.
        # Preserves all old keys
        
        print(name)
        self.create_profile('default')

        for key in self.players['default'].keys():
            print(key)
         
        print('Updated Profile for '+name)
        for key in self.players['default'].keys():
            print(name,'/',str(key))
            if name + '/' + key not in self.players:
                if not(key =='/default_nickname'):
                    self.players[name+'/'+key] = self.players['default/'+key]
                else:
                    self.players[name+'/'+key] = name

        '''
        try:
            old_settings = self.user_settings(name)
            self.create_profile(name)
            ti
        except KeyError:
            self.create_profile(name)
            old_settings = self.user_settings(name)
        #print(name)

        
        for key in old_settings.keys():
            self.players[name+'/'+key][...] = old_settings[key]    
        '''
    @commands.Cog.listener()
    async def on_message(self,message):
        #print(message.author)
        guild = message.guild
        if guild:
            name = message.author.name
            #print(message.channel,self.logging_channels[0])    
         #   print(message.channel.name.encode() == self.players[name+'/ignore_logging'][...])
            if message.channel.name in self.logging_channels and not(message.channel.name.encode() in self.players[name+'/ignore_logging'][...]):
            #    print('channel in logging_channel')
                if self.players[name+'/enable_logging'][...]:
             #       print('message logged')
                    if not(os.path.isfile('logs/%d.dat'%(guild.id))):
                        with open('logs/%d.dat'%guild.id,'w') as f:
                            print('created_at\tid\tguild\tauthor.name\tchannel\tchannel.id\tcontent\tattachments',file=f)

                    with open('logs/%d.dat'%(guild.id),'a') as f:
                        print(("{0.created_at}\t{0.id}\t{0.guild}\t{0.author.name}\t{0.channel}\t{0.channel.id}\t{0.content}\t{0.attachments}".format(message)).replace('\n','\\n'),file=f)
            #await bot.process_commands(message)
             
    @commands.Cog.listener()
    async def on_member_update(self,before,after):
        if before.display_name != after.display_name:
            now = datetime.now()
            timestr = now.strftime('%Y/%m/%d  %H:%M:%S')
            with open('logs/nicknames/' + after.name.replace(' ','_') + '_nicknames_' +after.guild.name.replace(' ','_') +'.dat','a') as f:
                f.write(timestr+'\t'+before.display_name + '\t' + after.display_name + '\n')

    @commands.Cog.listener()
    async def on_ready(self):
        print('Logged in as {0} ({0.id})'.format(bot.user))
        print('------')
        if args.UPDATE_ALL:
            self.update_all()
        else:
            print('Skipping Profile Updates')
        guild = discord.utils.get(bot.guilds,name='Play to Win')
        channel = discord.utils.get(guild.text_channels,name='mr-o-status')
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('Profiles Updated Awaiting Commands')
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        if not(args.TEST_MODE) and not(args.DISABLE_WAKEUP):
            await channel.send('Mr. O just woke up from his nap.')
    
    


        

TOKEN = os.getenv('DISCORD_TOKEN')

bot.add_cog(intros(bot))
bot.run(TOKEN)
