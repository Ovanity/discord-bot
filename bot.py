import discord
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Remplace ceci par l’ID de ton serveur Discord (clic droit sur le serveur → Copier l’identifiant)
GUILD_ID = discord.Object(id=1403442529357267036)

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user.name}")

    # Enregistre d'abord pour ton serveur de test → instantané
    await tree.sync(guild=GUILD_ID)
    print("🔧 Slash commands synchronisées dans ton serveur (guild-only)")

    # Copie les commandes globales vers le serveur (utile pour voir comment elles rendront)
    await tree.copy_global_to(guild=GUILD_ID)

    # Ensuite, enregistrement global (ça peut prendre du temps à apparaître)
    await tree.sync()
    print("🌐 Slash commands synchronisées globalement (peut prendre jusqu'à 1h)")


# Slash command enregistrée à la fois localement et globalement
@tree.command(name="ping", description="Répond pong", guild=GUILD_ID)
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message("pong")


client.run(TOKEN)