from discord.ext import commands
import os
import sys
sys.path.append('functions')
import discord
import profile_fun as pf

class users(commands.Cog):
    def __init__(self, bot):
        print('Cog Loaded: users')
        self.bot = bot
        
        
        
    @commands.command()
    async def users_test(self,ctx):
        """Re-enables Mr. O's playing intro songs."""
        await ctx.send('Users work')
        
    @commands.command()  
    async def reset_profile(self,ctx):
        # TODO: Resets the profile for a member to
        #       the default profile
        dic = {'user_name':ctx.author.name,'guild_name':ctx.author.guild.name}
        print('Reseting profile for {user_name} in {guild_name}'.format(**dic))

        await self.delete_user(ctx.guild,ctx.author)
        await self.generate_user(ctx.guild,ctx.author)
        
    @commands.command()  
    async def test_update(self,ctx):
        # TODO: Resets the profile for a member to
        #       the default profile
        await self.bot.db.execute("UPDATE users SET default_nickname = 'changed name' WHERE guild_id = %d AND user_id = %d;"%(ctx.guild.id,ctx.author.id))
    
    @commands.command()
    async def default_nickname(self, ctx, nickname, playerID=None):
        member = pf.find_member(ctx.author.guild,ctx,playerID)
        oldNickname = await self.pull_value(ctx.author.guild,member,'default_nickname')
        await self.set_value(ctx.author.guild,member,'default_nickname',nickname)
        await ctx.send('Default Nickname set from %s to %s for %s'%(oldNickname,nickname,member.name))    
    
    @commands.command()
    async def reset_nickname(self, ctx, playerID=None):
        member = pf.find_member(ctx.author.guild,ctx,playerID)
        print(member,type(member))
        oldNickname = await self.pull_value(ctx.author.guild,member,'default_nickname')
        await member.edit(nick=str(oldNickname))
        await ctx.send('Nickname reset to %s for %s'%(oldNickname,member.name))
        
    @commands.command()
    async def volume(self, ctx,volume: float,playerID=None):
        member = pf.find_member(ctx.author.guild,ctx,playerID)
        oldVolume = await self.pull_value(ctx.author.guild,member,'volume')
        await self.set_value(ctx.author.guild,member,'volume',volume)
        await ctx.send('Volume set from %0.3f to %0.3f for %s'%(oldVolume,volume,member.name))
        
    @commands.command()
    async def length(self, ctx,length: float,playerID=None):
        member = pf.find_member(ctx.author.guild,ctx,playerID)
        oldLength = await self.pull_value(ctx.author.guild,member,'length')
        await self.set_value(ctx.author.guild,member,'length',length)
        await ctx.send('Length set from %0.3f to %0.3f for %s'%(oldLength,length,member.name))
        
    @commands.command()
    async def solo_play(self,ctx,playerID=None):
        member = pf.find_member(ctx.author.guild,ctx,playerID)
        val = await self.pull_value(ctx.author.guild,member,'solo_play')
        await self.set_value(ctx.author.guild,member,'solo_play',val==0)
        
    @commands.command()
    async def unify_settings(self,ctx,playerID=None):
        member = pf.find_member(ctx.author.guild,ctx,playerID)

        mainRow = await self.bot.db.fetchrow("SELECT * FROM users WHERE guild_id = %d AND user_id = %d"%(ctx.author.guild.id,member.id))

        allRow = await self.bot.db.fetch("SELECT * FROM users WHERE user_id = %d"%(member.id))

        for row in allRow:
            for key in dict(row):
                if key not in ('id','guild_name','guild_id','user_id','user_name','superuser','ban','ban_count'):
                    guild = discord.utils.find(lambda g: g.id == row['guild_id'],self.bot.guilds)
                    await self.set_value(guild,member,key,mainRow[key])

            
    @commands.command()
    async def settings(self,ctx,playerID=None):
        member = pf.find_member(ctx.author.guild,ctx,playerID)
        settings = await self.pull_user(ctx.author.guild,member)
        print(settings)
        string = '```\nSettings for %s on %s\n'%(ctx.author.name,ctx.author.guild)
        maxKey = 0
        for key in dict(settings):
            curKey = len(key)
            
            if curKey > maxKey:
                maxKey = curKey
                
        for key in dict(settings):
            curKey = len(key)
            string += ' '*(maxKey-curKey) + key + ':  ' + str(settings[key]) + '\n'
        string += '```'
        
        await ctx.author.send(string)
        #await self.set_value(ctx.author.guild,member,'solo_play',val==0)
        
    async def set_value(self,guild,member,key,value):
        dic = {'guild_id':guild.id,'user_id':member.id,'key':key,'value':value,'user_name':member.name,'guild_name':guild.name}
        print('Set {key} for {user_name} in {guild_name} to {value}'.format(**dic))
        if type(dic['value']) == str:
            await self.bot.db.execute("UPDATE users SET {key} = '{value}' WHERE guild_id = {guild_id} AND user_id = {user_id};".format(**dic))
        else:
            await self.bot.db.execute("UPDATE users SET {key} = {value} WHERE guild_id = {guild_id} AND user_id = {user_id};".format(**dic))

    async def pull_value(self,guild,member,key):
        testRow = await self.bot.db.fetchval("SELECT %s FROM users WHERE guild_id = %d AND user_id = %d"%(key,guild.id,member.id))
        return testRow
        
    async def pull_user(self,guild,member):
        testRow = await self.bot.db.fetchrow("SELECT * FROM users WHERE guild_id = %d AND user_id = %d"%(guild.id,member.id))

        return testRow
        
    async def delete_user(self,guild,member):
        await self.bot.db.execute("DELETE FROM users WHERE user_id = %d AND guild_id = %d;"%(member.id,guild.id))

    async def generate_user(self,guild,member):
        print('Adding User %s to Guild %s'%(member.name,guild.name))

        await self.bot.db.execute("INSERT INTO users (guild_name, guild_id,user_id,user_name) VALUES ('%s', %d, %d, '%s');"%(guild.name,guild.id,member.id,member.name))

    async def check_member(self,guild,member):
        # TODO: Code to update individual profile 
        #       in a specific guild.
        #       Needs to add any new settings while
        #       not affecting existing settings
        testRow = await self.bot.db.fetch("SELECT * FROM users WHERE guild_id = %d AND user_id = %d"%(guild.id,member.id))
        if len(testRow) == 0:
            await self.generate_user(guild,member)       

    async def check_guild(self,guild):
        for member in guild.members:
            await self.check_member(guild,member) 

    async def check_all(self,guild_list):
        for guild in guild_list:
            await self.check_guild(guild)


    def load_defaults(self, directory=None):
        if directory == None:
            path = 'user_defaults.ini'
        else:
            path = directory + '/user_defaults.ini'

        if os.path.exists(path):
            with open(path,'r') as f:
                content = f.readlines()
            
            
            content = [x.strip().replace('\t','').replace(' ','')  for x in content] 
            dic = {}
            for line in content:
                if len(line) > 0:
                    a = line.split('=')
                    varname = a[0]
                    vartype = a[1].split(':')[0]
                    varval = a[1].split(':')[1]
                    


                    if vartype == 'BOOL':
                        dic[a[0]] = ('BOOL',bool(int(varval)))
                    elif vartype == 'TEXT':
                        dic[a[0]] = ('TEXT',varval.replace('"',"'"))
                    elif vartype == 'FLOAT':
                        dic[a[0]] = ('FLOAT',float(varval))
                    elif vartype == 'BIGINT':
                        dic[a[0]] = ('BIGINT',int(varval))
                    else:
                        try:
                            dic[a[0]] = ('BIGINT',int(varval))
                        except ValueError:
                            dic[a[0]] = ('TEXT',str(varval))
                    
            return dic
        else:
            return {}    
        