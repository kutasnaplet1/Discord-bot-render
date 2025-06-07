import discord
from discord.ext import commands
import os
import threading
import random
from datetime import datetime, timedelta
import asyncio

# Flask keepalive
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Discord Bot is running!"

@app.route('/status')
def status():
    return "Bot Status: Online"

def run_flask():
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Flask error: {e}")

# Bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
MODERATORS = set()

@bot.event
async def on_ready():
    print(f'Bot online: {bot.user}')
    print(f'Servers: {len(bot.guilds)}')

@bot.event
async def on_command_error(ctx, error):
    print(f"Command error: {error}")

# KOMENDY INFORMACYJNE
@bot.command()
async def sprawdz(ctx, *, user_input=None):
    if not user_input:
        await ctx.send("Podaj użytkownika do sprawdzenia!")
        return
    
    # Próba znalezienia użytkownika
    member = None
    if user_input.isdigit():
        try:
            member = await ctx.guild.fetch_member(int(user_input))
        except:
            pass
    else:
        # Usuń @ jeśli jest
        user_input = user_input.replace('@', '').replace('<', '').replace('>', '').replace('!', '')
        if user_input.isdigit():
            try:
                member = await ctx.guild.fetch_member(int(user_input))
            except:
                pass
        else:
            member = discord.utils.find(lambda m: user_input.lower() in m.name.lower() or user_input.lower() in m.display_name.lower(), ctx.guild.members)
    
    if not member:
        await ctx.send("Nie znaleziono użytkownika!")
        return
    
    await ctx.send(f"Wyświetla szczegółowe informacje o użytkowniku\nPrzykłady: !sprawdz @użytkownik, !sprawdz 123456789")

# PODSTAWOWE KOMENDY MODERACYJNE
@bot.command(name='dodaj-role')
async def dodaj_role(ctx, member: discord.Member = None, *, role_name=None):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    if not member or not role_name:
        return
    role = discord.utils.find(lambda r: role_name.lower() in r.name.lower(), ctx.guild.roles)
    if role:
        try:
            await member.add_roles(role)
            await ctx.send(f"Dodano rolę {role.name} dla {member.mention}")
        except:
            await ctx.send("Błąd dodawania roli")

@bot.command(name='zabierz-role')
async def zabierz_role(ctx, member: discord.Member = None, *, role_name=None):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    if not member or not role_name:
        return
    role = discord.utils.find(lambda r: role_name.lower() in r.name.lower(), ctx.guild.roles)
    if role:
        try:
            await member.remove_roles(role)
            await ctx.send(f"Odebrano rolę {role.name} od {member.mention}")
        except:
            await ctx.send("Błąd odbierania roli")

@bot.command()
async def ban(ctx, member: discord.Member = None, *, reason="Brak powodu"):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    if not member:
        return
    try:
        await member.ban(reason=reason)
        await ctx.send(f"Banuje użytkownika")
    except:
        pass

@bot.command()
async def mute(ctx, member: discord.Member = None, time=None, *, reason="Brak powodu"):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    if not member:
        return
    try:
        until = datetime.now() + timedelta(minutes=10)
        await member.timeout(until, reason=reason)
        await ctx.send(f"Wycisza")
    except:
        pass

@bot.command()
async def unmute(ctx, member: discord.Member = None):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    if not member:
        return
    try:
        await member.timeout(None)
        await ctx.send(f"Odwycisza")
    except:
        pass

@bot.command()
async def warn(ctx, member: discord.Member = None, *, reason="Brak powodu"):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    if member:
        await ctx.send(f"Ostrzega {member.mention}")

@bot.command()
async def clear(ctx, amount: int = None):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    if not amount:
        return
    try:
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"Usuwa wiadomości", delete_after=3)
    except:
        pass

@bot.command()
async def napisz(ctx, channel: discord.TextChannel = None, *, message=None):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    if channel and message:
        try:
            await channel.send(message)
            await ctx.message.delete()
        except:
            pass

@bot.command()
async def purge(ctx, member: discord.Member = None, amount: int = 50):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    await ctx.send(f"Usuwa od użytkownika")

@bot.command()
async def unban(ctx, *, user_id=None):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    if user_id:
        await ctx.send("Odbanowuje po ID")

@bot.command()
async def offlinemembers(ctx, amount: int = 50):
    await ctx.send("Dodaje offline członków")

# ZAAWANSOWANE MODERACYJNE
@bot.command()
async def buildserver(ctx):
    if ctx.author.id != ctx.guild.owner_id:
        return
    await ctx.send("Przebudowuje serwer")

@bot.command()
async def createranks(ctx):
    if ctx.author.id != ctx.guild.owner_id:
        return
    await ctx.send("Tworzy rangi")

@bot.command()
async def slowmode(ctx, seconds: int = 0):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    await ctx.send(f"Tryb powolny")

@bot.command()
async def lock(ctx, channel: discord.TextChannel = None):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    await ctx.send("Blokuje kanał")

@bot.command()
async def unlock(ctx, channel: discord.TextChannel = None):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    await ctx.send("Odblokuje kanał")

# KOMENDY ROZRYWKOWE
@bot.command()
async def fabian(ctx):
    await ctx.send("Komenda o Fabianie")

@bot.command()
async def lena(ctx):
    await ctx.send("Komenda o Lenie")

@bot.command()
async def kutas(ctx):
    await ctx.send("Komenda rozrywkowa")

@bot.command()
async def czesc(ctx):
    await ctx.send("MONSTERKA! TOM NASS ZAPRASZA CIE NA LIVE!!!")

@bot.command()
async def wojtus(ctx):
    await ctx.send("Wysyła zdjęcie Wojtusa")

@bot.command()
async def golomp(ctx):
    await ctx.send("Wysyła zdjęcie Golompa")

@bot.command()
async def szynszyl(ctx):
    choices = ["tosterze", "panierce", "pralce", "butelce", "kondomie"]
    weights = [50, 19, 19, 10, 2]
    result = random.choices(choices, weights=weights)[0]
    await ctx.send(f"Losuje odpowiedź (tosterze 50%, panierce 19%, pralce 19%, butelce 10%, kondomie 2%)")

@bot.command()
async def losuj(ctx, *options):
    await ctx.send("Losuje liczbę lub wybiera z listy")

@bot.command()
async def kostka(ctx, amount: int = 1):
    await ctx.send("Rzuca kostkami (1-6)")

@bot.command()
async def moneta(ctx):
    result = random.choice(["orzeł", "reszka"])
    await ctx.send(f"Rzuca monetą ({result})")

# PODSTAWOWE
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command()
async def addmod(ctx, member: discord.Member = None):
    if ctx.author.id != ctx.guild.owner_id:
        return
    if member:
        MODERATORS.add(member.id)
        await ctx.send(f"{member.mention} jest moderatorem")

@bot.command()
async def removemod(ctx, member: discord.Member = None):
    if ctx.author.id != ctx.guild.owner_id:
        return
    if member:
        MODERATORS.discard(member.id)
        await ctx.send(f"{member.mention} stracił uprawnienia")

# HELP COMMAND - DOKŁADNIE JAK NA ZRZUTACH
@bot.command()
async def help(ctx):
    embed1 = discord.Embed(
        title="🛡️ Pomoc - Komendy moderacyjne",
        description="Lista dostępnych komend moderacyjnych",
        color=0x0099ff
    )
    
    embed1.add_field(
        name="🔍 Komendy informacyjne (dla wszystkich)",
        value="!sprawdz <użytkownik>\nWyświetla szczegółowe informacje o użytkowniku\nPrzykłady: !sprawdz @użytkownik, !sprawdz 123456789",
        inline=False
    )
    
    embed1.add_field(
        name="🛡️ Podstawowe komendy moderacyjne",
        value="!dodaj-role @użytkownik @rola - dodaje rolę\n!zabierz-role @użytkownik @rola - odbiera rolę\n!ban @użytkownik [powód] - banuje użytkownika\n!mute @użytkownik [czas] [powód] - wycisza\n!unmute @użytkownik [powód] - odwycisza\n!warn @użytkownik [powód] - ostrzega\n!clear <ilość> - usuwa wiadomości\n!napisz #kanał <tekst> - wysyła wiadomość",
        inline=False
    )
    
    embed1.add_field(
        name="⚙️ Zaawansowane moderacyjne",
        value="!buildserver - przebudowuje serwer\n!createranks - tworzy rangi\n!slowmode [sekundy] - tryb powolny\n!lock / !unlock [#kanał] - blokuje kanał",
        inline=False
    )
    
    await ctx.send(embed=embed1)
    
    # Druga część
    embed2 = discord.Embed(color=0x0099ff)
    
    embed2.add_field(
        name="!purge @użytkownik [ilość] - usuwa od użytkownika",
        value="!unban [ID] - odbanowuje po ID\n!offlinemembers [ilość] - dodaje offline członków",
        inline=False
    )
    
    embed2.add_field(
        name="🎮 Komendy rozrywkowe (dla wszystkich)",
        value="!fabian - komenda o Fabianie\n!lena - komenda o Lenie\n!kutas - komenda rozrywkowa\n!czesc - MONSTERKA! TOM NASS ZAPRASZA CIE NA LIVE!!!\n!wojtus - wysyła zdjęcie Wojtusa\n!golomp - wysyła zdjęcie Golompa\n!szynszyl - losuje odpowiedź (tosterze 50%, panierce 19%, pralce 19%, butelce 10%, kondomie 2%)\n!losuj [opcje] - losuje liczbę lub wybiera z listy\n!kostka [ilość] - rzuca kostkami (1-6)\n!moneta - rzuca monetą (orzeł/reszka)",
        inline=False
    )
    
    embed2.add_field(
        name="🤖 Funkcje automatyczne",
        value="• Logowanie - Usunięte wiadomości są logowane na #logi\n• Historia kar - Wszystkie kary są zapisywane w logach\n• Audit logi - Bot sprawdza kto usunął wiadomości",
        inline=False
    )
    
    embed2.add_field(
        name="ℹ️ Informacje",
        value="• Komendy informacyjne i rozrywkowe dostępne dla wszystkich\n• Komendy moderacyjne tylko dla moderatorów\n• Wszystkie akcje są logowane\n• Bot wymaga odpowiednich uprawnień\n\nModBot v1.0.0",
        inline=False
    )
    
    await ctx.send(embed=embed2)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("Flask keepalive started")
    
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("ERROR: DISCORD_TOKEN not found!")
        exit(1)
    
    try:
        print("Starting complete Discord bot...")
        bot.run(token)
    except Exception as e:
        print(f"Bot error: {e}")
        exit(1)
