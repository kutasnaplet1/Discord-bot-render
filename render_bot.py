import discord
from discord.ext import commands
import os

# Setup intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

MODERATORS = set()

@bot.event
async def on_ready():
    print(f'Bot online: {bot.user}')
    await bot.change_presence(status=discord.Status.online)

@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! {latency}ms')

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="Brak powodu"):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("❌ Brak uprawnień!")
        return
    try:
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member.mention} zbanowany. Powód: {reason}")
    except Exception:
        await ctx.send("❌ Nie mogę zbanować tego użytkownika!")

@bot.command()
async def mute(ctx, member: discord.Member, *, reason="Brak powodu"):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("❌ Brak uprawnień!")
        return
    try:
        from datetime import datetime, timedelta
        until = datetime.now() + timedelta(minutes=10)
        await member.timeout(until, reason=reason)
        await ctx.send(f"🔇 {member.mention} wyciszony na 10 minut. Powód: {reason}")
    except Exception:
        await ctx.send("❌ Nie mogę wyciszyć tego użytkownika!")

@bot.command()
async def unmute(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("❌ Brak uprawnień!")
        return
    try:
        await member.timeout(None)
        await ctx.send(f"🔊 {member.mention} odwyciszony")
    except Exception:
        await ctx.send("❌ Nie mogę odwyciszyć tego użytkownika!")

@bot.command()
async def clear(ctx, amount: int = 5):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("❌ Brak uprawnień!")
        return
    if amount > 100:
        amount = 100
    try:
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🗑️ Usunięto {len(deleted) - 1} wiadomości", delete_after=3)
    except Exception:
        await ctx.send("❌ Nie mogę usunąć wiadomości!")

@bot.command()
async def addmod(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("❌ Tylko właściciel serwera!")
        return
    MODERATORS.add(member.id)
    await ctx.send(f"✅ {member.mention} otrzymał uprawnienia moderatora!")

@bot.command()
async def removemod(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("❌ Tylko właściciel serwera!")
        return
    MODERATORS.discard(member.id)
    await ctx.send(f"✅ {member.mention} stracił uprawnienia moderatora!")

@bot.command()
async def czesc(ctx):
    await ctx.send("👋 Cześć! Bot działa 24/7 dzięki Render.com!")

@bot.command()
async def szynszyl(ctx):
    import random
    choices = [
        ("tosterze", 50),
        ("panierce", 19), 
        ("pralce", 19),
        ("butelce", 10),
        ("kondomie", 2)
    ]
    
    rand = random.randint(1, 100)
    cumulative = 0
    
    for choice, weight in choices:
        cumulative += weight
        if rand <= cumulative:
            await ctx.send(f"🐹 Szynszyl siedzi w {choice}!")
            return

@bot.command()
async def losuj(ctx, *options):
    import random
    if not options:
        result = random.randint(1, 100)
        await ctx.send(f"🎲 Wylosowana liczba: **{result}**")
    elif len(options) == 1 and options[0].isdigit():
        max_num = int(options[0])
        if max_num < 1:
            await ctx.send("❌ Liczba musi być większa od 0!")
            return
        result = random.randint(1, max_num)
        await ctx.send(f"🎲 Wylosowana liczba (1-{max_num}): **{result}**")
    else:
        result = random.choice(options)
        await ctx.send(f"🎯 Wybrana opcja: **{result}**")

@bot.command()
async def kostka(ctx, dice_count: int = 1):
    import random
    if dice_count < 1 or dice_count > 10:
        await ctx.send("❌ Liczba kostek: 1-10!")
        return
    
    results = [random.randint(1, 6) for _ in range(dice_count)]
    total = sum(results)
    
    if dice_count == 1:
        await ctx.send(f"🎲 Wynik kostki: **{results[0]}**")
    else:
        dice_str = " + ".join(map(str, results))
        await ctx.send(f"🎲 Wyniki ({dice_count} kostek): {dice_str} = **{total}**")

@bot.command()
async def moneta(ctx):
    import random
    result = random.choice(["Orzeł 🦅", "Reszka 🪙"])
    await ctx.send(f"🪙 Rzut monetą: **{result}**")

@bot.command()
async def info(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    embed = discord.Embed(
        title=f"Informacje o {member.display_name}",
        color=0x0099ff
    )
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Nick", value=member.display_name, inline=True)
    embed.add_field(name="Konto utworzone", value=member.created_at.strftime("%d.%m.%Y"), inline=True)
    
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    
    await ctx.send(embed=embed)

@bot.command()
async def pomoc(ctx):
    embed = discord.Embed(
        title="🤖 Komendy Bota",
        description="Lista dostępnych komend:",
        color=0x00ff00
    )
    
    embed.add_field(
        name="👑 Właściciel",
        value="`!addmod @user` - nadaj uprawnienia\n`!removemod @user` - odbierz uprawnienia",
        inline=False
    )
    
    embed.add_field(
        name="🛡️ Moderacja",
        value="`!ban @user [powód]` - banuj\n`!mute @user [powód]` - wycisz\n`!unmute @user` - odwycisz\n`!clear [liczba]` - usuń wiadomości",
        inline=False
    )
    
    embed.add_field(
        name="🎮 Zabawa",
        value="`!czesc` - powitanie\n`!szynszyl` - gdzie szynszyl?\n`!losuj [opcje]` - losuj\n`!kostka [liczba]` - rzuć kostką\n`!moneta` - rzuć monetą",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Informacje",
        value="`!info [@user]` - info o użytkowniku\n`!ping` - sprawdź ping",
        inline=False
    )
    
    await ctx.send(embed=embed)

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ BŁĄD: Brak DISCORD_TOKEN w zmiennych środowiskowych")
        exit(1)
    
    try:
        print("🚀 Uruchamiam Discord Bota...")
        bot.run(token, log_handler=None)
    except Exception as e:
        print(f"❌ BŁĄD URUCHOMIENIA: {e}")
        exit(1)
