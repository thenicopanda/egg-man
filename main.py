# Things of note:
# Change guild id on line 48
# Change Normal Leaderboard id on line 51
# Chnage Soul Leaderboard id on line 98


# Imports
import discord, random, re
from discord.ext import commands, tasks
from discord.utils import get
import tools as t
from decimal import Decimal
from math import ceil
from datetime import datetime


# Config Variables
gameList = t.load("displayGame") # List of games to cycle through


bot = commands.Bot(command_prefix=t.botPrefix,
                   description=t.botName,
                   case_insensitive=True)


if __name__ == '__main__':
    bot.remove_command('help')
    bot.load_extension('cogs.egg')


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online)
    print("Successfully logged in and booted... Now go fix some bugs!")
    if not changeStatus.is_running():
        changeStatus.start()


@bot.event
async def on_member_remove(member):
    print(f"Delete {member} asap")


@tasks.loop(minutes=5)
async def changeStatus():
    """Update the leaderboard and change the bot game every 7 minutes"""
    t.updateAllUsers()
    guild = bot.get_guild(944489070577471499)
    await bot.change_presence(activity=discord.Game("Updating Board(s)"))

    leaderboardChannel = bot.get_channel(944490623614996510) # Get the #leaderboard channel
    messages = await leaderboardChannel.history(limit=10).flatten()
    currentMessages = int( len( messages ) )

    sortedLeaderboard = t.updateLeaderboard() # Collect the current leaderboard stats
    messagesNeeded = int( ceil( len( sortedLeaderboard ) / 25 ) )

    messageCount = 0
    while messageCount != 1:
        if currentMessages == messagesNeeded: 
            messageCount = 1
        elif currentMessages < messagesNeeded: 
            await leaderboardChannel.send("⠀")
            currentMessages += 1
        elif currentMessages > messagesNeeded: 
            await messages[-1].delete()
        messages = await leaderboardChannel.history(limit=10).flatten()
    messages = await leaderboardChannel.history(limit=10).flatten()
    messages.reverse()
    countingNumber = 0 # Counting number for place values on leaderboard
    embedLimitCounter = 0 # Limit counter to avoid accidentlly adding too many fields to the embed
    messageCounter = 0
    initialLeaderboardEmbed = discord.Embed(title = "Leaderboard", color=0xb3e4f4) # Create the leaderboard embed

    for x in sortedLeaderboard: # For person in the leaderboard
        countingNumber += 1 # Add one to the Counting Number
        embedLimitCounter += 1 # Add one to the Embed Limit Number
        if embedLimitCounter == 26: # If there are 25 fields on the embed already
            await messages[messageCounter].edit(embed=initialLeaderboardEmbed) # Send the first embed
            embedLimitCounter = 0 # Reset the embed limit
            messageCounter += 1
            initialLeaderboardEmbed = discord.Embed(color=0xb3e4f4) # Create a new leaderboard embed
        try: 
            member = await guild.fetch_member(x["discord"])
            
            role = get(guild.roles, name=x['rank'])
            await member.add_roles(role, reason="Leaderboard Update.")
        except:
            print(f"Could not give role '{x['rank']}' to {x['discord']}")
        eb = t.human_format(Decimal(x["eb"]))
        display = re.sub("[\(\[].*?[\)\]]", "", member.display_name)
        embedTitle = "{}. {}".format(countingNumber, display) # Set the title of the embed field
        initialLeaderboardEmbed.add_field(name=embedTitle, value=f"{eb}%\n - *{x['pe']} Prophecy Eggs*", inline=False) # add the field to the embed
    initialLeaderboardEmbed.timestamp = datetime.now()
    await messages[messageCounter].edit(embed=initialLeaderboardEmbed) # send any leftover embeds


    soulLeaderboardChannel = bot.get_channel(944490669911736360) # Get the #leaderboard channel
    messages = await soulLeaderboardChannel.history(limit=10).flatten()
    currentMessages = int( len( messages ) )

    sortedSoulLeaderboard = t.updateSoulLeaderboard() # Collect the current leaderboard stats

    messagesNeeded = int( ceil( len( sortedSoulLeaderboard ) / 25 ) )

    messageCount = 0
    while messageCount != 1:
        if currentMessages == messagesNeeded: 
            messageCount = 1
        elif currentMessages < messagesNeeded: 
            await soulLeaderboardChannel.send("⠀")
            currentMessages += 1
        elif currentMessages > messagesNeeded: 
            await messages[-1].delete()
        messages = await soulLeaderboardChannel.history(limit=10).flatten()
    messages = await soulLeaderboardChannel.history(limit=10).flatten()
    messages.reverse()

    countingNumber = 0 # Counting number for place values on leaderboard
    embedLimitCounter = 0 # Limit counter to avoid accidentlly adding too many fields to the embed
    messageCounter = 0
    initialSoulLeaderboardEmbed = discord.Embed(title = "Soul Egg Leaderboard", color=0xb3e4f4) # Create the leaderboard embed
    for x in sortedSoulLeaderboard: # For person in the leaderboard
        countingNumber += 1 # Add one to the Counting Number
        embedLimitCounter += 1 # Add one to the Embed Limit Number
        if embedLimitCounter == 26: # If there are 25 fields on the embed already
            await messages[messageCounter].edit(embed=initialSoulLeaderboardEmbed) # Send the first embed
            embedLimitCounter = 0 # Reset the embed limit
            messageCounter += 1
            initialSoulLeaderboardEmbed = discord.Embed(color=0xb3e4f4) # Create a new leaderboard embed
        try: 
            member = await guild.fetch_member(x["discord"])
        except:
            pass
        soulEggs = t.human_format(Decimal(x["soulEggs"]))
        display = re.sub("[\(\[].*?[\)\]]", "", member.display_name)
        embedTitle = "{}. {}".format(countingNumber, display) # Set the title of the embed field
        initialSoulLeaderboardEmbed.add_field(name=embedTitle, value=f"{soulEggs} Soul Eggs", inline=False) # add the field to the embed
        initialSoulLeaderboardEmbed.timestamp = datetime.now()
    await messages[messageCounter].edit(embed=initialSoulLeaderboardEmbed) # send any leftover embeds
    
    await bot.change_presence(activity=discord.Game(random.choice(gameList)))


bot.run(t.load("leaderboardToken"))
