import discord
from discord.ext import commands
import music

cogs = [music]
commands_prefix= ['.','/']
client = commands.Bot(command_prefix=commands_prefix, intents = discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client)

client.run("OTg5OTE2ODE3NjYzMzUyODY0.GeHiQf.fMlyVetqQX4Q_aU576prrBiH21nopo4Nyyo4aM")