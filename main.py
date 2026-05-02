import discord
import asyncio
import os
import random
import sys
import json
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
from PIL import Image, ImageDraw
import io

# --- SYSTÈME KEEP ALIVE POUR RENDER ---
app = Flask('')
@app.route('/')
def home(): 
    return "L'ange Angel est bien en ligne !"

def run(): 
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()
    print("✅ Keep-alive Flask server started on port 8080", flush=True)
    sys.stdout.flush()

# --- CONFIGURATION DU BOT ---
intents = discord.Intents.all()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
client = commands.Bot(command_prefix="!", intents=intents)

# --- CONFIGURATION DES SALONS ---
ID_SALON_WELCOME = 1499019793318285343  
ID_SALON_LEVELUP = 1499039238015160390  
ID_SALON_RULES = 1499012460772851793
ID_SERVEUR = 1499002734748111039  

# LISTE EXACTE DES RÔLES
LEVEL_ROLES = {
    "91": "lvl 91-100 ~ Legendary Art Deity 👑🌟",
    "81": "lvl 81-90 ~ Galaxy Master Illustrator 🔮✨",
    "71": "lvl 71-80 ~ Midnight Concept Maker 🌌📜",
    "61": "lvl 61-70 ~ Aqua Vision Artist 🌊💎",
    "51": "lvl 51-60 ~ Sky Palette Poet 🫧🎨",
    "41": "lvl 41-50 ~ Neon Art Sprite 💖⚡",
    "31": "lvl 31-40 ~ Blossom Illustrator 🌸🖋️",
    "21": "lvl 21-30 ~ Velvet Canvas Dreamer 🍰🖌️",
    "16": "lvl 16-20 ~ Passion Painter 🔥🎨",
    "11": "lvl 11-15 ~ Curious Line Crafter 🍊📏",
    "6":  "lvl 6-10 ~ Honey Sketchling 🍯✏️",
    "0":  "lvl 1-5 ~ Tiny Doodle Bean 🌼🖍️"
}

# --- GESTION DE LA SAUVEGARDE DES DONNÉES ---
DATA_FILE = "users_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Erreur de lecture du fichier JSON: {e}", flush=True)
            return {}
    return {}

def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(user_data, f, indent=4)
    except Exception as e:
        print(f"⚠️ Erreur de sauvegarde JSON: {e}", flush=True)

# On charge les données au démarrage
user_data = load_data()

# --- FONCTIONS UTILITAIRES ---
def get_rank_name(level):
    for threshold in sorted([int(k) for k in LEVEL_ROLES.keys()], reverse=True):
        if level >= threshold:
            return LEVEL_ROLES[str(threshold)]
    return LEVEL_ROLES["0"]

async def update_member_roles(member, level):
    """Assigne le bon rôle et supprime les anciens rôles de niveau obsolètes"""
    rank_name = get_rank_name(level)
    role = discord.utils.get(member.guild.roles, name=rank_name)
    
    if role and role not in member.roles:
        try:
            # On cherche les anciens rôles à retirer
            to_remove = [r for r in member.roles if r.name in LEVEL_ROLES.values() and r.name != rank_name]
            if to_remove:
                await member.remove_roles(*to_remove)
            
            await member.add_roles(role)
            print(f"Rôle {rank_name} attribué à {member.name}", flush=True)
        except discord.Forbidden:
            print(f"ERREUR: Angel n'a pas les permissions pour modifier les rôles de {member.name}.", flush=True)

def create_xp_progress_image(current_xp, xp_needed, username):
    """Génère la barre d'XP avec un dégradé précis du jaune vers le rose"""
    width, height = 400, 50
    img = Image.new('RGB', (width, height), color=(40, 40, 40))
    draw = ImageDraw.Draw(img)
    
    bar_padding = 10
    bar_height = 30
    bar_y = (height - bar_height) // 2
    
    # Dessin de la barre de fond grise
    draw.rectangle(
        [(bar_padding, bar_y), (width - bar_padding, bar_y + bar_height)],
        fill=(60, 60, 60),
        outline=(150, 150, 150),
        width=2
    )
    
    # Calcul précis du pourcentage de remplissage
    progress = max(0.0, min(1.0, current_xp / xp_needed))
    bar_width = width - (2 * bar_padding) - 4
    filled_width = max(0, int(bar_width * progress))
    
    if filled_width > 0:
        for x in range(filled_width):
            ratio = x / max(filled_width, 1)
            # Dégradé Jaune -> Rose
            r = int(255)
            g = int(255 - (ratio * 150))
            b = int(ratio * 180)
            
            draw.line([(bar_padding + 2 + x, bar_y + 2), (bar_padding + 2 + x, bar_y + bar_height - 2)], fill=(r, g, b), width=1)
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return discord.File(img_bytes, filename='xp_bar.png')

# --- ÉVÉNEMENTS DU BOT ---
@client.event
async def on_ready():
    try:
        print(f"📡 Connexion établie avec {client.user.name}", flush=True)
        await client.tree.sync()
        try:
            guild = discord.Object(id=ID_SERVEUR)
            await client.tree.sync(guild=guild)
            print(f"✅ Commandes synchronisées pour le serveur {ID_SERVEUR}", flush=True)
        except Exception as e:
            print(f"⚠️ Erreur lors de la synchronisation serveur: {e}", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"⚠️ Erreur on_ready: {e}", flush=True)

@client.event
async def on_member_join(member):
    channel = client.get_channel(ID_SALON_WELCOME)
    if channel:
        msg = (f"Hello {member.mention} ! ╰ ( ≧ ⩊ ≦ ) ╯\n"
               f"Welcome to our community ☆ : . 。 o ( ≧ ▽ ≦ ) o . . : ☆\n\n"
               f"Make sure to read the rules in <#{ID_SALON_RULES}> ! Have fun and don't forget to keep it cool ╰(°▽°)╯")
        try:
            with open('welcome.jpg', 'rb') as f:
                await channel.send(content=msg, file=discord.File(f))
        except:
            await channel.send(msg)

@client.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    user_id = str(message.author.id)
    
    # Initialisation
    if user_id not in user_data:
        user_data[user_id] = {"xp": 0, "level": 0}

    # Gain de 10 XP
    user_data[user_id]["xp"] += 10
    current_xp = user_data[user_id]["xp"]
    
    # Recalcul dynamique du niveau basé uniquement sur l'XP
    current_lvl = user_data[user_id]["level"]
    new_lvl = current_xp // 100

    # Attribution du bon rôle
    await update_member_roles(message.author, new_lvl)

    # --- MESSAGE DE LEVEL UP ---
    if new_lvl > current_lvl:
        user_data[user_id]["level"] = new_lvl
        channel = client.get_channel(ID_SALON_LEVELUP)
        if channel:
            rank_name = get_rank_name(new_lvl)
            lvl_msg = f"GG {message.author.mention}, you reached **level {new_lvl}** ! ✨ You unlocked the rank **{rank_name}** !"
            img = random.choice(['level_a.jpg', 'level_b.jpg'])
            try:
                with open(img, 'rb') as f:
                    await channel.send(content=lvl_msg, file=discord.File(f))
            except:
                await channel.send(lvl_msg)

    save_data()
    await client.process_commands(message)

# --- COMMANDES ---
@client.tree.command(name="level", description="Affiche votre niveau et votre rang")
@discord.app_commands.guilds(discord.Object(id=ID_SERVEUR))
async def level_command(interaction: discord.Interaction):
    try:
        user_id = str(interaction.user.id)
        
        if user_id not in user_data:
            user_data[user_id] = {"xp": 0, "level": 0}
            save_data()
        
        current_xp = user_data[user_id]["xp"]
        
        # Le niveau est TOUJOURS recalculé pour être 100% exact
        current_level = current_xp // 100
        user_data[user_id]["level"] = current_level
        save_data()
        
        # 100 XP nécessaires par niveau
        xp_needed = 100
        xp_in_level = current_xp % xp_needed
        
        # Mise à jour du rôle en direct si nécessaire
        await update_member_roles(interaction.user, current_level)
        
        rank_name = get_rank_name(current_level)
        roles = [role.name for role in interaction.user.roles if role.name != "@everyone"]
        roles_str = ", ".join(roles) if roles else "Aucun rôle"
        
        xp_bar_file = create_xp_progress_image(xp_in_level, xp_needed, interaction.user.name)
        
        embed = discord.Embed(
            title=f"📊 Niveau de {interaction.user.name}",
            description=f"**Niveau :** {current_level}\n**Rang Système :** {rank_name}",
            color=discord.Color.gold()
        )
        embed.add_field(name="📍 Vos rôles Discord", value=roles_str, inline=False)
        embed.add_field(name="⚡ Progression XP", value=f"{xp_in_level}/{xp_needed} XP (Total: {current_xp})", inline=False)
        embed.set_image(url="attachment://xp_bar.png")
        embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)
        
        await interaction.response.send_message(embed=embed, file=xp_bar_file)
    except Exception as e:
        print(f"❌ ERREUR DANS /level: {e}", flush=True)
        try:
            await interaction.response.send_message(f"❌ Erreur: {str(e)[:100]}")
        except:
            pass

async def main():
    keep_alive()
    async with client:
        token = os.getenv('TOKEN')
        if not token:
            print("❌ ERREUR: Variable d'environnement 'TOKEN' manquante!", flush=True)
            return
        await client.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Bot arrêté par l'utilisateur", flush=True)
    except Exception as e:
        print(f"❌ Erreur fatale: {e}", flush=True)