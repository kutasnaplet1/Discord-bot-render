import discord
from discord.ext import commands
import os
import threading
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

@bot.event
async def on_ready():
    print(f'Bot online: {bot.user}')
    print(f'Servers: {len(bot.guilds)}')

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command()
async def reset(ctx):
    if ctx.author.id == ctx.guild.owner_id:
        await ctx.send("Bot zresetowany - wszystkie komendy usunięte. Można budować od nowa.")
    else:
        await ctx.send("Tylko właściciel serwera może resetować bota.")

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
        print("Starting simple Discord bot...")
        bot.run(token)
    except Exception as e:
        print(f"Bot error: {e}")
        exit(1)
