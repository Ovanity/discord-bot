import discord
from discord import app_commands
from discord import Embed
import os
from dotenv import load_dotenv
from datetime import datetime
import random

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



# Commande romantique /depuis
@tree.command(name="love", description="Depuis combien de temps vous êtes ensemble", guild=GUILD_ID)
async def depuis_command(interaction: discord.Interaction):
    debut = datetime(2025, 3, 31)
    maintenant = datetime.now()
    difference = maintenant - debut

    jours_total = difference.days
    mois = jours_total // 30
    jours = jours_total % 30

    message = (
        f"🕰️ Ça fait **{mois} mois, {jours} jours** qu'on se parle.\n"
        f"Chaque jour compte. ❤️"
    )

    # 🔓 Visible par tout le monde
    await interaction.response.send_message(message)


@tree.command(name="coeur", description="Affiche une ligne de cœurs aléatoires", guild=GUILD_ID)
async def coeur_command(interaction: discord.Interaction):
    emojis = ['❤️', '💜', '💙', '💚', '💛', '🖤', '🤍', '🤎']
    e = random.choice(emojis)
    ligne = e * 10  # 10 cœurs sur une ligne
    await interaction.response.send_message(ligne)

@tree.command(name="8ball", description="Pose une question à la boule magique", guild=GUILD_ID)
@app_commands.describe(question="Pose ta question existentielle ici")
async def eightball(interaction: discord.Interaction, question: str):
    réponses = [
        ("✨ Absolument", "Les astres sont alignés."),
        ("🌘 Non, et de loin", "Évite ça à tout prix."),
        ("🌀 Peut-être", "Mais tu devras faire un choix bientôt."),
        ("🔮 Je ne peux pas répondre", "Essaie de poser une question plus claire."),
        ("🔥 Oui, fonce", "N’hésite plus une seconde."),
        ("💀 Mauvaise idée", "Ça sent les ennuis."),
        ("🧠 Réfléchis encore", "Tu connais déjà la réponse."),
        ("🦋 Laisse le temps faire", "Tout s’éclairera.")
    ]

    titre, réponse = random.choice(réponses)

    embed = Embed(
        title="🎱 Boule magique",
        description=f"**Question :** {question}",
        color=random.choice([0x9b59b6, 0x3498db, 0xe74c3c, 0x2ecc71])
    )
    embed.add_field(name="🗯️ Réponse", value=f"{titre} – {réponse}", inline=False)
    embed.set_footer(text=f"Demande de {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)

# Lancer le bot
client.run(TOKEN)