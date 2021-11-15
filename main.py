#!/bin/python3
import discord
import json
import random
from discord.ext import commands,tasks
from requests import get
from discord.ext.commands import CommandNotFound
import os
# Get Token
with open("token.txt") as file:
    token = file.read()

max = 15000 # Max storage (Free)
premium = 35000 # Max storage (Premium)
color = 0x63615b # Embed color


bot = commands.Bot(command_prefix=".",case_insensitive=True) # define bot
bot.remove_command("help") #remove help command

#Ignore command not found
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    else:
        return

# Help command
@bot.command()
async def help(ctx):
    if ctx.guild.id == 871118468043399169:
        invitemenu = discord.Embed(title="Invite Me",description="Click [here](https://discord.com/api/oauth2/authorize?client_id=871118080753954836&permissions=52224&scope=bot) to invite me to your own server",color=color)
        await ctx.send(embed=invitemenu)
        return
    else:
        helpmenu = discord.Embed(title="Help",color=color)
        helpmenu.add_field(name="`.add [line type]`",value="Add lines to a line type in the storage. You can use this with a txt file or with a paste site link.",inline=False)
        helpmenu.add_field(name="`.remove [line type]`",value="Removes a line type from the storage",inline=False)
        helpmenu.add_field(name="`.clear [line type]`",value="Cleares a line type in the storage",inline=False)
        helpmenu.add_field(name="`.get [line type]` or `.gen [line type]`",value="Get a line from a line type in the storage",inline=False)
        helpmenu.add_field(name="`.stock` or `.types`",value="See the line types in the storage",inline=False)
        helpmenu.add_field(name="`.showstock [line type]` or `.showlines [line type]`",value="Sends the lines in a linetype as a file",inline=False)
        helpmenu.add_field(name="`.channel [channel]`",value="Change the gen channel",inline=False)
        helpmenu.add_field(name="`.invite`",value="Shows the invite link for the bot",inline=False)
        helpmenu.description = "For support, join the discord [here](https://discord.gg/gcNSHzhR2h)"
        await ctx.send(embed=helpmenu)

# Channel command
@bot.command()
async def channel(ctx,ch:discord.TextChannel=None):
    if ctx.guild is None:
        await ctx.send("Cannot run this command in dms!")
        return
    if ctx.guild.id == 871118468043399169:
        return
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send("You need to have `Administator` permission to use this command!")
        return
    with open(f"Guilds/{ctx.guild.id}.json",encoding="utf-8") as file:
        data = json.load(file)
    if ch == None:
        if data["channel"] == 0:
            error = discord.Embed(title="Error",description="No gen channel has been setup! Do `.channel [channel]` to change the gen channel",color=color)
            await ctx.send(embed=error)
        else:
            channel = data["channel"]
            await ctx.send(f"The gen channel is currently: <#{channel}>\n\nChange the gen channel by doing `.channel [channel]`")
    else:
        ch = ch.id
        data["channel"] = ch
        with open(f"Guilds/{ctx.guild.id}.json","w") as file:
            json.dump(data,file,indent=4)
        await ctx.send(f"Gen channel changed to <#{ch}>")
@channel.error # Channel not found
async def channel_error(ctx,error):
    if isinstance(error,commands.errors.ChannelNotFound):
        await ctx.send("Channel not found!")

#Invite
@bot.command()
async def invite(ctx):
    invitemenu = discord.Embed(title="Invite Me",description="Click [here](https://discord.com/api/oauth2/authorize?client_id=871118080753954836&permissions=52224&scope=bot) to invite me to your own server",color=color)
    await ctx.send(embed=invitemenu)

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.guild == None:
        return
    if message.author.id != bot.user.id:
        if str(message.guild.id)+".json" not in os.listdir("Guilds"):
            data = {"services":{},"channel":0,"premium":0}
            with open(f"Guilds/{message.guild.id}.json","w") as file:
                json.dump(data,file,indent=4)
        if message.content.replace("!","") == bot.user.mention or message.content == bot.user.mention:
            await message.channel.send("My prefix is `.`") # Say prefix

@bot.event
async def on_guild_join(guild):
    data = {"services":{},"channel":0,"premium":0}
    with open(f"Guilds/{guild.id}.json","w") as file:
        json.dump(data,file,indent=4)

@bot.event
async def on_guild_remove(guild):
    os.remove(f"Guilds/{guild.id}.json")

# ON ready
@bot.event
async def on_ready():
    print(bot.user.mention)
    status.start()

#Status
@tasks.loop(seconds=30)
async def status():
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} servers use my storage!"))

# gen command
@bot.command(aliases=['get'])
async def gen(ctx,name=None):
    if ctx.guild is None:
        await ctx.send("Cannot run this command in dms!")
        return
    if ctx.guild.id == 871118468043399169:
        return
    if name == None:
        error = discord.Embed(title="Error",description="Correct syntax - `.gen [name]` or `.get [name]`\n\n`.stock` or `.types` for the line types",color=color)
        await ctx.send(embed=error)
    else:
        with open(f"Guilds/{ctx.guild.id}.json",encoding="utf-8") as file:
            data = json.load(file)
        if data["channel"] == 0:
            error = discord.Embed(title="Error",description="The gen channel has not been added! Do `.channel [channel]` to add the gen channel",color=color)
            await ctx.send(embed=error)
        else:
            if ctx.channel.id != data["channel"]:
                channel = data["channel"]
                await ctx.send(f"Gen channel is <#{channel}>",delete_after=5)
            else:
                name = name.lower()
                if data["services"] == {}:
                    error = discord.Embed(title="Error",description="I have no line types! Do `.help` for some help",color=color)
                    await ctx.send(embed=error)
                else:
                    if name not in data["services"]:
                        error = discord.Embed(title="Error",description="Line type not found!\n\n`.stock` or `.types` for the line types",color=color)
                        await ctx.send(embed=error)
                    else:
                        account = random.choice(data["services"][name])
                        try:
                            accountmenu = discord.Embed(title=name.capitalize()+" Line",description=account,color=color)
                            accountmenu.set_footer(text="This message will delete in 2 minutes")
                            msg = await ctx.author.send(embed=accountmenu,delete_after=120)
                        except:
                            error = discord.Embed(title="Error",description="Your dms are not open. I cant send you messages!\nTry turning on this setting, and then running the command again.",color=color)
                            error.set_image(url="https://i.imgur.com/6limCHr.png")
                            await ctx.send(embed=error)
                        else:
                            data["services"][name].remove(account)
                            with open(f"Guilds/{ctx.guild.id}.json","w") as file:
                                json.dump(data,file,indent=4)
                            success = discord.Embed(title="Lines Sent",description=f"I sent you a line from my storage!\nClick [here]({msg.jump_url}) to jump to the message",color=color)
                            await ctx.send(embed=success)                  

# add command
@bot.command()
async def add(ctx,service=None,link=None):
    if ctx.guild is None:
        await ctx.send("Cannot run this command in dms!")
        return
    if ctx.guild.id == 871118468043399169:
        return
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send("You need to have `Administator` permission to use this command!")
        return
    if service == None:
        error = discord.Embed(title="Error",description="Correct syntax:\n\n`.add [name]`\n(Required .txt file)\n\n`.add [name] [link]`",color=color)
        await ctx.send(embed=error)
        return
    else:
        service = service.lower()
        if link != None:
            if "paste.ee/" in link:
                link = link.split("paste.ee")[1].replace("/p/","/r/")
                a = get("https://paste.ee"+link)
                if a.status_code != 200:
                    error = discord.Embed(title="Error",description="Server connection failed!\nTry again in a few minutes",color=color)
                    await ctx.send(embed=error)
                else:
                    a = a.text.splitlines()
                    with open(f"Guilds/{ctx.guild.id}.json",encoding="utf-8") as file:
                        data = json.load(file)
                    try:
                        data["services"][service]
                    except:
                        data["services"][service] = []
                    added = 0
                    for account in a:
                        if len(account) > 500:
                            pass
                        if account == "":
                            pass
                        else:
                            if data["premium"] == 0:
                                total = 0
                                for service in data["services"]:
                                    total += len(data["services"][service])
                                if total > max-1:
                                    pass
                                else:
                                    added += 1
                                    data["services"][service].append(account)
                            if data["premium"] == 1:
                                total = 0
                                for service in data["services"]:
                                    total += len(data["services"][service])
                                if total > premium-1:
                                    pass
                                else:
                                    added += 1
                                    data["services"][service].append(account)
                    with open(f"Guilds/{ctx.guild.id}.json","w") as file:
                        json.dump(data,file,indent=4)
                    if added == 0:
                        success = discord.Embed(title="No Lines Added",description=f"Max storage reached!\n\nTo get more storage, join the discord [here](https://discord.gg/gcNSHzhR2h)",color=color)
                    else:
                        success = discord.Embed(title="Lines Added",description=f"Lines added - {added}\n\nCheck new stock with `.stock`",color=color)
                    await ctx.send(embed=success)
            elif "ghostbin.com/" in link:
                link = link.split("ghostbin.com")[1]
                a = get("https://ghostbin.com"+link)
                if a.status_code != 200:
                    error = discord.Embed(title="Error",description="Server connection failed!\nTry again in a few minutes",color=color)
                    await ctx.send(embed=error)
                else:
                    a = a.text.split('<textarea class="form-control" id="paste" name="paste" disabled>')[1].split('</textarea>')[0].splitlines()
                    with open(f"Guilds/{ctx.guild.id}.json",encoding="utf-8") as file:
                        data = json.load(file)
                    try:
                        data["services"][service]
                    except:
                        data["services"][service] = []
                    added = 0
                    for account in a:
                        if len(account) > 500:
                            pass
                        if account == "":
                            pass
                        else:
                            if data["premium"] == 0:
                                total = 0
                                for service in data["services"]:
                                    total += len(data["services"][service])
                                if total > max-1:
                                    pass
                                else:
                                    added += 1
                                    data["services"][service].append(account)
                            if data["premium"] == 1:
                                total = 0
                                for service in data["services"]:
                                    total += len(data["services"][service])
                                if total > premium-1:
                                    pass
                                else:
                                    added += 1
                                    data["services"][service].append(account)
                    with open(f"Guilds/{ctx.guild.id}.json","w") as file:
                        json.dump(data,file,indent=4)
                    if added == 0:
                        success = discord.Embed(title="No Lines Added",description=f"Max storage reached!\n\nTo get more storage, join the discord [here](https://discord.gg/gcNSHzhR2h)",color=color)
                    else:
                        success = discord.Embed(title="Lines Added",description=f"Lines added - {added}\n\nCheck new stock with `.stock`",color=color)
                    await ctx.send(embed=success)
            else:
                error = discord.Embed(title="Error",description="Paste site not added yet!\n\nList of supported sites:\n[https://paste.ee](https://paste.ee)\n[https://ghostbin](https://ghostbin.com)",color=color)
                await ctx.send(embed=error)
        else:
            if str(ctx.message.attachments) != "[]":
                url = str(ctx.message.attachments).split("url=")[1].replace("'","").replace(">","").replace("]","")
                a = get(url)
                if a.status_code != 200:
                    error = discord.Embed(title="Error",description="Server connection failed!\nTry again in a few minutes",color=color)
                    await ctx.send(embed=error)
                else:
                    a = a.text.splitlines()
                    with open(f"Guilds/{ctx.guild.id}.json",encoding="utf-8") as file:
                        data = json.load(file)
                    try:
                        data["services"][service]
                    except:
                        data["services"][service] = []
                    added = 0
                    for account in a:
                        if len(account) > 500:
                            pass
                        if account == "":
                            pass
                        else:
                            if data["premium"] == 0:
                                total = 0
                                for service in data["services"]:
                                    total += len(data["services"][service])
                                if total > max-1:
                                    pass
                                else:
                                    added += 1
                                    data["services"][service].append(account)
                            if data["premium"] == 1:
                                total = 0
                                for service in data["services"]:
                                    total += len(data["services"][service])
                                if total > premium-1:
                                    pass
                                else:
                                    added += 1
                                    data["services"][service].append(account)
                    with open(f"Guilds/{ctx.guild.id}.json","w") as file:
                        json.dump(data,file,indent=4)
                    if added == 0:
                        success = discord.Embed(title="No Lines Added",description=f"Max storage reached!\n\nTo get more storage, join the discord [here](https://discord.gg/gcNSHzhR2h)",color=color)
                    else:
                        success = discord.Embed(title="Lines Added",description=f"Lines added - {added}\n\nCheck new stock with `.stock`",color=color)
                    await ctx.send(embed=success)
            else:
                error = discord.Embed(title="Error",description="Correct syntax:\n\n`.add [name]`\n(Required .txt file)\n\n`.add [name] [link]`",color=color)
                await ctx.send(embed=error)

#clear command
@bot.command()
async def clear(ctx,service=None):
    if ctx.guild is None:
        await ctx.send("Cannot run this command in dms!")
        return
    if ctx.guild.id == 871118468043399169:
        return
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send("You need to have `Administator` permission to use this command!")
        return
    if service == None:
        error = discord.Embed(title="Error",description="Correct syntax - `.clear [name]`",color=color)
        await ctx.send(embed=error)
    else:
        service = service.lower()
        try:
            with open(f"Guilds/{ctx.guild.id}.json",encoding="utf-8") as file:
                data = json.load(file)
            data["services"][service].clear()
            with open(f"Guilds/{ctx.guild.id}.json","w") as file:
                json.dump(data,file,indent=4)
            success = discord.Embed(title="Line Type Cleared",description="Line type cleared\n\nCheck new stock with `.stock`",color=color)
            await ctx.send(embed=success)
        except:
            error = discord.Embed(title="Error",description="Line type does not exist!",color=color)
            await ctx.send(embed=error)

#remove command
@bot.command()
async def remove(ctx,service=None):
    if ctx.guild is None:
        await ctx.send("Cannot run this command in dms!")
        return
    if ctx.guild.id == 871118468043399169:
        return
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send("You need to have `Administator` permission to use this command!")
        return
    if service == None:
        error = discord.Embed(title="Error",description="Correct syntax - `.remove [name]`",color=color)
        await ctx.send(embed=error)
    else:
        service = service.lower()
        try:
            with open(f"Guilds/{ctx.guild.id}.json",encoding="utf-8") as file:
                data = json.load(file)
            data["services"].pop(service)
            with open(f"Guilds/{ctx.guild.id}.json","w") as file:
                json.dump(data,file,indent=4)
            success = discord.Embed(title="Line Type Removed",description="Line type removed\n\nCheck new stock with `.stock`",color=color)
            await ctx.send(embed=success)
        except:
            error = discord.Embed(title="Error",description="Line type does not exist!",color=color)
            await ctx.send(embed=error)

# stock command
@bot.command(aliases=['types'])
async def stock(ctx):
    if ctx.guild is None:
        await ctx.send("Cannot run this command in dms!")
        return
    if ctx.guild.id == 871118468043399169:
        return
    with open(f"Guilds/{ctx.guild.id}.json",encoding="utf-8") as file:
        data = json.load(file)["services"]
    with open(f"Guilds/{ctx.guild.id}.json",encoding="utf-8") as file:
        other = json.load(file)
    stock = discord.Embed(title="Line Types",description="",color=color)
    total = 0
    for service in data:
        accounts = len(data[service])
        total += accounts
        stock.description += f"{service.capitalize()} - {accounts}\n"
    if stock.description != "":
        if other["premium"] == 0:
            percent = round(total/max*100,2)
            stock.description += f"\nStorage - {total}/{max} - {percent}%"
            if percent > 75:
                stock.description += "\nTo get more storage, join the discord [here](https://discord.gg/gcNSHzhR2h)"
        if other["premium"] == 1:
            percent = round(total/premium*100,2)
            stock.description += f"\nStorage - {total}/{premium} - {percent}%"
    if stock.description == "":
        stock.description = "I have no lines types in my storage for this server."
    await ctx.send(embed=stock)

@bot.command(aliases=['showlines'])
async def showstock(ctx,service=None):
    if ctx.guild is None:
        await ctx.send("Cannot run this command in dms!")
        return
    if ctx.guild.id == 871118468043399169:
        return
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send("You need to have `Administator` permission to use this command!")
        return
    with open(f"Guilds/{ctx.guild.id}.json",encoding="utf-8") as file:
        data = json.load(file)
    if service == None:
        error = discord.Embed(title="Error",description="Correct syntax - `.showstock [name]` or `showlines [name]`",color=color)
        await ctx.send(embed=error)
    else:
        service=service.lower()
        try:
            accounts = data["services"][service]
        except:
            error = discord.Embed(title="Error",description="Line type does not exist!\n\nDo `.stock` to show the available line types",color=color)
            await ctx.send(embed=error)
        else:
            with open(str(ctx.guild.id)+".txt","a+",encoding="utf-8") as file:
                for account in accounts:
                    try:
                        file.write(account+"\n")
                    except:
                        pass
            await ctx.send(file=discord.File(str(ctx.guild.id)+".txt",filename=service.capitalize()+"_stock.txt"))  
            os.remove(str(ctx.guild.id)+".txt") 
bot.run(token)
