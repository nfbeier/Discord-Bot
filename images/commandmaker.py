# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 01:03:50 2020

@author: Matthew
"""

# %%

mainDir = r'C:\Users\Matthew\Downloads\play2win'
text = ''
import glob

for idx, fileName in enumerate(glob.glob(mainDir + '/*')):
    splitname = fileName.split('\\')[-1]
    text += '\t@commands.command()\n'
    text += '\tasync def %s(self, ctx)\n'%splitname.split('.')[0]
    text += "\t\tawait self.post_image(ctx, '%s')\n\n\n"%splitname

with open(mainDir + '/commands.txt','w') as f:
    f.write(text)