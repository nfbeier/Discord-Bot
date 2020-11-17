import asyncio
import os
import discord
from dotenv import load_dotenv
import glob
import numpy as np
from discord.ext import commands
import h5py
import time
from datetime import datetime
import argparse
import sys

sys.path.append('cogs')
from audio_cog import audio
from image_cog import images
from user_cog import users

load_dotenv()
parser = argparse.ArgumentParser(description="Sets runtime settings for discord bot")
parser.add_argument('--TEST_MODE', type=int,default=0)
parser.add_argument('--UPDATE_ALL',type=int,default=1)
parser.add_argument('--DISABLE_WAKEUP',type=int,default=0)

args = parser.parse_args()

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),description='Introductiongeneral discord bot')

class base(commands.Cog):
    #Base function mainly interact through listeners and responding to server events.
    #Functions responding to messasges/user inputs will go into the more specific cogs.
    def __init__(self,bot):
        print('Base Initialized')


    @commands.Cog.listener()
    async def on_message(self, message):
        guild = message.guild

        # TODO: Need to implement logging

        #lis

    @commands.Cog.listener()
    async def on_member_update(self,before,after):
        if before.display_name != after.display_name:
            print('Need to complete')
            # TODO: audio nickname update

            # TODO: append nickname log

    @commands.Cog.listener()
    async def on_ready(self):
        on_ready_message = 'Logged in as {0} ({0.id})'.format(bot.user)
        print('-'*len(on_ready_message))
        print(on_ready_message)
        print('-'*len(on_ready_message))
        # TODO: check for users without a profile

# TODO: Update existing profiles to ensure all fields are satisfied




# TODO:

TOKEN = os.getenv('DISCORD_TOKEN')

bot.add_cog(base(bot))
bot.add_cog(users(bot))
bot.add_cog(audio(bot))
bot.add_cog(images(bot))


bot.run(TOKEN)
