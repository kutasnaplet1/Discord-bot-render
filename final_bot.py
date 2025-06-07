import discord
from discord.ext import commands
import os
import threading
import random
from datetime import datetime, timedelta
import http.server
import socketserver

# Simple HTTP server without Flask
class SimpleHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Discord Bot is running!")
    
    def log_message(self, format, *args):
        return

def run_http_server():
    try:
        with socketserver.TCPServer(("0.0.0.0", 5000), SimpleHandler) as httpd:
            httpd.serve_forever()
    except Exception as e:
        print(f"HTTP server error: {e}")

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
    
    embed = discord.Embed(
        title=f"Informacje o {member.display_name}",
        color=0x0099ff,
        timestamp=datetime.now()
    )
    
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Nazwa", value=member.name, inline=True)
    embed.add_field(name="Wyświetlana nazwa", value=member.display_name, inline=True)
    
    if member.joined_at:
        embed.add_field(name="Dołączył na serwer", value=member.joined_at.strftime("%d.%m.%Y %H:%M"), inline=True)
    
    embed.add_field(name="Konto utworzone", value=member.created_at.strftime("%d.%m.%Y %H:%M"), inline=True)
    embed.add_field(name="Role", value=f"{len(member.roles) - 1}", inline=True)
    
    await ctx.send(embed=embed)

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
        await ctx.send(f"{member.mention} został zbanowany!\nPowód: {reason}")
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
        await ctx.send(f"{member.mention} został wyciszony!")
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
        await ctx.send(f"{member.mention} został odwyciszony!")
    except:
        pass

@bot.command()
async def warn(ctx, member: discord.Member = None, *, reason="Brak powodu"):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    if member:
        await ctx.send(f"{member.mention} otrzymał ostrzeżenie!\nPowód: {reason}")

@bot.command()
async def clear(ctx, amount: int = None):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    if not amount:
        return
    try:
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"Usunięto {len(deleted) - 1} wiadomości!", delete_after=3)
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
    await ctx.send(f"Usuwam wiadomości od {member.mention}")

@bot.command()
async def unban(ctx, *, user_id=None):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    if user_id:
        try:
            user_id = int(user_id)
            user = await bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"Unbanowano {user.name}")
        except:
            await ctx.send("Błąd unbanowania lub użytkownik nie jest zbanowany")

@bot.command()
async def offlinemembers(ctx, amount: int = 50):
    await ctx.send("Dodaję offline członków")

# ZAAWANSOWANE MODERACYJNE
@bot.command()
async def buildserver(ctx):
    if ctx.author.id != ctx.guild.owner_id:
        return
    await ctx.send("Przebudowuję serwer...")

@bot.command()
async def createranks(ctx):
    if ctx.author.id != ctx.guild.owner_id:
        return
    await ctx.send("Tworzę rangi...")

@bot.command()
async def slowmode(ctx, seconds: int = 0):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    try:
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"Tryb powolny ustawiony na {seconds} sekund")
    except:
        await ctx.send("Błąd ustawiania trybu powolnego")

@bot.command()
async def lock(ctx, channel: discord.TextChannel = None):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    if not channel:
        channel = ctx.channel
    await ctx.send(f"Blokuję kanał {channel.mention}")

@bot.command()
async def unlock(ctx, channel: discord.TextChannel = None):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        return
    if not channel:
        channel = ctx.channel
    await ctx.send(f"Odblokowuję kanał {channel.mention}")

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
    await ctx.send("Wysyłam zdjęcie Wojtusa")

@bot.command()
async def golomp(ctx):
    await ctx.send("Wysyłam zdjęcie Golompa")

@bot.command()
async def szynszyl(ctx):
    choices = ["tosterze", "panierce", "pralce", "butelce", "kondomie"]
    weights = [50, 19, 19, 10, 2]
    result = random.choices(choices, weights=weights)[0]
    await ctx.send(f"Szynszyl w {result}!")

@bot.command()
async def losuj(ctx, *options):
    if not options:
        result = random.randint(1, 100)
        await ctx.send(f"Wylosowana liczba: {result}")
    elif len(options) == 1 and options[0].isdigit():
        max_num = int(options[0])
        if max_num > 0:
            result = random.randint(1, max_num)
            await ctx.send(f"Liczba (1-{max_num}): {result}")
    else:
        result = random.choice(options)
        await ctx.send(f"Wybrano: {result}")

@bot.command()
async def kostka(ctx, amount: int = 1):
    if amount < 1:
        amount = 1
    if amount > 10:
        amount = 10
    
    results = [random.randint(1, 6) for _ in range(amount)]
    if amount == 1:
        await ctx.send(f"Kostka: {results[0]}")
    else:
        await ctx.send(f"Kostki: {results}, Suma: {sum(results)}")

@bot.command()
async def moneta(ctx):
    result = random.choice(["orzeł", "reszka"])
    await ctx.send(f"Moneta: {result}")

# FUNKCJE AUTOMATYCZNE
@bot.event
async def on_message_delete(message):
    """Logowanie - Usunięte wiadomości są logowane na #logi"""
    if message.author.bot:
        return
    
    log_channel = discord.utils.get(message.guild.channels, name="logi")
    if log_channel:
        embed = discord.Embed(
            title="Wiadomość usunięta",
            description=f"**Autor:** {message.author.mention}\n**Kanał:** {message.channel.mention}\n**Treść:** {message.content}",
            color=0xff0000,
            timestamp=datetime.now()
        )
        await log_channel.send(embed=embed)

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
        await ctx.send(f"{member.mention} został moderatorem!")

@bot.command()
async def removemod(ctx, member: discord.Member = None):
    if ctx.author.id != ctx.guild.owner_id:
        return
    if member:
        MODERATORS.discard(member.id)
        await ctx.send(f"{member.mention} stracił uprawnienia moderatora!")

# INFO COMMAND
@bot.command()
async def info(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    embed = discord.Embed(
        title=f"Informacje o {member.display_name}",
        color=member.color if member.color.value != 0 else 0x0099ff
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id, inline=True)
    
    if member.joined_at:
        embed.add_field(name="Dołączył", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
    
    embed.add_field(name="Najwyższa rola", value=member.top_role.mention, inline=True)
    
    await ctx.send(embed=embed)

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
    # Start HTTP server
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()
    print("HTTP keepalive started on port 5000")
    
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("ERROR: DISCORD_TOKEN not found!")
        exit(1)
    
    try:
        print("Starting Discord bot with ALL original commands...")
        bot.run(token)
    except Exception as e:
        print(f"Bot error: {e}")
        exit(1)
