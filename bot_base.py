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


parser = argparse.ArgumentParser(description="Sets runtime settings for discord bot")
parser.add_argument('--TEST_MODE', type=int,default=0)
parser.add_argument('--UPDATE_ALL',type=int,default=1)
parser.add_argument('--DISABLE_WAKEUP',type=int,default=0)

args = parser.parse_args()

bot = commands.Bot(commpand_prefix=commands.when_mentioned_or("!"),
        description='Introduction/general discord bot')

class base(commands.Cogs):
    def __init__(self,bot):
        print('Base Initialized')


TOKEN = os.getenv('DISCORD_TOKEN')

bot.add_cog(base(bot))
bot.run(TOKEN)
