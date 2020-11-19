from discord.ext import commands
import discord
import sys
#from profile_fun import *
import os

class base(commands.Cog):
    #Base function mainly interact through listeners and responding to server events.
    #Functions responding to messasges/user inputs will go into the more specific cogs.
    def __init__(self,bot):
        print('base cog loaded')
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self,member: discord.Member, before, after):
        a = 1
        # TODO: Implement 

    @commands.Cog.listener()
    async def on_message(self, message):
        guild = message.guild

        # TODO: Need to implement logging

        #lis

    @commands.Cog.listener()
    async def on_member_update(self,before,after):
        if before.display_name != after.display_name:
            print('Need to complete')
            print('Was %s now %s'%(before.display_name,after.display_name))
            print('Name: ',after.name)
            print('id: ', after.id)
            # TODO: audio nickname update

            # TODO: append nickname log

    @commands.Cog.listener()
    async def on_ready(self):
        on_ready_message = 'Logged in as {0} ({0.id})'.format(self.bot.user)
        print('-'*len(on_ready_message))
        print(on_ready_message)
        print('-'*len(on_ready_message))
        # TODO: check for users without a profile
        users = self.bot.get_cog('users')
        #print(users)
        
        
        await self.bot.db.execute("CREATE TABLE IF NOT EXISTS users(id bigint PRIMARY KEY, discord_id bigint DEFAULT NULL, name text DEFAULT NULL);")
        
        for guild in self.bot.guilds:
            table_name = guild.name + '_' + str(guild.id)
            table_name = table_name.replace(' ','_')
            print(table_name)

            await self.bot.db.execute("CREATE TABLE IF NOT EXISTS guild_%s(id bigint PRIMARY KEY, discord_id bigint DEFAULT NULL, name text DEFAULT NULL);"%table_name)


        if users is not None:
            users.update_all(self.bot.guilds)

           # print(users.load_defaults('settings'))