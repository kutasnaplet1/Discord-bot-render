import discord
from discord.ext import commands
import os
import threading
import random
from datetime import datetime, timedelta

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
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)
MODERATORS = set()

@bot.event
async def on_ready():
    print(f'Bot online: {bot.user}')
    print(f'Servers: {len(bot.guilds)}')

@bot.event
async def on_command_error(ctx, error):
    print(f"Command error: {error}")
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("Nie znaleziono użytkownika!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Brakuje argumentu!")
    else:
        await ctx.send("Wystąpił błąd!")

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command()
async def ban(ctx, member: discord.Member = None, *, reason="Brak powodu"):
    if not member:
        await ctx.send("Podaj użytkownika do zbanowania!")
        return
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Brak uprawnień!")
        return
    try:
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} zbanowany")
    except discord.Forbidden:
        await ctx.send("Brak uprawnień do banowania!")
    except Exception as e:
        await ctx.send(f"Błąd: {e}")

@bot.command()
async def unban(ctx, user_id: int):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Brak uprawnień!")
        return
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"Unbanowano użytkownika {user.name}")
    except discord.NotFound:
        await ctx.send("Użytkownik nie jest zbanowany!")
    except Exception as e:
        await ctx.send(f"Błąd: {e}")

@bot.command()
async def mute(ctx, member: discord.Member = None, *, reason="Brak powodu"):
    if not member:
        await ctx.send("Podaj użytkownika do wyciszenia!")
        return
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Brak uprawnień!")
        return
    try:
        until = datetime.now() + timedelta(minutes=10)
        await member.timeout(until, reason=reason)
        await ctx.send(f"{member.mention} wyciszony")
    except discord.Forbidden:
        await ctx.send("Brak uprawnień do wyciszania!")
    except Exception as e:
        await ctx.send(f"Błąd: {e}")

@bot.command()
async def unmute(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("Podaj użytkownika do odwyciszenia!")
        return
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Brak uprawnień!")
        return
    try:
        await member.timeout(None)
        await ctx.send(f"{member.mention} odwyciszony")
    except Exception as e:
        await ctx.send(f"Błąd: {e}")

@bot.command()
async def clear(ctx, amount: int = 5):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Brak uprawnień!")
        return
    if amount > 100:
        amount = 100
    try:
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"Usunięto {len(deleted) - 1} wiadomości", delete_after=3)
    except Exception as e:
        await ctx.send(f"Błąd: {e}")

@bot.command()
async def napisz(ctx, channel: discord.TextChannel, *, message):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Brak uprawnień!")
        return
    try:
        await channel.send(message)
        await ctx.message.delete()
    except discord.Forbidden:
        await ctx.send("Brak uprawnień do pisania na tym kanale!")
    except Exception as e:
        await ctx.send(f"Błąd: {e}")

@bot.command()
async def addmod(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("Podaj użytkownika!")
        return
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("Tylko właściciel!")
        return
    MODERATORS.add(member.id)
    await ctx.send(f"{member.mention} jest moderatorem")

@bot.command()
async def removemod(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("Podaj użytkownika!")
        return
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
    choices = ["tosterze", "panierce", "pralce"]
    result = random.choice(choices)
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
            await ctx.send("Liczba musi być większa od 0!")
    else:
        result = random.choice(options)
        await ctx.send(f"Wybrano: {result}")

@bot.command()
async def kostka(ctx, dice_count: int = 1):
    if dice_count < 1:
        dice_count = 1
    if dice_count > 10:
        dice_count = 10
    
    results = [random.randint(1, 6) for _ in range(dice_count)]
    if dice_count == 1:
        await ctx.send(f"Kostka: {results[0]}")
    else:
        await ctx.send(f"Kostki: {results}, Suma: {sum(results)}")

@bot.command()
async def moneta(ctx):
    result = random.choice(["Orzeł", "Reszka"])
    await ctx.send(f"Moneta: {result}")

@bot.command()
async def info(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    info_text = f"**{member.display_name}**\n"
    info_text += f"ID: {member.id}\n"
    info_text += f"Role: {len(member.roles)-1}\n"
    if member.joined_at:
        info_text += f"Dołączył: {member.joined_at.strftime('%d.%m.%Y')}"
    
    await ctx.send(info_text)

@bot.command()
async def sprawdz(ctx, member: discord.Member = None):
    if not member:
        await ctx.send("Podaj użytkownika do sprawdzenia!")
        return
    
    embed = discord.Embed(
        title=f"Szczegółowe informacje o {member.display_name}",
        color=0x0099ff,
        timestamp=datetime.now()
    )
    
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="🆔 ID", value=member.id, inline=True)
    embed.add_field(name="📛 Nazwa", value=member.name, inline=True)
    embed.add_field(name="🏷️ Wyświetlana nazwa", value=member.display_name, inline=True)
    
    if member.joined_at:
        embed.add_field(name="📅 Dołączył na serwer", value=member.joined_at.strftime("%d.%m.%Y %H:%M"), inline=True)
    
    embed.add_field(name="🎂 Konto utworzone", value=member.created_at.strftime("%d.%m.%Y %H:%M"), inline=True)
    embed.add_field(name="🎭 Role", value=f"{len(member.roles) - 1}", inline=True)
    embed.add_field(name="📊 Status", value=str(member.status).title(), inline=True)
    embed.add_field(name="🔝 Najwyższa rola", value=member.top_role.mention if member.top_role.name != "@everyone" else "Brak", inline=True)
    embed.add_field(name="🤖 Bot", value="Tak" if member.bot else "Nie", inline=True)
    
    if member.premium_since:
        embed.add_field(name="💎 Nitro Boost", value=member.premium_since.strftime("%d.%m.%Y"), inline=True)
    
    permissions = []
    if member.guild_permissions.administrator:
        permissions.append("Administrator")
    if member.guild_permissions.manage_guild:
        permissions.append("Zarządzanie serwerem")
    if member.guild_permissions.manage_channels:
        permissions.append("Zarządzanie kanałami")
    if member.guild_permissions.manage_messages:
        permissions.append("Zarządzanie wiadomościami")
    if member.guild_permissions.ban_members:
        permissions.append("Banowanie")
    if member.guild_permissions.kick_members:
        permissions.append("Wyrzucanie")
    
    if permissions:
        embed.add_field(name="🔑 Główne uprawnienia", value="\n".join(permissions[:5]), inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def fabian(ctx):
    await ctx.send("opisuje to cwel")

@bot.command()
async def lena(ctx):
    await ctx.send("pela pije snajpera na lekcji polskiego")

@bot.command()
async def kutas(ctx):
    await ctx.send("naplet")

@bot.command()
async def help(ctx):
    help_text = """**KOMENDY BOTA:**

**Moderacja:**
!ban @user [powód] - banowanie
!unban [id] - usuwa bana
!mute @user [powód] - wyciszenie  
!unmute @user - odwyciszenie
!clear [liczba] - usuwanie wiadomości
!addmod @user - nadanie uprawnień (właściciel)
!removemod @user - odebranie uprawnień (właściciel)
!napisz #kanal wiadomość - pisze wiadomość i usuwa oryginalną

**Zabawa:**
!czesc - powitanie
!szynszyl - losowy szynszyl
!losuj [opcje] - losowanie
!kostka [liczba] - rzut kostką
!moneta - rzut monetą
!fabian - opisuje to cwel
!lena - pela pije snajpera na lekcji polskiego
!kutas - naplet

**Info:**
!info [@user] - podstawowe informacje
!sprawdz @user - szczegółowe informacje o użytkowniku
!ping - ping bota
!help - pomoc

Właściciel serwera ma pełne uprawnienia."""
    await ctx.send(help_text)

if __name__ == "__main__":
    # Start Flask server
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("Flask keepalive started")
    
    # Start Discord bot
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
