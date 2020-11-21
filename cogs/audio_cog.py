from discord.ext import commands
import numpy as np
import glob
from gtts import gTTS
import discord
import os
import asyncio
import re
import sys
sys.path.append('functions')
import profile_fun as pf
class audio(commands.Cog):
    def __init__(self, bot):
        print('Cog Loaded: audio')
        self.bot = bot
   
        
    @commands.command()
    async def audio_test(self,ctx):
        """Re-enables Mr. O's playing intro songs."""
        await ctx.send('Audio work')

    @commands.command()
    async def play(self,ctx,playerID=None,custom_audio = 0.5):
        await ctx.message.delete()
        
        try:
            custom_audio = float(custom_audio)
        except ValueError:
            custom_audio = 0.5

       # print(playerID)
        member = pf.find_member(ctx.author.guild,ctx,playerID)
       # print(member)
        channel = self.find_voicechat(ctx)
        
        users = self.bot.get_cog('users')

        volume = await users.pull_value(ctx.author.guild,member,'volume')
        length = await users.pull_value(ctx.author.guild,member,'length')
        solo_play = True
        audio_enabled = await users.pull_value(ctx.author.guild,ctx.author,'audio_enabled')
        if audio_enabled:
            await self.user_audio(channel=channel,member=member,volume=volume,length=length,custom_audio=custom_audio,solo_play=solo_play)
 
    @commands.command()
    async def say(self,ctx,*args):
        await ctx.message.delete()
        string = ''
        for part in args:
            string += part
            string += ' '
        channel = self.find_voicechat(ctx)
        print(args,string)
        filePath = 'audio/clips/say.mp3'
        self.generate_audio(string,filePath)
        await self.play_audio(channel,filePath,volume=0.5,length=3)
            
    @commands.command()
    async def upload_audio(self,ctx,playerID=None):
        users = self.bot.get_cog('users')
        member = await users.find_supermember(ctx,playerID)
            
        if ctx.message.attachments:

            print(ctx.message.attachments[0].filename)#,ctx.message['filename'].attachments)
            if ctx.message.attachments[0].filename[-4:] == '.mp3':
                customfile  = 'custom_' + member.name +'_'+ str(member.id)+ '_'+ str(member.guild.id) +'.mp3'

                await ctx.message.attachments[0].save('audio/users/'+customfile)
                
                
    async def user_audio(self, channel, member, volume,length,custom_audio, solo_play=0):
        if len(channel.members) > 1 or solo_play:
            default_audio = np.random.random() > custom_audio
            if default_audio:
                volume = 0.5
                
            audioFile = self.find_member_audio(member,default_audio)
            await self.play_audio(channel,audioFile,volume,length) 

            
    async def play_audio(self,channel,audioFile,volume=0.5,length=3):
            voice = await channel.connect(timeout=1.0)
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(audioFile),volume=volume)
            voice.play(source,after=lambda e: print('player error: %s' %e) if e else None)
            await asyncio.sleep(length)
            await voice.disconnect()
            
    def find_voicechat(self,ctx):
        for channel in ctx.guild.voice_channels:
            for member in channel.members:
                if member==ctx.author:
                    return channel
        return None    
        
    def generate_audio(self,text,path):        
        myobj = gTTS(text=text,lang='en',slow=False)
        myobj.save(path)
            
            
    def find_member_audio(self,member,default_audio,directory='audio/users/'):
        audiofile = ''
        
        customfile  = 'custom_' + member.name +'_'+ str(member.id)+ '_'+ str(member.guild.id) +'.mp3'
        defaultfile = 'default_' + member.display_name +'_'+ str(member.id)+ '_'+ str(member.guild.id) +'.mp3'
        
        text = member.display_name
        if not(default_audio):
            if os.path.isfile(directory + customfile):
                audiofile = customfile
            elif os.path.isfile(directory + defaultfile):
                audiofile = defaultfile
            else:
                audiofile = defaultfile
                self.generate_audio(text,directory+audiofile)
        else:
            audiofile = defaultfile

            if not(os.path.isfile(directory + defaultfile)):
                self.generate_audio(text,directory+audiofile)

            
        return directory+audiofile    
