#https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py
import asyncio
import os
import discord
import youtube_dl
from dotenv import load_dotenv
import glob
load_dotenv()
from discord.ext import commands
from gtts import gTTS
# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '169.234.214.5' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


client = discord.Client()
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),
                   description='Relatively simple music bot example')

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""


        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(query))

    @commands.command()
    async def yt(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()



        #voice = await after.channel.move_to)     



        #await channel.connect()




@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')



@bot.event
async def on_voice_state_update(member: discord.Member,before, after):
    #print(after.channel)      
    #print(bot.voice_clients)
    audioFile = ''
    if not(member.name == 'Mr. O'):
        if not(glob.glob('audio/' + member.name + '.mp3') == []):
            audioFile = member.name + '.mp3'
            volume = 0.25
        elif not(glob.glob('audio/' + member.display_name + '_n.mp3') == []):
            audioFile = member.display_name + '_n.mp3'
            volume = 0.75
        else:
            myobj = gTTS(text=member.display_name,lang='en',slow=False)
            myobj.save('audio/' + member.display_name + '_n.mp3')
            audioFile = member.display_name + '_n.mp3'
            volume = 0.75
        print(member)
        if audioFile == 'Mr. T.mp3':
            sleepTime = 8
        else:
            sleepTime = 3
        print(after.channel,after)
    
    if audioFile == 'MiraFritz.mp3':
        volume = 0.75
    elif audioFile == 'snorkus.mp3':
        volume = 0.75


    if not(after.channel == None) and not(after.channel == before.channel) and not(member.name == 'Mr. O') and bot.voice_clients == []:

        print(len(after.channel.members))
        if len(after.channel.members) > 1:
            print('Playing Clip ' + audioFile)
            voice = await after.channel.connect(timeout=1.0)


            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('audio/' + audioFile),volume=volume)
            voice.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
            await asyncio.sleep(sleepTime)
            await voice.disconnect()
        

TOKEN = os.getenv('DISCORD_TOKEN')

bot.add_cog(Music(bot))
bot.run(TOKEN)
