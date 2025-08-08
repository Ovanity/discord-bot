import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # Charge les variables d'environnement depuis .env
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user.name}")

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

bot.run(TOKEN)