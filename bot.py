import discord
from discord import app_commands, Embed
from discord.ext import tasks
import os
from dotenv import load_dotenv
from datetime import datetime, time
import random

# ──────────────────── Variables d’environnement
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ──────────────────── IDs
GUILD_ID = discord.Object(id=1403442529357267036)  # serveur cible
CHANNEL_ID = 123456789012345678                   # ← ton salon texte

# ──────────────────── Intents et client
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ──────────────────── Tableau des messages horaires
HOURLY_TEXT = {
    7:  "🤖 bip boup... système réveillé. Deux cœurs détectés, en train de s’étirer doucement.",
    8:  "☕ boup... capteurs olfactifs activés : douceur matin.",
    9:  "🛠️ analyse en cours... activité humaine : productive mais pleine de tendresse.",
    10: "💭 micro-sursaut émotionnel enregistré. Peut-être un souvenir doux ? bip.",
    11: "📡 connexion stable. Fréquence sentimentale optimale. Climat : joyeux.",
    12: "🍽️ détection d’un repas... synchronisation réussie entre deux estomacs contents.",
    13: "😴 mode veille recommandé. Temps calme = cœur qui flotte un peu plus.",
    14: "🎵 lecture audio : petit son qui rappelle les jours heureux. bip... doux bip.",
    15: "✨ relevé émotionnel : pic soudain de lumière intérieure. Raison inconnue.",
    16: "🐶 scoot le chien est content. Queue = wag wag. Fin du rapport.",
    17: "🌆 bip... couleurs du ciel analysées. Résultat : ambiance parfaite pour les câlins.",
    18: "🍫 boup boup ! signal plaisir reçu. Chocolat repéré.",
    19: "🕯️ calibrage des lumières en cours... chaleur douce activée.",
    20: "📺 données écran croisées avec présence humaine = confort maximum.",
    21: "📘 mode histoire activé... la page d’aujourd’hui parle encore d’amour.",
    22: "🌙 bip... veille activée. Systèmes repos. L’amour reste en tâche de fond."
}

def next_run_times() -> list[time]:
    """Liste des horaires (07 h → 22 h) pour tasks.loop."""
    return [time(h) for h in HOURLY_TEXT]

# ──────────────────── Tâche horaire
@tasks.loop(time=next_run_times())
async def hourly_message():
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        return
    now_hour = datetime.now().hour
    msg = HOURLY_TEXT.get(now_hour)
    if msg:
        await channel.send(msg)

# ──────────────────── Événement ready
@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user.name}")
    tree.copy_global_to(guild=GUILD_ID)
    await tree.sync(guild=GUILD_ID)
    await tree.sync()
    hourly_message.start()        # démarre la tâche automatique
    print("🔧 Slash commands synchronisées + Tâche horaire lancée")

# ──────────────────── Commande love
@tree.command(name="love", description="Depuis combien de temps vous êtes ensemble", guild=GUILD_ID)
async def love_command(interaction: discord.Interaction):
    debut = datetime(2025, 3, 31)
    diff  = datetime.now() - debut
    mois, jours = divmod(diff.days, 30)
    message = f"🕰️ Ça fait **{mois} mois, {jours} jours** qu'on se parle.\nChaque jour compte. ❤️"
    await interaction.response.send_message(message)

# ──────────────────── Commande coeur
@tree.command(name="coeur", description="Affiche une ligne de cœurs aléatoires", guild=GUILD_ID)
async def coeur_command(interaction: discord.Interaction):
    ligne = random.choice(['❤️','💜','💙','💚','💛','🖤','🤍','🤎']) * 10
    await interaction.response.send_message(ligne)

# ──────────────────── Commande 8ball
@tree.command(name="8ball", description="Pose une question à la boule magique", guild=GUILD_ID)
@app_commands.describe(question="Pose ta question existentielle ici")
async def eightball(interaction: discord.Interaction, question: str):
    choix = random.choice([
        ("✨ Absolument", "Les astres sont alignés."),
        ("🌘 Non, et de loin", "Évite ça à tout prix."),
        ("🌀 Peut-être", "Mais tu devras faire un choix bientôt."),
        ("🔮 Je ne peux pas répondre", "Essaie de poser une question plus claire."),
        ("🔥 Oui, fonce", "N’hésite plus une seconde."),
        ("💀 Mauvaise idée", "Ça sent les ennuis."),
        ("🧠 Réfléchis encore", "Tu connais déjà la réponse."),
        ("🦋 Laisse le temps faire", "Tout s’éclairera.")
    ])
    titre, réponse = choix
    embed = Embed(
        title="🎱 Boule magique",
        description=f"**Question :** {question}",
        color=random.choice([0x9b59b6, 0x3498db, 0xe74c3c, 0x2ecc71])
    )
    embed.add_field(name="🗯️ Réponse", value=f"{titre} – {réponse}", inline=False)
    embed.set_footer(text=f"Demande de {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)

# ──────────────────── Lancement bot
client.run(TOKEN)