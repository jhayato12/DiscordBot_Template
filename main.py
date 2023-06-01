import discord
import asyncio
from discord import Guild
from discord.ext import commands, tasks
from discord.ui import Button
from discord.ext.commands import has_permissions, MissingPermissions, MissingRequiredArgument, has_guild_permissions

token = "" # Provide Token for your bot from discord

client = commands.Bot(command_prefix="!", bot=True, intents=discord.Intents.all())
activityMessage = discord.Game("") #provide Game that is being played by the bot

@client.event
async def on_ready():
    print(f"{client.user} is ready")
    await client.change_presence(status=discord.Status.online, activity=activityMessage)

@client.event
async def on_member_join(member):
    guild: Guild = member.guild
    channel = guild.get_channel() #provide channel id of your welcome channel
    await channel.send(f"Welcome {member.mention} to {guild.name}") #Change welcome message on demand

#Commands
@client.tree.command(name="hello", description="Says hello to the user")
async def hello(Interaction: discord.Interaction):
    await Interaction.response.send_message(f'Hello {Interaction.user.mention}!')
## Command hello is the only / command, you can rebuild further commands after this example

#kicking someone from your guild
@client.command(name="kick", aliases = ["Kick"])
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        await ctx.send("You cant kick yourself!")
        return
    if member.guild_permissions.moderate_members:
        await ctx.send("You cant kick a moderator")
        return
    await member.kick(reason=reason)
    if reason != None:
        await ctx.send(f"User {member} has been kicked! Reason: {reason}")
    else:
        await ctx.send(f"User {member} has been kicked from the server!")

#banishing someone from your guild
@client.command(name= "ban", aliases=["Ban", "banish", "Banish"])
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        await ctx.send("You cant banish yourself!")
        return
    if member.guild_permissions.moderate_members:
        await ctx.send("You cant banish a moderator")
        return

    await member.ban(reason=reason)
    if reason != None:
        await ctx.send(f"User{member} has been banished from the server! Reason: {reason}")
    else:
        await ctx.send(f"User{member} has been banished from the server!")

#muting a member of your guild
@client.command(name="mute", aliases=["m", "Mute"])
@commands.has_permissions(mute_members=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        await ctx.send("You cant mute yourself!")
        return
    if member.guild_permissions.moderate_members:
        await ctx.send("You cant mute a moderator")
        return
    if ctx.author != member:
        guild = ctx.guild
        mutedRole = discord.utils.get(guild.roles, name="Muted")
    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False)
    
    if reason != None:
        await ctx.send(f"{member} has been muted in {ctx.guild.name}! Reason: {reason}")
        await member.add_roles(mutedRole, reason=reason)
    else:
        await ctx.send(f"{member} has been muted in {ctx.guild.name}!")
        await member.add_roles(mutedRole, reason=reason)

@client.command(name="tempmute", aliases=["tm"])
@commands.has_permissions(manage_roles=True)
async def tempmute(ctx, member:discord.Member, minutes: int):
    if member == ctx.author:
        await ctx.send("You cant mute yourself!")
        return
    if member.guild_permissions.moderate_members:
        await ctx.send("You cant mute a moderator")
        return
    if ctx.author != member:
        guild = ctx.guild
        mutedRole = discord.utils.get(guild.roles, name="Muted")
    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False)
    
    await member.add_roles(mutedRole)
    await ctx.send(f"{member} has been muted for {minutes} minutes!")
    await asyncio.sleep(minutes)
    await member.remove_roles(mutedRole)
    await ctx.send(f"{member} has been unmuted!")

#unmuting your server members
@client.command(name="unmute", aliases=["um", "Unmute"])
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    if member == ctx.author:
        await ctx.send("You cant unmute yourself!")
        return
    if member.guild_permissions.moderate_members:
        await ctx.send("You cant unmute a moderator")
        return
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

    await member.remove_roles(mutedRole)
    await ctx.send(f"{member} has been unmuted!")

#clears a specific amount of messages in the specific channel
@client.command(name="clear", aliases=["c", "Clear"])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, number=0):
    if number >= 1:
        await ctx.channel.purge(limit=number+1)
    else:
        await ctx.send("Please provide a valid number")

#Embed commands
#avatar command responding with an embed containing the av of the mentioned person
@client.command(name= "avatar", aliases=["av", "Avatar", "Av"])
async def avatar(ctx, member:discord.Member = None):
    if member == None:
        member = ctx.author

    name = member.display_name
    profile_picture = member.display_avatar

    avembed = discord.Embed(title="Avatar")
    avembed.set_author(name=name, icon_url=profile_picture)
    avembed.set_image(url=profile_picture)
    
    await ctx.send(embed=avembed)

#profile command responding with an embed containing informations such as: Discord member since, Discord Id, Guild member since, // continuing to add
@client.command(name="profile", aliases=["pf", "Profile", "Pf"])
async def profile(ctx, member:discord.Member = None):
    if member == None:
        member = ctx.author

    name = member.name
    profile_picture = member.avatar
    memberid = member.id
    discordjoindate = member.created_at.strftime("%d/%m/%y")
    guildjoindate = member.guild.created_at.strftime("%d/%m/%y")

    profileEmbed = discord.Embed(title=f"{name}'s Profile")
    profileEmbed.set_thumbnail(url=profile_picture)
    profileEmbed.add_field(name="Discord member since:", value=discordjoindate)
    profileEmbed.add_field(name="Discord ID:", value=memberid, inline=True)
    profileEmbed.add_field(name="Joined server on: ", value=guildjoindate, inline=False)
    profileEmbed.add_field(name="Server roles:", value="".join([role.mention for role in member.roles]))

    await ctx.send(embed=profileEmbed)

#Errors
@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You dont have permission to kick people")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You missed an argument, please call the function again")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You dont have permission to ban people")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You missed an argument, please call the function again")
@tempmute.error
async def tempmute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You dont have permission to mute people")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You missed an argument, please call the function again")
@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You dont have permission to mute people")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You missed an argument, please call the function again")
@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You dont have permission to mute people")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You missed an argument, please call the function again")
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You dont have permission to clear channels")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You missed an argument, please call the function again")

client.run(token=token)