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
        guilds = self.bot.get_cog('guilds')

        #print(users)
        print(users)
        if users is not None:
            print(os.getcwd())


                
          #  await self.bot.db.execute('DROP TABLE IF EXISTS users;')
          #  await self.bot.db.execute('DROP TABLE IF EXISTS guild;')

            user_default = users.load_defaults(directory='settings')
            user_string = await self.build_table(table_name = 'users',settings = user_default)


          #  await self.bot.db.execute("INSERT INTO users (guild_id,guild_name,ban) VALUES (10,'thisguild',True);")
           # await self.bot.db.execute("INSERT INTO users (guild_id,guild_name,ban) VALUES (5,'otherguild',False);")


        if guilds is not None:
            guild_default = guilds.load_defaults(directory='settings')
            for guild in self.bot.guilds:
                table_name = 'guild_' +guild.name + '_' + str(guild.id)
                table_name = table_name.replace(' ','_')
                guild_string = await self.build_table(table_name = table_name,settings = guild_default)
            #await self.bot.db.execute("INSERT INTO %s (guild_id,guild_name) VALUES (5,'otherguild');"%table_name)



       # if users is not None:
            #users.update_all(self.bot.guilds)

           # print(users.load_defaults('settings'))
           
           
    async def build_table(self,table_name,settings):
        db_string = "CREATE TABLE IF NOT EXISTS %s(id SERIAL"%table_name
        print('Building table: %s'%table_name)
        for key in settings.keys():
        # print(user_string)
        # user_string += ', %s %s'%(str(key),str(default[key][0]))

            db_string += ', %s %s DEFAULT %s'%(str(key),str(settings[key][0]),str(settings[key][1]))
        db_string += ');'
        await self.bot.db.execute(db_string)
        testRow = await self.bot.db.fetchrow("SELECT * FROM %s"%table_name)
        print(testRow)
        if testRow == None:
            await self.bot.db.execute("INSERT INTO %s DEFAULT VALUES;"%table_name)
            testRow = await self.bot.db.fetchrow("SELECT * FROM %s"%table_name)
        #print(table_name)
        #print(table_name,testRow.keys())
        
        tableKeys = []
        for key in testRow.keys():
            tableKeys.append(key)
        for key in settings.keys():
            if not(key in tableKeys):
                print('Adding column %s to table %s'%(str(key),str(table_name)))
                await self.bot.db.execute("ALTER TABLE %s ADD %s %s DEFAULT %s"%(table_name,str(key),str(settings[key][0]),str(settings[key][1])))
