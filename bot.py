import discord
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user.name}")
    await tree.sync()  # 👈 enregistre les slash commands
    print("🔧 Slash commands synchronisées")

@tree.command(name="ping", description="Répond pong")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")

client.run(TOKEN)