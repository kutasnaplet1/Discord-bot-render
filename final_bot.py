import discord
from discord.ext import commands
import os
import threading
import random
from datetime import datetime, timedelta

# Simple HTTP server without Flask dependency
import http.server
import socketserver
from urllib.parse import urlparse

class SimpleHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        if self.path == '/':
            self.wfile.write(b"Discord Bot is running!")
        elif self.path == '/status':
            self.wfile.write(b'{"status": "online", "uptime": "24/7"}')
        else:
            self.wfile.write(b"Discord Bot is running!")
    
    def log_message(self, format, *args):
        return  # Suppress logs

def run_http_server():
    with socketserver.TCPServer(("0.0.0.0", 5000), SimpleHandler) as httpd:
        httpd.serve_forever()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

MODERATORS = set()

@bot.event
async def on_ready():
    print(f'Bot online: {bot.user}')
    print(f'Servers: {len(bot.guilds)}')

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Ping: {latency}ms')

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="Brak powodu"):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("❌ Brak uprawnień!")
        return
    try:
        await member.ban(reason=reason)
        await ctx.send(f"🔨 {member.mention} został zbanowany!\nPowód: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ Brak uprawnień do banowania!")
    except Exception as e:
        await ctx.send(f"❌ Błąd: {e}")

@bot.command()
async def mute(ctx, member: discord.Member, *, reason="Brak powodu"):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("❌ Brak uprawnień!")
        return
    try:
        until = datetime.now() + timedelta(minutes=10)
        await member.timeout(until, reason=reason)
        await ctx.send(f"🔇 {member.mention} został wyciszony na 10 minut!\nPowód: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ Brak uprawnień do wyciszania!")
    except Exception as e:
        await ctx.send(f"❌ Błąd: {e}")

@bot.command()
async def unmute(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("❌ Brak uprawnień!")
        return
    try:
        await member.timeout(None)
        await ctx.send(f"🔊 {member.mention} został odwyciszony!")
    except Exception as e:
        await ctx.send(f"❌ Błąd: {e}")

@bot.command()
async def clear(ctx, amount: int = 5):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("❌ Brak uprawnień!")
        return
    if amount > 100:
        await ctx.send("❌ Maksymalnie 100 wiadomości!")
        return
    try:
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🧹 Usunięto {len(deleted) - 1} wiadomości!", delete_after=3)
    except Exception as e:
        await ctx.send(f"❌ Błąd: {e}")

@bot.command()
async def addmod(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("❌ Tylko właściciel może nadawać uprawnienia!")
        return
    MODERATORS.add(member.id)
    await ctx.send(f"👑 {member.mention} został moderatorem!")

@bot.command()
async def removemod(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("❌ Tylko właściciel może odbierać uprawnienia!")
        return
    MODERATORS.discard(member.id)
    await ctx.send(f"👑 {member.mention} nie jest już moderatorem!")

@bot.command()
async def czesc(ctx):
    await ctx.send(f"Cześć {ctx.author.mention}! 👋\nJestem gotowy do pracy!")

@bot.command()
async def szynszyl(ctx):
    choices = ["tosterze", "panierce", "pralce", "butelce", "kondomie"]
    weights = [50, 19, 19, 10, 2]
    result = random.choices(choices, weights=weights)[0]
    await ctx.send(f"🐹 Szynszyl w {result}!")

@bot.command()
async def losuj(ctx, *options):
    if not options:
        result = random.randint(1, 100)
        await ctx.send(f"🎲 Wylosowana liczba: {result}")
    elif len(options) == 1 and options[0].isdigit():
        max_num = int(options[0])
        result = random.randint(1, max_num)
        await ctx.send(f"🎲 Wylosowana liczba (1-{max_num}): {result}")
    else:
        result = random.choice(options)
        await ctx.send(f"🎯 Wylosowano: {result}")

@bot.command()
async def kostka(ctx, dice_count: int = 1):
    if dice_count < 1 or dice_count > 10:
        await ctx.send("❌ Można rzucić 1-10 kostkami!")
        return
    results = [random.randint(1, 6) for _ in range(dice_count)]
    total = sum(results)
    if dice_count == 1:
        await ctx.send(f"🎲 Kostka: {results[0]}")
    else:
        await ctx.send(f"🎲 Kostki: {results}\nSuma: {total}")

@bot.command()
async def moneta(ctx):
    result = random.choice(["Orzeł", "Reszka"])
    await ctx.send(f"🪙 Moneta: {result}")

@bot.command()
async def info(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    embed = discord.Embed(
        title=f"Informacje o {member.display_name}",
        color=0x0099ff,
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    embed.add_field(name="ID", value=member.id, inline=True)
    
    if member.joined_at:
        embed.add_field(name="Dołączył na serwer", value=member.joined_at.strftime("%d.%m.%Y"), inline=True)
    else:
        embed.add_field(name="Dołączył na serwer", value="Nieznane", inline=True)
        
    embed.add_field(name="Konto utworzone", value=member.created_at.strftime("%d.%m.%Y"), inline=True)
    embed.add_field(name="Role", value=f"{len(member.roles) - 1}", inline=True)
    
    await ctx.send(embed=embed)

@bot.command()
async def pomoc(ctx):
    help_embed = discord.Embed(
        title="📋 Lista Komend",
        description="Wszystkie dostępne komendy bota:",
        color=0x0099ff
    )
    
    help_embed.add_field(
        name="🔨 Moderacja",
        value="!ban @user [powód]\n!mute @user [powód]\n!unmute @user\n!clear [liczba]\n!addmod @user\n!removemod @user",
        inline=False
    )
    
    help_embed.add_field(
        name="🎮 Zabawa",
        value="!czesc - powitanie\n!szynszyl - losowy szynszyl\n!losuj [opcje] - losowanie\n!kostka [liczba] - rzut kostką\n!moneta - rzut monetą",
        inline=False
    )
    
    help_embed.add_field(
        name="ℹ️ Informacje",
        value="!info [@user] - info o użytkowniku\n!ping - ping bota\n!pomoc - ta lista",
        inline=False
    )
    
    await ctx.send(embed=help_embed)

if __name__ == "__main__":
    # Start HTTP keepalive server
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    print("HTTP keepalive started on port 5000")
    
    # Start Discord bot
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ DISCORD_TOKEN not found!")
        exit(1)
    
    try:
        print("🚀 Starting Discord bot...")
        bot.run(token)
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
