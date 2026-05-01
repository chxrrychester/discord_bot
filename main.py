import discord
import asyncio
import os
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- SYSTÈME KEEP ALIVE POUR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "L'ange Angel est bien en ligne !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# --------------------------------------

# Configuration des intents (indispensable pour les membres)
intents = discord.Intents.all()
intents.members = True 

client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print(f"L'ange {client.user.name} est réveillé et en ligne !")

@client.event
async def on_member_join(member):
    # Message de bienvenue dans un salon spécifique (remplace ID_DU_SALON)
    # ou en message privé comme tu l'avais fait :
    try:
        await member.send(f"Hello {member.mention} ! Welcome to our community...")
        # Tu peux ajouter ici l'envoi de ton image de bienvenue
    except discord.Forbidden:
        print(f"Impossible d'envoyer un MP à {member.name}")

# Système de niveaux (Exemple simplifié)
@client.event
async def on_message(message):
    if message.author.bot:
        return
    # Ici, tu devrais normalement avoir une base de données pour les niveaux
    await client.process_commands(message)

async def main():
    # Lancement du serveur web pour Render
    keep_alive()
    
    async with client:
        # Remplace 'TON_TOKEN' par ton vrai token si tu testes en local
        # Ou utilise os.getenv('TOKEN') pour plus de sécurité
        await client.start(os.getenv('TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())