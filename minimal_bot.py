import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
MODERATORS = set()

@bot.event
async def on_ready():
    print(f'{bot.user} online!')
    await bot.change_presence(status=discord.Status.online)

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
        await ctx.send(f"{member.mention} zbanowany. Powód: {reason}")
    except:
        await ctx.send("Nie mogę zbanować!")

@bot.command()
async def mute(ctx, member: discord.Member, *, reason="Brak powodu"):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Brak uprawnień!")
        return
    try:
        from datetime import datetime, timedelta
        until = datetime.now() + timedelta(minutes=10)
        await member.timeout(until, reason=reason)
        await ctx.send(f"{member.mention} wyciszony na 10 minut.")
    except:
        await ctx.send("Nie mogę wyciszyć!")

@bot.command()
async def unmute(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in MODERATORS:
        await ctx.send("Brak uprawnień!")
        return
    try:
        await member.timeout(None)
        await ctx.send(f"{member.mention} odwyciszony")
    except:
        await ctx.send("Nie mogę odwyciszyć!")

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
    except:
        await ctx.send("Nie mogę usunąć!")

@bot.command()
async def addmod(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("Tylko właściciel!")
        return
    MODERATORS.add(member.id)
    await ctx.send(f"{member.mention} otrzymał uprawnienia!")

@bot.command()
async def removemod(ctx, member: discord.Member):
    if ctx.author.id != ctx.guild.owner_id:
        await ctx.send("Tylko właściciel!")
        return
    MODERATORS.discard(member.id)
    await ctx.send(f"{member.mention} stracił uprawnienia!")

@bot.command()
async def czesc(ctx):
    await ctx.send("Cześć! Bot działa 24/7!")

@bot.command()
async def szynszyl(ctx):
    import random
    choices = ["tosterze", "panierce", "pralce", "butelce", "kondomie"]
    result = random.choice(choices)
    await ctx.send(f"Szynszyl siedzi w {result}!")

@bot.command()
async def losuj(ctx, *options):
    import random
    if not options:
        result = random.randint(1, 100)
        await ctx.send(f"Wylosowana liczba: {result}")
    elif len(options) == 1 and options[0].isdigit():
        max_num = int(options[0])
        if max_num < 1:
            await ctx.send("Liczba musi być większa od 0!")
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
        await ctx.send(f"Wynik: {results[0]}")
    else:
        await ctx.send(f"Wyniki: {' + '.join(map(str, results))} = {total}")

@bot.command()
async def moneta(ctx):
    import random
    result = random.choice(["Orzeł", "Reszka"])
    await ctx.send(f"Rzut monetą: {result}")

@bot.command()
async def info(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    await ctx.send(f"ID: {member.id}, Nazwa: {member.display_name}")

@bot.command()
async def help(ctx):
    help_text = """**BOT COMMANDS:**
**Właściciel:** !addmod @user, !removemod @user
**Moderacja:** !ban @user, !mute @user, !unmute @user, !clear 10
**Fun:** !czesc, !szynszyl, !losuj, !kostka, !moneta
**Info:** !info, !ping"""
    await ctx.send(help_text)

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("DISCORD_TOKEN not found!")
        exit(1)
    try:
        print("Starting bot...")
        bot.run(token)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
