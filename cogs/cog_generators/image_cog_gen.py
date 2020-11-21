
import numpy as np
import glob
import argparse

import os

#os.chdir(r'G:\Users\mstan\git\discord_bot')
parser = argparse.ArgumentParser(description="Sets runtime settings for discord bot")
parser.add_argument('--basepath', type=str,default='cogs/cog_base')
parser.add_argument('--imagepath', type=str,default='images/')
parser.add_argument('--cogpath', type=str,default='cogs/')

args = parser.parse_args()

pathList = glob.glob(args.imagepath + '*.png')
fileList = []
for idx in range(len(pathList)):
    fileList.append(pathList[idx].replace('\\','/').split('/')[-1][0:-4].lower())
print(fileList)
string = ''

#string += "from discord.ext import commands\n\n\n\nclass images(commands.Cog):\n\tdef __init__(self, bot):\n\t\tprint('Cog Loaded: images')\n\t\tself.bot = bot"
#string += "\n\n\n"
with open(args.basepath + '/image_cog_base.py','r') as f:
    string = f.read()
string += '\n\n' 

for idx in range(len(fileList)):
    string += "\t@commands.command()\n\tasync def %s(self,ctx):\n\t\tawait self.post_image(ctx,'%s')\n\n\n"%(fileList[idx],pathList[idx])
string = string.replace('\t','    ') 
with open('cogs/image_cog.py','w') as f:
    print(string,file=f)