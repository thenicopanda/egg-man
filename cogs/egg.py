"""
############################################################################################
 Commands
 * ecalc      - Calculate a hypothetical EB based on input.
 * update     - Force the leaderboard to update right away.
 * addaccount - Add an EID to your account.
############################################################################################
"""
adminCommandPermList = [822066927400517632, 958777642931351612]
#                       B1llyGoat           Alex (me)

# Imports
import discord
from discord.ext import commands
import tools as t
from discord.commands import Option



class Egg(commands.Cog, name="Egg Server Functions"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='ecalc', guild_ids=[944489070577471499])
    async def ecalc(self,
                    ctx,
                    souleggs: Option(str, "How many Soul Eggs?"),
                    prophecyeggs: Option(int, "How many Prophecy Eggs?"),
                    prophecybonus: Option(int, "How many Prophecy Bonus levels? (Ingame max is 5 at the moment)", required = False, default = 5),
                    soulfood: Option(int, "How many Soul Food levels? (Ingame max is 140 at the moment)", required = False, default = 140),
                    humanreadable: Option(bool, "True for preformatted, False for exact numbers", required = False, default = True, options = [True, False])
                    ):
        """Calculate EB based on values you enter."""
        souleggs = t.formatLargeNumber(souleggs)
        results = t.calculateEB(souleggs, prophecyeggs, prophecybonus, soulfood, humanreadable)
        if results == False:
            await ctx.respond(f"Something went wrong when calculating...```Soul Eggs: {souleggs}\nProphecy Eggs: {prophecyeggs}\nProphecy Bonus: {prophecybonus}\nSoul Food: {soulfood}```")
        elif results == "E1":
            await ctx.respond("Must enter 1 or more Soul Eggs.")
        else:
            messageToSend = f"Results:```Soul Eggs: {souleggs}\nProphecy Eggs: {prophecyeggs}\nProphecy Bonus: {prophecybonus}\nSoul Food: {soulfood}\n\nEarnings Bonus: {results}%```"
            await ctx.respond(messageToSend)

    @commands.slash_command(name='addaccount', guild_ids=[944489070577471499])
    async def addAccount(self, ctx, eid: Option(str, "What is your EID")):
        """Add an Egg, Inc. account."""
        msg = await ctx.send("Working...")
        result = t.addAccount(eid, ctx.author.display_name, ctx.author.id)
        if result == True:
            await msg.edit(f"Account added. {ctx.author.mention}")
        else:
            print(f"EID could not be added: {eid}")
            await msg.edit(f"Something went wrong. {ctx.author.mention}")

    @commands.slash_command(name="deleteaccount", guild_ids=[944489070577471499])
    async def deleteaccount(self, ctx, eid: Option(str, "Egg, Inc. account to delete")):
        results = t.deleteAccount(eid, ctx.author.id)
        if results == True:
            await ctx.respond("Account deleted successfully")
        else:
            await ctx.respond("You either do not have permission to delete this account or it does not exist. Please double check the EID used.")

    @commands.slash_command(name='userstatus', guild_ids=[944489070577471499])
    async def userstatus(self, ctx):
        """Check what accounts are linked to you."""
        results = t.searchByDiscordID(ctx.author.id)
        baseMsg = f"Accounts for {ctx.author.mention}:\n"
        msg = ""
        for eid, contents in results.items():
            eb = t.calculateEB(contents["soulEggs"], contents["prophecyEggs"], contents["prophecyBonus"], contents["soulFood"], True)
            msg += f"> {eid} - {eb}%\n"
        if msg == "":
            await ctx.respond(f"No accounts found for {ctx.author.mention}")
        else:
            await ctx.respond(f"{baseMsg} {msg}")

    @commands.slash_command(name='admin', guild_ids=[944489070577471499])
    async def admincommand(self, 
                           ctx, 
                           which: Option(str, "What would you like to do?", choices=["userstatus", "deleteaccount", "addaccount"]),
                           user: Option(discord.User, "Who are you running the command as?", required = True),
                           eid: Option(str, "What is the EID to adjust? (Not needed for userstatus)", required = False, default = False)):
        """Run commands in the name of another user."""
        if ctx.author.id in adminCommandPermList:
            if which == "userstatus":
                        results = t.searchByDiscordID(user.id)
                        baseMsg = f"Accounts for {user.display_name}:\n"
                        msg = ""
                        for eid, contents in results.items():
                            eb = t.calculateEB(contents["soulEggs"], contents["prophecyEggs"], contents["prophecyBonus"], contents["soulFood"], True)
                            msg += f"> {eid} - {eb}%\n"
                        if msg == "":
                            await ctx.respond(f"No accounts found for {user.display_name}")
                        else:
                            await ctx.respond(f"{baseMsg} {msg}")
            elif which == "deleteaccount":
                results = t.deleteAccount(eid, user.id)
                if results == True:
                    await ctx.respond(f"Account deleted for {user.display_name} successfully")
                else:
                    await ctx.respond("Either something went wrong or this EID is not in use. Please double check the EID used and make sure it belongs to the account mentioned.")
            elif which == "addaccount":
                msg = await ctx.send("Working...")
                result = t.addAccount(eid, user.display_name, user.id)
                if result == True:
                    await msg.edit(f"Account added for {user.display_name}. {ctx.author.mention}")
                else:
                    print(f"EID could not be added: {eid}")
                    await msg.edit(f"Something went wrong. {ctx.author.mention}")
        else: 
            await ctx.respond("You do not have permission to use this command. If this is an error please ping B1llyG0at or Alex.")


def setup(bot):
    bot.add_cog(Egg(bot))
