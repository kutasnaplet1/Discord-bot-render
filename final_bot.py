import discord
from discord.ext import commands
import os
import threading
import http.server
import socketserver
import random
from datetime import datetime, timedelta

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

# System moderatorów i kar
MODERATORS = set()
USER_PUNISHMENTS = {}  # {user_id: [{"type": "warn", "reason": "...", "date": "...", "by": "..."}]}

def add_punishment(user_id, punishment_type, reason, moderator_name):
    """Dodaje karę do historii użytkownika"""
    if user_id not in USER_PUNISHMENTS:
        USER_PUNISHMENTS[user_id] = []
    
    punishment = {
        "type": punishment_type,
        "reason": reason,
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "by": moderator_name
    }
    USER_PUNISHMENTS[user_id].append(punishment)

@bot.event
async def on_ready():
    print(f'Bot online: {bot.user}')
    print(f'Servers: {len(bot.guilds)}')

# SYSTEM UPRAWNIEŃ - tylko właściciel może nadawać uprawnienia moderacji
@bot.command()
async def addmod(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("Tylko właściciel serwera może nadawać uprawnienia moderacji.")
        return
    
    MODERATORS.add(member.id)
    await ctx.send(f"{member.mention} otrzymał uprawnienia moderatora.")

@bot.command()
async def removemod(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("Tylko właściciel serwera może zabierać uprawnienia moderacji.")
        return
    
    MODERATORS.discard(member.id)
    await ctx.send(f"{member.mention} stracił uprawnienia moderatora.")

# KOMENDY MODERACYJNE - właściciel może karać każdego, moderatorzy nie mogą karać właściciela
@bot.command()
async def ban(ctx, member: discord.Member, *, reason="Brak powodu"):
    # Sprawdź uprawnienia
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Nie masz uprawnień do banowania.")
        return
    
    # Moderatorzy nie mogą banować właściciela
    if member.id == ctx.guild.owner_id and ctx.author.id != ctx.guild.owner_id:
        await ctx.send("Nie możesz zbanować właściciela serwera.")
        return
    
    try:
        await member.ban(reason=reason)
        add_punishment(member.id, "ban", reason, ctx.author.display_name)
        await ctx.send(f"{member.mention} został zbanowany.\nPowód: {reason}")
    except:
        await ctx.send("Błąd podczas banowania użytkownika.")

@bot.command()
async def unban(ctx, user_id: int):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Nie masz uprawnień do odbanowywania.")
        return
    
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"Użytkownik {user.name} został odbanowany.")
    except:
        await ctx.send("Błąd podczas odbanowywania lub użytkownik nie jest zbanowany.")

@bot.command()
async def mute(ctx, member: discord.Member, czas: int = 10, *, reason="Brak powodu"):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Nie masz uprawnień do wyciszania.")
        return
    
    if member.id == ctx.guild.owner_id and ctx.author.id != ctx.guild.owner_id:
        await ctx.send("Nie możesz wyciszyć właściciela serwera.")
        return
    
    # Maksymalnie 50 dni
    if czas > 50 * 24 * 60:  # 50 dni w minutach
        czas = 50 * 24 * 60
        await ctx.send(f"Maksymalny czas wyciszenia to 50 dni. Ustawiam na {czas // (24 * 60)} dni.")
    
    try:
        until = datetime.now() + timedelta(minutes=czas)
        await member.timeout(until, reason=reason)
        add_punishment(member.id, "mute", f"{reason} ({czas} min)", ctx.author.display_name)
        await ctx.send(f"{member.mention} został wyciszony na {czas} minut.\nPowód: {reason}")
    except:
        await ctx.send("Błąd podczas wyciszania użytkownika.")

@bot.command()
async def unmute(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Nie masz uprawnień do odwyciszania.")
        return
    
    try:
        await member.timeout(None)
        await ctx.send(f"{member.mention} został odwyciszony.")
    except:
        await ctx.send("Błąd podczas odwyciszania użytkownika.")

@bot.command()
async def warn(ctx, member: discord.Member, *, reason="Brak powodu"):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Nie masz uprawnień do ostrzegania.")
        return
    
    if member.id == ctx.guild.owner_id and ctx.author.id != ctx.guild.owner_id:
        await ctx.send("Nie możesz ostrzec właściciela serwera.")
        return
    
    add_punishment(member.id, "warn", reason, ctx.author.display_name)
    await ctx.send(f"{member.mention} otrzymał ostrzeżenie.\nPowód: {reason}")

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="Brak powodu"):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Nie masz uprawnień do wyrzucania.")
        return
    
    if member.id == ctx.guild.owner_id and ctx.author.id != ctx.guild.owner_id:
        await ctx.send("Nie możesz wyrzucić właściciela serwera.")
        return
    
    try:
        await member.kick(reason=reason)
        add_punishment(member.id, "kick", reason, ctx.author.display_name)
        await ctx.send(f"{member.mention} został wyrzucony z serwera.\nPowód: {reason}")
    except:
        await ctx.send("Błąd podczas wyrzucania użytkownika.")

@bot.command()
async def historiakar(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Nie masz uprawnień do przeglądania historii kar.")
        return
    
    if member.id not in USER_PUNISHMENTS or not USER_PUNISHMENTS[member.id]:
        await ctx.send(f"{member.display_name} nie ma żadnych kar w historii.")
        return
    
    embed = discord.Embed(
        title=f"Historia kar - {member.display_name}",
        color=0xff0000
    )
    
    punishments = USER_PUNISHMENTS[member.id]
    for i, punishment in enumerate(punishments[-10:], 1):  # Ostatnie 10 kar
        embed.add_field(
            name=f"{i}. {punishment['type'].upper()}",
            value=f"**Powód:** {punishment['reason']}\n**Data:** {punishment['date']}\n**Przez:** {punishment['by']}",
            inline=False
        )
    
    embed.set_footer(text=f"Łącznie kar: {len(punishments)}")
    await ctx.send(embed=embed)

@bot.command()
async def clear(ctx, amount: int):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Nie masz uprawnień do usuwania wiadomości.")
        return
    
    if amount > 100:
        amount = 100
        await ctx.send("Maksymalnie można usunąć 100 wiadomości na raz.")
    
    if amount < 1:
        await ctx.send("Podaj liczbę większą od 0.")
        return
    
    try:
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"Usunięto {len(deleted) - 1} wiadomości.", delete_after=3)
    except:
        await ctx.send("Błąd podczas usuwania wiadomości.")

@bot.command()
async def napisz(ctx, channel: discord.TextChannel, *, message):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Nie masz uprawnień do wysyłania wiadomości na inne kanały.")
        return
    
    try:
        await channel.send(message)
        await ctx.message.delete()
        # Potwierdzenie na DM
        try:
            await ctx.author.send(f"✅ Wiadomość wysłana na {channel.mention}:\n{message}")
        except:
            pass  # Jeśli nie można wysłać DM
    except:
        await ctx.send("Błąd podczas wysyłania wiadomości.")

# KOMENDY INFORMACYJNE
@bot.command()
async def sprawdz(ctx, member: discord.Member):
    embed = discord.Embed(
        title=f"Informacje o {member.display_name}",
        color=0x0099ff,
        timestamp=datetime.now()
    )
    
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Nazwa", value=member.name, inline=True)
    embed.add_field(name="Wyświetlana nazwa", value=member.display_name, inline=True)
    
    if member.joined_at:
        embed.add_field(name="Dołączył na serwer", value=member.joined_at.strftime("%d.%m.%Y %H:%M"), inline=True)
    
    embed.add_field(name="Konto utworzone", value=member.created_at.strftime("%d.%m.%Y %H:%M"), inline=True)
    embed.add_field(name="Najwyższa rola", value=member.top_role.mention, inline=True)
    
    # Dodaj informację o karach
    if member.id in USER_PUNISHMENTS and USER_PUNISHMENTS[member.id]:
        embed.add_field(name="Łączna liczba kar", value=len(USER_PUNISHMENTS[member.id]), inline=True)
    else:
        embed.add_field(name="Łączna liczba kar", value="0", inline=True)
    
    await ctx.send(embed=embed)

# KOMENDY ROZRYWKOWE
@bot.command()
async def fabian(ctx):
    await ctx.send("to cwel")

@bot.command()
async def lena(ctx):
    await ctx.send("pije snajpera na lekcji polskiego")

@bot.command()
async def kutas(ctx):
    await ctx.send("naplet")

@bot.command()
async def szynszyl(ctx):
    choices = ["kondomie", "tosterze", "butelce", "pralce", "panierce"]
    weights = [2, 8, 20, 20, 50]
    
    result = random.choices(choices, weights=weights)[0]
    await ctx.send(f"szynszyl w {result}")

# PODSTAWOWE KOMENDY
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command()
async def reset(ctx):
    if ctx.author.id == ctx.guild.owner_id:
        await ctx.send("Bot zresetowany - wszystkie komendy usunięte. Można budować od nowa.")
    else:
        await ctx.send("Tylko właściciel serwera może resetować bota.")

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="🛡️ Komendy bota",
        description="Lista dostępnych komend",
        color=0x0099ff
    )
    
    # Komendy dla właściciela
    if ctx.author.id == ctx.guild.owner_id:
        embed.add_field(
            name="👑 Komendy właściciela",
            value="!addmod @użytkownik - nadaje uprawnienia moderatora\n!removemod @użytkownik - zabiera uprawnienia moderatora\n!reset - resetuje bota",
            inline=False
        )
    
    # Komendy moderacyjne
    if ctx.author.id == ctx.guild.owner_id or ctx.author.id in MODERATORS:
        embed.add_field(
            name="🛡️ Komendy moderacyjne",
            value="!ban @użytkownik [powód] - banuje użytkownika\n!unban <id> - odbanowuje użytkownika\n!mute @użytkownik [minuty] [powód] - wycisza (max 50 dni)\n!unmute @użytkownik - odwycisza\n!warn @użytkownik [powód] - ostrzega\n!kick @użytkownik [powód] - wyrzuca z serwera\n!clear <ilość> - usuwa wiadomości (max 100)\n!napisz #kanał <wiadomość> - wysyła wiadomość\n!historiakar @użytkownik - pokazuje historię kar",
            inline=False
        )
    
    embed.add_field(
        name="ℹ️ Komendy informacyjne",
        value="!sprawdz @użytkownik - szczegółowe informacje o użytkowniku\n!ping - sprawdza ping bota",
        inline=False
    )
    
    embed.add_field(
        name="🎮 Komendy rozrywkowe",
        value="!fabian - komentarz o Fabianie\n!lena - komentarz o Lenie\n!kutas - komentarz\n!szynszyl - losowa odpowiedź z procentami",
        inline=False
    )
    
    embed.set_footer(text="Używaj komend odpowiedzialnie!")
    await ctx.send(embed=embed)

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
        print("Starting Discord bot...")
        bot.run(token)
    except Exception as e:
        print(f"Bot error: {e}")
        exit(1)
