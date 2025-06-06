import discord
from discord.ext import commands
import os
from flask import Flask
import threading

# Flask keepalive server
app = Flask(__name__)

@app.route('/')
def home():
    return "Discord Bot is running!"

@app.route('/status')
def status():
    return {"status": "online", "bot": str(bot.user) if bot.is_ready() else "connecting"}

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

# Discord bot setup
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
        await ctx.send(f"{member.mention} wyciszony na 10 minut")
    except:
        await ctx.send("Błąd wyciszenia")

@bot.command()
async def unmute(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Brak uprawnień!")
        return
    try:
        await member.timeout(None)
        await ctx.send(f"{member.mention} odwyciszony")
    except:
        await ctx.send("Błąd odwyciszenia")

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
async def removemod(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("Tylko właściciel!")
        return
    MODERATORS.discard(member.id)
    await ctx.send(f"{member.mention} stracił uprawnienia")

@bot.command()
async def czesc(ctx):
    await ctx.send("Cześć! Bot działa 24/7!")

@bot.command()
async def szynszyl(ctx):
    import random
    choices = ["tosterze", "panierce", "pralce", "butelce", "kondomie"]
    weights = [50, 19, 19, 10, 2]
    result = random.choices(choices, weights=weights)[0]
    await ctx.send(f"Szynszyl w {result}!")

@bot.command()
async def losuj(ctx, *options):
    import random
    if not options:
        result = random.randint(1, 100)
        await ctx.send(f"Wylosowana liczba: {result}")
    elif len(options) == 1 and options[0].isdigit():
        max_num = int(options[0])
        if max_num < 1:
            await ctx.send("Liczba musi być > 0!")
            return
        result = random.randint(1, max_num)
        await ctx.send(f"Wylosowana liczba (1-{max_num}): {result}")
    else:
        result = random.choice(options)
        await ctx.send(f"Wybrana opcja: {result}")

@bot.command()
async def kostka(ctx, dice_count: int = 1):
    import random
    if dice_count < 1 or dice_count > 10:
        await ctx.send("Liczba kostek: 1-10!")
        return
    results = [random.randint(1, 6) for _ in range(dice_count)]
    total = sum(results)
    if dice_count == 1:
        await ctx.send(f"Kostka: {results[0]}")
    else:
        await ctx.send(f"Kostki: {' + '.join(map(str, results))} = {total}")

@bot.command()
async def moneta(ctx):
    import random
    result = random.choice(["Orzeł", "Reszka"])
    await ctx.send(f"Moneta: {result}")

@bot.command()
async def info(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    await ctx.send(f"ID: {member.id}, Nick: {member.display_name}")

@bot.command()
async def pomoc(ctx):
    help_text = """**KOMENDY BOTA:**
**Właściciel:** !addmod @user, !removemod @user
**Moderacja:** !ban @user, !mute @user, !unmute @user, !clear 10
**Zabawa:** !czesc, !szynszyl, !losuj, !kostka, !moneta
**Info:** !ping, !info, !pomoc"""
    await ctx.send(help_text)

if __name__ == "__main__":
    # Start Flask server in background
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Start Discord bot
    token = os.getenv('DISCORD_TOKEN')
    if token:
        print("Starting Discord bot...")
        bot.run(token)
    else:
        print("Missing DISCORD_TOKEN")
