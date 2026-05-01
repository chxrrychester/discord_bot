import discord
import asyncio
import os
import random
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

# --- CONFIGURATION DU BOT ---
intents = discord.Intents.all()
intents.members = True 
client = commands.Bot(command_prefix="!", intents=intents)

# --- CONFIGURATION DES SALONS (Tes IDs fournis) ---
ID_SALON_WELCOME = 1499019793318285343  # Salon #Welcome
ID_SALON_LEVELUP = 1499039238015160390  # Salon #level-up
ID_SALON_RULES = 1499012460772851793  # Salon #Rules (Vérifie cet ID)

# Liste exacte des noms de rôles pour la correspondance et le nettoyage
LEVEL_ROLES = [
    "lvl 91-100 ~ Legendary Art Deity 🌌 ✨",
    "lvl 81-90 ~ Galaxy Master Illustrator 🌌 🎨",
    "lvl 71-80 ~ Midnight Concept Maker 🌑 ✍️",
    "lvl 61-70 ~ Aqua Vision Artist 🌊 🎨",
    "lvl 51-60 ~ Sky Palette Poet 🫧 🎨",
    "lvl 41-50 ~ Neon Art Sprite 💖 ⚡",
    "lvl 31-40 ~ Blossom Illustrator 🌸 🎨",
    "lvl 21-30 ~ Velvet Canvas Dreamer 🎨 ☁️",
    "lvl 16-20 ~ Passion Painter 🔥 🎨",
    "lvl 11-15 ~ Curious Line Crafter 🧐 🖋️",
    "lvl 6-10 ~ Honey Sketchling 🧁 🖋️",
    "lvl 1-5 ~ Tiny Doodle Bean 🌸 🖋️"
]

# Base de données d'XP temporaire
user_data = {} 

def get_rank_name(level):
    if level >= 91: return LEVEL_ROLES[0]
    elif level >= 81: return LEVEL_ROLES[1]
    elif level >= 71: return LEVEL_ROLES[2]
    elif level >= 61: return LEVEL_ROLES[3]
    elif level >= 51: return LEVEL_ROLES[4]
    elif level >= 41: return LEVEL_ROLES[5]
    elif level >= 31: return LEVEL_ROLES[6]
    elif level >= 21: return LEVEL_ROLES[7]
    elif level >= 16: return LEVEL_ROLES[8]
    elif level >= 11: return LEVEL_ROLES[9]
    elif level >= 6: return LEVEL_ROLES[10]
    else: return LEVEL_ROLES[11]

@client.event
async def on_ready():
    print(f"L'ange {client.user.name} est réveillé et prêt à donner des grades !")

@client.event
async def on_member_join(member):
    channel = client.get_channel(ID_SALON_WELCOME)
    if channel:
        msg = (f"Hello {member.mention} ! ╰ ( ≧ ⩊ ≦ ) ╯\n"
               f"Welcome to our community ☆ : . 。 o ( ≧ ▽ ≦ ) o . . : ☆\n\n"
               f"Make sure to read the rules in <#{ID_SALON_RULES}> ! Have fun and don't forget to keep it cool ╰(°▽°)╯")
        try:
            with open('welcome.jpg', 'rb') as f:
                picture = discord.File(f)
                await channel.send(content=msg, file=picture)
        except:
            await channel.send(msg)

@client.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    user_id = str(message.author.id)
    if user_id not in user_data:
        user_data[user_id] = {"xp": 0, "level": 0}

    # Gain d'XP
    user_data[user_id]["xp"] += 10
    current_xp = user_data[user_id]["xp"]
    current_lvl = user_data[user_id]["level"]
    new_lvl = current_xp // 100

    # Si l'utilisateur change de niveau
    if new_lvl > current_lvl:
        user_data[user_id]["level"] = new_lvl
        rank_name = get_rank_name(new_lvl)
        
        # 1. Message de félicitations
        channel = client.get_channel(ID_SALON_LEVELUP)
        if channel:
            lvl_msg = f"GG {message.author.mention}, you reached **level {new_lvl}** ! ✨ You unlocked the rank **{rank_name}** !"
            img_name = random.choice(['level_a.jpg', 'level_b.jpg'])
            try:
                with open(img_name, 'rb') as f:
                    await channel.send(content=lvl_msg, file=discord.File(f))
            except:
                await channel.send(lvl_msg)

        # 2. Gestion des Rôles
        new_role = discord.utils.get(message.guild.roles, name=rank_name)
        if new_role:
            try:
                # On retire d'abord les anciens rôles de niveaux pour éviter de les accumuler
                roles_to_remove = [r for r in message.author.roles if r.name in LEVEL_ROLES]
                if roles_to_remove:
                    await message.author.remove_roles(*roles_to_remove)
                
                # On ajoute le nouveau rôle
                await message.author.add_roles(new_role)
                print(f"Rôle {rank_name} donné à {message.author.name}")
            except discord.Forbidden:
                print(f"ERREUR : Je ne peux pas donner le rôle. Vérifie que mon rôle 'Angel' est TOUT EN HAUT de la liste des rôles.")
            except Exception as e:
                print(f"Erreur imprévue : {e}")

    await client.process_commands(message)

async def main():
    keep_alive()
    async with client:
        token = os.getenv('TOKEN') or "TON_TOKEN_ICI"
        await client.start(token)

if __name__ == "__main__":
    asyncio.run(main())