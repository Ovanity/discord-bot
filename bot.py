import discord
from discord import app_commands
import os
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ID de ton serveur Discord (clic droit sur l’icône du serveur → Copier l’identifiant)
GUILD_ID = discord.Object(id=1403442529357267036)

# Définition des intentions du bot
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user.name}")

    # Copier les commandes globales vers ton serveur de test (instantané)
    tree.copy_global_to(guild=GUILD_ID)

    # Synchronisation immédiate avec ton serveur (slash command dispo en 2-5 sec)
    await tree.sync(guild=GUILD_ID)
    print("🔧 Slash commands synchronisées dans ton serveur (guild-only)")

    # Enregistrement global (apparition sous 15-60 min)
    await tree.sync()
    print("🌐 Slash commands synchronisées globalement")


# Slash command disponible dans ton serveur uniquement pour l’instant
@tree.command(name="ping", description="Répond pong yeah yeah ça fonctionne", guild=GUILD_ID)
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message("pong")


# Lancer le bot
client.run(TOKEN)