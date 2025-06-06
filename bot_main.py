import discord
from discord.ext import commands
import asyncio
import logging
import os
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
MODERATORS = set()

class Colors:
    SUCCESS = 0x00ff00
    ERROR = 0xff0000
    WARNING = 0xffff00
    INFO = 0x0099ff
    MODERATION = 0xff6b35

def can_moderate(user_id, guild_owner_id):
    return user_id == guild_owner_id or user_id in MODERATORS

def is_owner(user_id, guild_owner_id):
    return user_id == guild_owner_id

@bot.event
async def on_ready():
    logger.info(f'{bot.user} jest online na Render 24/7!')
    logger.info(f'Bot jest na {len(bot.guilds)} serwerach')
    activity = discord.Activity(type=discord.ActivityType.watching, name="Render 24/7 | !help")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Brakuje argumentów! Użyj `!help` po więcej informacji.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Nieprawidłowy argument! Sprawdź składnię komendy.")
    else:
        logger.error(f"Nieobsłużony błąd: {error}")
        await ctx.send("❌ Wystąpił nieoczekiwany błąd!")

@bot.command(name='addmod')
async def add_moderator(ctx, member: discord.Member):
    if not is_owner(ctx.author.id, ctx.guild.owner_id):
        await ctx.send("❌ Tylko właściciel serwera może nadawać uprawnienia!")
        return
    
    MODERATORS.add(member.id)
    embed = discord.Embed(
        title="✅ Uprawnienia nadane",
        description=f"{member.mention} otrzymał uprawnienia moderatorskie!",
        color=Colors.SUCCESS
    )
    await ctx.send(embed=embed)

@bot.command(name='removemod')
async def remove_moderator(ctx, member: discord.Member):
    if not is_owner(ctx.author.id, ctx.guild.owner_id):
        await ctx.send("❌ Tylko właściciel serwera może odbierać uprawnienia!")
        return
    
    MODERATORS.discard(member.id)
    embed = discord.Embed(
        title="✅ Uprawnienia odebrane",
        description=f"{member.mention} stracił uprawnienia moderatorskie!",
        color=Colors.WARNING
    )
    await ctx.send(embed=embed)

@bot.command(name='ban')
async def ban_user(ctx, member: discord.Member, *, reason="Brak powodu"):
    if not can_moderate(ctx.author.id, ctx.guild.owner_id):
        await ctx.send("❌ Brak uprawnień do banowania!")
        return
    
    if member.id == ctx.author.id:
        await ctx.send("❌ Nie możesz zbanować siebie!")
        return
    
    if not is_owner(ctx.author.id, ctx.guild.owner_id) and member.top_role >= ctx.author.top_role:
        await ctx.send("❌ Nie możesz banować użytkowników z wyższą rolą!")
        return
    
    try:
        await member.ban(reason=f"Zbanowany przez {ctx.author} - {reason}")
        embed = discord.Embed(
            title="🔨 Użytkownik zbanowany",
            description=f"**Użytkownik:** {member.mention}\n**Powód:** {reason}",
            color=Colors.ERROR
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("❌ Nie mam uprawnień do banowania tego użytkownika!")

@bot.command(name='mute')
async def mute_user(ctx, member: discord.Member, duration="10m", *, reason="Brak powodu"):
    if not can_moderate(ctx.author.id, ctx.guild.owner_id):
        await ctx.send("❌ Brak uprawnień do wyciszania!")
        return
    
    if member.id == ctx.author.id:
        await ctx.send("❌ Nie możesz wyciszyć siebie!")
        return
    
    if not is_owner(ctx.author.id, ctx.guild.owner_id) and member.top_role >= ctx.author.top_role:
        await ctx.send("❌ Nie możesz wyciszać użytkowników z wyższą rolą!")
        return
    
    time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    if duration[-1] in time_units:
        try:
            time_amount = int(duration[:-1])
            time_seconds = time_amount * time_units[duration[-1]]
            if time_seconds > 2419200:
                time_seconds = 2419200
            until = datetime.now() + timedelta(seconds=time_seconds)
        except ValueError:
            await ctx.send("❌ Nieprawidłowy format czasu! (np. 10m, 1h, 2d)")
            return
    else:
        await ctx.send("❌ Nieprawidłowy format czasu! (np. 10m, 1h, 2d)")
        return
    
    try:
        await member.timeout(until, reason=f"Wyciszony przez {ctx.author} - {reason}")
        embed = discord.Embed(
            title="🔇 Użytkownik wyciszony",
            description=f"**Użytkownik:** {member.mention}\n**Czas:** {duration}\n**Powód:** {reason}",
            color=Colors.MODERATION
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("❌ Nie mam uprawnień do wyciszania tego użytkownika!")

@bot.command(name='unmute')
async def unmute_user(ctx, member: discord.Member):
    if not can_moderate(ctx.author.id, ctx.guild.owner_id):
        await ctx.send("❌ Brak uprawnień do odwyciszania!")
        return
    
    try:
        await member.timeout(None)
        embed = discord.Embed(
            title="🔊 Użytkownik odwyciszony",
            description=f"**Użytkownik:** {member.mention}",
            color=Colors.SUCCESS
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("❌ Nie mam uprawnień do odwyciszania tego użytkownika!")

@bot.command(name='clear')
async def clear_messages(ctx, amount: int):
    if not can_moderate(ctx.author.id, ctx.guild.owner_id):
        await ctx.send("❌ Brak uprawnień do usuwania wiadomości!")
        return
    
    if amount < 1 or amount > 100:
        await ctx.send("❌ Liczba wiadomości musi być między 1 a 100!")
        return
    
    try:
        deleted = await ctx.channel.purge(limit=amount + 1)
        embed = discord.Embed(
            title="🗑️ Wiadomości usunięte",
            description=f"Usunięto {len(deleted) - 1} wiadomości",
            color=Colors.INFO
        )
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(3)
        await msg.delete()
    except discord.Forbidden:
        await ctx.send("❌ Nie mam uprawnień do usuwania wiadomości!")

@bot.command(name='info')
async def user_info(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    embed = discord.Embed(
        title=f"Informacje o {member.display_name}",
        color=member.color if member.color.value != 0 else Colors.INFO
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id, inline=True)
    
    if member.joined_at:
        embed.add_field(name="Dołączył", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
    
    embed.add_field(name="Najwyższa rola", value=member.top_role.mention, inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Opóźnienie: **{latency}ms**",
        color=Colors.INFO
    )
    await ctx.send(embed=embed)

@bot.command(name='czesc')
async def hello_command(ctx):
    embed = discord.Embed(
        title="👋 Cześć z Render!",
        description="https://cdn.discordapp.com/attachments/1242768717037637632/1247959025992220703/invitation.jpg",
        color=Colors.INFO
    )
    await ctx.send(embed=embed)

@bot.command(name='szynszyl')
async def szynszyl_command(ctx):
    import random
    choices = [("tosterze", 50), ("panierce", 19), ("pralce", 19), ("butelce", 10), ("kondomie", 2)]
    
    rand = random.randint(1, 100)
    cumulative = 0
    result = choices[0][0]
    
    for choice, weight in choices:
        cumulative += weight
        if rand <= cumulative:
            result = choice
            break
    
    percentage = [w for c, w in choices if c == result][0]
    embed = discord.Embed(
        title="🐭 Szynszyl siedzi w...",
        description=f"**{result}** ({percentage}%)",
        color=Colors.INFO
    )
    await ctx.send(embed=embed)

@bot.command(name='losuj')
async def random_command(ctx, *options):
    import random
    
    if not options:
        result = random.randint(1, 100)
        embed = discord.Embed(
            title="🎲 Losowanie",
            description=f"Wylosowana liczba: **{result}**",
            color=Colors.INFO
        )
    elif len(options) == 1 and options[0].isdigit():
        max_num = int(options[0])
        if max_num < 1:
            await ctx.send("❌ Liczba musi być większa od 0!")
            return
        result = random.randint(1, max_num)
        embed = discord.Embed(
            title="🎲 Losowanie",
            description=f"Wylosowana liczba (1-{max_num}): **{result}**",
            color=Colors.INFO
        )
    else:
        result = random.choice(options)
        embed = discord.Embed(
            title="🎲 Losowanie",
            description=f"Wybrana opcja: **{result}**",
            color=Colors.INFO
        )
    
    await ctx.send(embed=embed)

@bot.command(name='kostka')
async def dice_command(ctx, dice_count: int = 1):
    import random
    
    if dice_count < 1 or dice_count > 10:
        await ctx.send("❌ Liczba kostek musi być między 1 a 10!")
        return
    
    results = [random.randint(1, 6) for _ in range(dice_count)]
    total = sum(results)
    
    if dice_count == 1:
        description = f"🎲 Wynik: **{results[0]}**"
    else:
        description = f"🎲 Wyniki: {' + '.join(map(str, results))} = **{total}**"
    
    embed = discord.Embed(
        title="🎯 Rzut kostką",
        description=description,
        color=Colors.INFO
    )
    await ctx.send(embed=embed)

@bot.command(name='moneta')
async def coin_command(ctx):
    import random
    result = random.choice(["Orzeł", "Reszka"])
    embed = discord.Embed(
        title="🪙 Rzut monetą",
        description=f"Wynik: **{result}**",
        color=Colors.INFO
    )
    await ctx.send(embed=embed)

@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(
        title="🤖 Bot Render 24/7",
        description="Automatyczne aktualizacje z GitHub - bot działa non-stop!",
        color=Colors.INFO
    )
    
    embed.add_field(
        name="👑 Właściciel",
        value="`!addmod @user` - nadaje uprawnienia\n`!removemod @user` - odbiera uprawnienia",
        inline=False
    )
    
    embed.add_field(
        name="⚡ Moderacja",
        value="`!ban @user [powód]` - banuje\n`!mute @user [czas] [powód]` - wycisza\n`!unmute @user` - odwycisza\n`!clear <liczba>` - usuwa wiadomości",
        inline=False
    )
    
    embed.add_field(
        name="🎉 Fun",
        value="`!czesc` - powitanie\n`!szynszyl` - losowanie\n`!losuj [opcje]` - losuje\n`!kostka [ile]` - rzuca kostką\n`!moneta` - rzuca monetą",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Informacje",
        value="`!info [@user]` - informacje\n`!ping` - sprawdza ping",
        inline=False
    )
    
    embed.set_footer(text="Render 24/7")
    
    await ctx.send(embed=embed)

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        exit(1)
    
    try:
        logger.info("Uruchamianie naprawionego bota na Render 24/7...")
        bot.run(token)
    except Exception as e:
        logger.error(f"Błąd podczas uruchamiania bota: {e}")
        exit(1)
