import discord
import asyncio
import os
import random
from discord.ext import commands
from discord import app_commands
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

# --- CONFIGURATION DES SALONS ---
ID_SALON_WELCOME = 1499019793318285343  
ID_SALON_LEVELUP = 1499039238015160390  
ID_SALON_RULES = 1499012460772851793    

# LISTE EXACTE DES RÔLES (Basée sur ton image 675855.png)
# Attention : Les rôles 41-50 et 51-60 n'ont pas "lvl" au début sur ton screen !
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

user_data = {} 

def get_rank_name(level):
    # On cherche le palier le plus haut atteint
    for threshold in sorted([int(k) for k in LEVEL_ROLES.keys()], reverse=True):
        if level >= threshold:
            return LEVEL_ROLES[str(threshold)]
    return LEVEL_ROLES["0"]

def create_xp_bar(current_xp, xp_needed, length=20):
    """Crée une jauge d'XP visuelle"""
    filled = int((current_xp / xp_needed) * length)
    bar = "█" * filled + "░" * (length - filled)
    return f"`{bar}` {current_xp}/{xp_needed} XP"

@client.event
async def on_ready():
    await client.tree.sync()
    print(f"L'ange {client.user.name} est prêt ! Rôles configurés.")

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
    if user_id not in user_data:
        # On initialise au niveau 0
        user_data[user_id] = {"xp": 0, "level": 0}

    # Gain d'XP
    user_data[user_id]["xp"] += 10
    current_xp = user_data[user_id]["xp"]
    current_lvl = user_data[user_id]["level"]
    new_lvl = current_xp // 100

    rank_name = get_rank_name(new_lvl)
    
    # --- LOGIQUE DE GRADE ---
    # On vérifie si l'utilisateur a déjà le rôle correspondant à son rang actuel
    role = discord.utils.get(message.guild.roles, name=rank_name)
    if role and role not in message.author.roles:
        try:
            # On retire les anciens rôles de la liste LEVEL_ROLES
            to_remove = [r for r in message.author.roles if r.name in LEVEL_ROLES.values()]
            if to_remove:
                await message.author.remove_roles(*to_remove)
            
            # On ajoute le nouveau rôle (même au niveau 0/1)
            await message.author.add_roles(role)
            print(f"Rôle {rank_name} attribué à {message.author.name}")
        except discord.Forbidden:
            print("ERREUR : Angel n'a pas les permissions. Monte le rôle 'Angel' tout en haut !")

    # --- MESSAGE DE LEVEL UP ---
    if new_lvl > current_lvl:
        user_data[user_id]["level"] = new_lvl
        channel = client.get_channel(ID_SALON_LEVELUP)
        if channel:
            lvl_msg = f"GG {message.author.mention}, you reached **level {new_lvl}** ! ✨ You unlocked the rank **{rank_name}** !"
            img = random.choice(['level_a.jpg', 'level_b.jpg'])
            try:
                with open(img, 'rb') as f:
                    await channel.send(content=lvl_msg, file=discord.File(f))
            except:
                await channel.send(lvl_msg)

    await client.process_commands(message)

@client.tree.command(name="level", description="Affiche votre niveau et votre rang")
async def level_command(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    
    if user_id not in user_data:
        user_data[user_id] = {"xp": 0, "level": 0}
    
    current_level = user_data[user_id]["level"]
    current_xp = user_data[user_id]["xp"]
    xp_needed = 100
    xp_in_level = current_xp % xp_needed
    
    rank_name = get_rank_name(current_level)
    xp_bar = create_xp_bar(xp_in_level, xp_needed)
    
    embed = discord.Embed(
        title=f"Niveau de {interaction.user.name}",
        description=f"**Niveau :** {current_level}\n**Rang :** {rank_name}",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="Progression XP",
        value=xp_bar,
        inline=False
    )
    embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)
    
    await interaction.response.send_message(embed=embed)

async def main():
    keep_alive()
    async with client:
        token = os.getenv('TOKEN') or "TON_TOKEN_ICI"
        await client.start(token)

if __name__ == "__main__":
    asyncio.run(main())