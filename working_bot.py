import discord
from discord.ext import commands
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
MODERATORS = set()

@bot.event
async def on_ready():
    logger.info(f'Bot {bot.user} is online!')
    activity = discord.Activity(type=discord.ActivityType.watching, name="!help")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.command(name='ping')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! {latency}ms')

@bot.command(name='ban')
async def ban_user(ctx, member: discord.Member, *, reason="Brak powodu"):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("❌ Brak uprawnień!")
        return
    
    try:
        await member.ban(reason=reason)
        await ctx.send(f"🔨 {member.mention} został zbanowany. Powód: {reason}")
    except:
        await ctx.send("❌ Nie mogę zbanować tego użytkownika!")

@bot.command(name='mute')
async def mute_user(ctx, member: discord.Member, *, reason="Brak powodu"):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("❌ Brak uprawnień!")
        return
    
    try:
        from datetime import datetime, timedelta
        until = datetime.now() + timedelta(minutes=10)
        await member.timeout(until, reason=reason)
        await ctx.send(f"🔇 {member.mention} został wyciszony na 10 minut. Powód: {reason}")
    except:
        await ctx.send("❌ Nie mogę wyciszyć tego użytkownika!")

@bot.command(name='unmute')
async def unmute_user(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("❌ Brak uprawnień!")
        return
    
    try:
        await member.timeout(None)
        await ctx.send(f"🔊 {member.mention} został odwyciszony")
    except:
        await ctx.send("❌ Nie mogę odwyciszyć tego użytkownika!")

@bot.command(name='clear')
async def clear_messages(ctx, amount: int = 5):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("❌ Brak uprawnień!")
        return
    
    if amount > 100:
        amount = 100
    
    try:
        deleted = await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"🗑️ Usunięto {len(deleted) - 1} wiadomości")
        import asyncio
        await asyncio.sleep(3)
        await msg.delete()
    except:
        await ctx.send("❌ Nie mogę usunąć wiadomości!")

@bot.command(name='addmod')
async def add_moderator(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("❌ Tylko właściciel może nadawać uprawnienia!")
        return
    
    MODERATORS.add(member.id)
    await ctx.send(f"✅ {member.mention} otrzymał uprawnienia moderatorskie!")

@bot.command(name='removemod')
async def remove_moderator(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("❌ Tylko właściciel może odbierać uprawnienia!")
        return
    
    MODERATORS.discard(member.id)
    await ctx.send(f"✅ {member.mention} stracił uprawnienia moderatorskie!")

@bot.command(name='czesc')
async def hello_command(ctx):
    await ctx.send("👋 Cześć! Bot działa na Render 24/7!")

@bot.command(name='szynszyl')
async def szynszyl_command(ctx):
    import random
    choices = ["tosterze", "panierce", "pralce", "butelce", "kondomie"]
    result = random.choice(choices)
    await ctx.send(f"🐭 Szynszyl siedzi w **{result}**!")

@bot.command(name='losuj')
async def random_command(ctx, *options):
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
        await ctx.send(f"🎲 Wybrana opcja: **{result}**")

@bot.command(name='kostka')
async def dice_command(ctx, dice_count: int = 1):
    import random
    
    if dice_count < 1 or dice_count > 10:
        await ctx.send("❌ Liczba kostek musi być między 1 a 10!")
        return
    
    results = [random.randint(1, 6) for _ in range(dice_count)]
    total = sum(results)
    
    if dice_count == 1:
        await ctx.send(f"🎲 Wynik: **{results[0]}**")
    else:
        await ctx.send(f"🎲 Wyniki: {' + '.join(map(str, results))} = **{total}**")

@bot.command(name='moneta')
async def coin_command(ctx):
    import random
    result = random.choice(["Orzeł", "Reszka"])
    await ctx.send(f"🪙 Rzut monetą: **{result}**")

@bot.command(name='info')
async def user_info(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    embed = discord.Embed(title=f"Informacje o {member.display_name}", color=0x0099ff)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="ID", value=member.id, inline=True)
    if member.joined_at:
        embed.add_field(name="Dołączył", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
    embed.add_field(name="Najwyższa rola", value=member.top_role.mention, inline=True)
    await ctx.send(embed=embed)

@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(title="🤖 Bot Commands", description="Bot działa 24/7 na Render!", color=0x0099ff)
    
    embed.add_field(
        name="👑 Właściciel",
        value="`!addmod @user` - nadaje uprawnienia\n`!removemod @user` - odbiera uprawnienia",
        inline=False
    )
    
    embed.add_field(
        name="⚡ Moderacja",
        value="`!ban @user` - banuje\n`!mute @user` - wycisza\n`!unmute @user` - odwycisza\n`!clear 10` - usuwa wiadomości",
        inline=False
    )
    
    embed.add_field(
        name="🎉 Fun",
        value="`!czesc` - powitanie\n`!szynszyl` - losowanie\n`!losuj` - losuje\n`!kostka` - kostka\n`!moneta` - moneta",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Informacje",
        value="`!info` - informacje o użytkowniku\n`!ping` - sprawdza ping",
        inline=False
    )
    
    await ctx.send(embed=embed)

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found!")
        exit(1)
    
    try:
        logger.info("Starting bot...")
        bot.run(token)
    except Exception as e:
        logger.error(f"Error: {e}")
        exit(1)
