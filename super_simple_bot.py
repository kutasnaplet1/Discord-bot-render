import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot online: {bot.user}')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def test(ctx):
    await ctx.send('Bot działa!')

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="Brak powodu"):
    if ctx.author.id == ctx.guild.owner_id:
        try:
            await member.ban(reason=reason)
            await ctx.send(f"{member.mention} zbanowany")
        except:
            await ctx.send("Błąd banowania")
    else:
        await ctx.send("Brak uprawnień")

@bot.command()
async def clear(ctx, amount: int = 5):
    if ctx.author.id == ctx.guild.owner_id:
        try:
            await ctx.channel.purge(limit=amount + 1)
            await ctx.send(f"Usunięto {amount} wiadomości", delete_after=3)
        except:
            await ctx.send("Błąd usuwania")
    else:
        await ctx.send("Brak uprawnień")

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
