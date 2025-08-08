import os
import random
import asyncio
import logging
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import aiohttp
import discord
from discord import app_commands, Embed
from discord.ext import tasks
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta  # pip install python-dateutil

# ──────────────────── Config de base
load_dotenv()
TOKEN: str | None = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN manquant dans l'environnement")

GUILD_ID = discord.Object(id=1403442529357267036)
CHANNEL_ID = 123456789012345678
FACT_CHANNEL_ID = CHANNEL_ID

PARIS = ZoneInfo("Europe/Paris")

# ──────────────────── Logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("luvbot")

# ──────────────────── Intents et client
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

_started = False  # évite les doubles start sur reconnexion

# ──────────────────── Messages horaires
HOURLY_TEXT: dict[int, str] = {
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
    # heures Europe/Paris correctes pour tasks.loop
    return [time(h, tzinfo=PARIS) for h in HOURLY_TEXT]

# ──────────────────── Tâche horaire
@tasks.loop(time=next_run_times())
async def hourly_message() -> None:
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        return
    now_hour = datetime.now(PARIS).hour
    msg = HOURLY_TEXT.get(now_hour)
    if msg:
        await channel.send(msg)

# ──────────────────── Tâche pour faits aléatoires
async def envoyer_fait_bienness() -> None:
    await client.wait_until_ready()
    horaires = [time(h, 30, tzinfo=PARIS) for h in range(7, 22, 2)]
    session_timeout = aiohttp.ClientTimeout(total=6)

    while not client.is_closed():
        now = datetime.now(PARIS)
        prochain: time | None = next((h for h in horaires if now.timetz() < h), None)
        next_run = datetime.combine(
            (now.date() + timedelta(days=1)) if not prochain else now.date(),
            horaires[0] if not prochain else prochain,
            tzinfo=PARIS
        )
        wait_sec = max(0, int((next_run - now).total_seconds()))
        log.info("Prochain fait à %s dans %ss", next_run.time().strftime("%H:%M:%S"), wait_sec)
        try:
            await asyncio.sleep(wait_sec)
        except asyncio.CancelledError:
            log.info("Tâche 'faits' annulée")
            return

        try:
            async with aiohttp.ClientSession(timeout=session_timeout) as session:
                async with session.get(
                    "https://uselessfacts.jsph.pl/random.json?language=fr",
                    headers={"Accept": "application/json"}
                ) as resp:
                    if resp.status != 200:
                        raise RuntimeError(f"HTTP {resp.status}")
                    data = await resp.json()
                    fait = data.get("text") or "Rien à déclarer."
            channel = client.get_channel(FACT_CHANNEL_ID)
            if channel:
                await channel.send(f"📚 Fait aléatoire : {fait}")
        except asyncio.CancelledError:
            raise
        except Exception as e:
            log.warning("Erreur fetch fait: %s", e)

# ──────────────────── Événement ready
@client.event
async def on_ready() -> None:
    global _started
    log.info("Connecté en tant que %s", client.user.name if client.user else "unknown")
    if not _started:
        # sync une fois côté guilde pour vitesse, puis global si tu veux
        tree.copy_global_to(guild=GUILD_ID)
        await tree.sync(guild=GUILD_ID)
        # await tree.sync()  # optionnel, plus lent, à activer si tu veux du global
        if not hourly_message.is_running():
            hourly_message.start()
        asyncio.create_task(envoyer_fait_bienness())
        _started = True
        log.info("Slash commands synchronisées + Tâches démarrées")

# ──────────────────── Slash commands
@tree.command(name="love", description="Depuis combien de temps vous êtes ensemble", guild=GUILD_ID)
async def love_command(interaction: discord.Interaction) -> None:
    debut = datetime(2025, 3, 31, tzinfo=PARIS)
    now = datetime.now(PARIS)
    delta = relativedelta(now, debut)
    message = (
        f"🕰️ Ça fait {delta.years} ans, {delta.months} mois, {delta.days} jours."
        "\nChaque jour compte. ❤️"
    )
    await interaction.response.send_message(message)

@tree.command(name="coeur", description="Affiche une ligne de cœurs aléatoires", guild=GUILD_ID)
async def coeur_command(interaction: discord.Interaction) -> None:
    ligne = random.choice(['❤️','💜','💙','💚','💛','🖤','🤍','🤎']) * 10
    await interaction.response.send_message(ligne)

@tree.command(name="8ball", description="Pose une question à la boule magique", guild=GUILD_ID)
@app_commands.describe(question="Pose ta question existentielle ici")
async def eightball(interaction: discord.Interaction, question: str) -> None:
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
    titre, reponse = choix
    embed = Embed(
        title="🎱 Boule magique",
        description=f"**Question :** {question}",
    )
    embed.add_field(name="🗯️ Réponse", value=f"{titre} — {reponse}", inline=False)
    embed.set_footer(text=f"Demande de {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)

# ──────────────────── Lancement bot
if __name__ == "__main__":
    client.run(TOKEN)
