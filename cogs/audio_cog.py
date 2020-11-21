from discord.ext import commands
import numpy as np
import glob
from gtts import gTTS
import discord
import os
import asyncio

class audio(commands.Cog):
    def __init__(self, bot):
        print('Cog Loaded: audio')
        self.bot = bot
   
        
    @commands.command()
    async def audio_test(self,ctx):
        """Re-enables Mr. O's playing intro songs."""
        await ctx.send('Audio work')

    @commands.command()
    async def play(self,ctx,playerID=None):
        await ctx.message.delete()
        
    
    async def play_audio(self, channel, member, volume,length,custom_audio, solo_play=0):
        if len(channel.members) > 1 or solo_play:
            default_audio = np.random.random() > custom_audio
            
            audioFile = self.find_audio(member,default_audio)
                
            voice = await channel.connect(timeout=1.0)
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(audioFile),volume=volume)
            voice.play(source,after=lambda e: print('player error: %s' %e) if e else None)
            await asyncio.sleep(length)
            await voice.disconnect()
            
    def generate_audio(self,text,path):        
        myobj = gTTS(text=text,lang='en',slow=False)
        myobj.save(path)
            
            
    def find_audio(self,member,default_audio,directory='audio/'):
        audiofile = ''
        customfile  = 'custom_' + member.name +'_'+ str(member.id)+ '.mp3'
        defaultfile = 'default_' + member.display_name +'_'+ str(member.id)+ '.mp3'
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
