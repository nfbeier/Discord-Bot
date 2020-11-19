from discord.ext import commands
import os



class users(commands.Cog):
    def __init__(self, bot):
        print('users cog loaded')
        self.bot = bot
        
        
        
    @commands.command()
    async def users_test(self,ctx):
        """Re-enables Mr. O's playing intro songs."""
        await ctx.send('Users work')
        
    def update_member(self,guild,member,update_profile=None):
        # TODO: Code to update individual profile 
        #       in a specific guild.
        #       Needs to add any new settings while
        #       not affecting existing settings
        if update_profile == None:
            update_profile = self.load_defaults
        print(guild,member)
        

    def update_guild(self,guild,member,update_profile=None):
        # TODO: Update all memeber of a single guild
        for member in guild.members:
            self.update_member(guild,member,update_profile) 



    def update_all(self,guild_list,update_profile=None):
        # TODO: Update all members in every guild
        #       associated with the bot.
        for guild in guild_list:
            self.update_guild(guild,update_profile)


    def reset_profile(self,guild,member):
        # TODO: Resets the profile for a member to
        #       the default profile
        temp = 1



    def load_defaults(self, directory=None):
        if directory == None:
            path = 'default_settings.dat'
        else:
            path = directory + '/default_settings.dat'

        if os.path.exists(path):
            with open(path,'r') as f:
                content = f.readlines()
            
            
            content = [x.strip().replace('\t','').replace(' ','')  for x in content] 
            dic = {}
            for line in content:
                if len(line) > 0:
                    a = line.split('=')
                    if a[1] == 'None':
                        dic[a[0]] = None
                    elif '"' in a[1]:
                        print(a[1])
                        dic[a[0]] = a[1].replace('"','')
                    elif '.' in a[1]:
                        dic[a[0]] = float(a[1])
                    else:
                        try:
                            dic[a[0]] = int(a[1])
                        except ValueError:
                            dic[a[0]] = a[1]
                    
            return dic
        else:
            return {}    
        
    def load_settings(self,path=None):
        # TODO: Loads all settings into python dictionary
        if os.path.exists(path):
            print('a')
      

    def create_file(self,path=None):
        if path == None:
            path = 'settings.h5'
        with h5py.File('settings.h5','w') as hf:
            # TODO: add what happens on load
            temp = 1