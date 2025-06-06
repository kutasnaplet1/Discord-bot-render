import discord
from discord.ext import commands
import os
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Discord Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
MODERATORS = set()

@bot.event
async def on_ready():
    print(f'Bot online: {bot.user}')

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="Brak powodu"):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Brak uprawnień!")
        return
    try:
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} zbanowany")
    except:
        await ctx.send("Błąd banowania")

@bot.command()
async def mute(ctx, member: discord.Member, *, reason="Brak powodu"):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Brak uprawnień!")
        return
    try:
        from datetime import datetime, timedelta
        until = datetime.now() + timedelta(minutes=10)
        await member.timeout(until, reason=reason)
        await ctx.send(f"{member.mention} wyciszony")
    except:
        await ctx.send("Błąd wyciszenia")

@bot.command()
async def clear(ctx, amount: int = 5):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Brak uprawnień!")
        return
    try:
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"Usunięto {len(deleted) - 1} wiadomości", delete_after=3)
    except:
        await ctx.send("Błąd usuwania")

@bot.command()
async def addmod(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("Tylko właściciel!")
        return
    MODERATORS.add(member.id)
    await ctx.send(f"{member.mention} jest moderatorem")

@bot.command()
async def szynszyl(ctx):
    import random
    choices = ["tosterze", "panierce", "pralce"]
    result = random.choice(choices)
    await ctx.send(f"Szynszyl w {result}!")

@bot.command()
async def kostka(ctx):
    import random
    result = random.randint(1, 6)
    await ctx.send(f"Kostka: {result}")

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
