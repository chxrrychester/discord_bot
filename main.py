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

# --- CONFIGURATION DES SALONS ---
# J'ai utilisé les IDs que tu avais insérés dans ton dernier message
ID_SALON_WELCOME = 1499019793318285343  # Salon #Welcome
ID_SALON_LEVELUP = 1499039238015160390  # Salon #level-up
ID_SALON_RULES = 1499012460772851793  # Salon #rules

# Base de données temporaire pour l'XP
user_data = {} 

def get_rank(level):
    if level >= 91: return "lvl 91-100 ~ Legendary Art Deity 🌌 ✨"
    elif level >= 81: return "lvl 81-90 ~ Galaxy Master Illustrator 🌌 🎨"
    elif level >= 71: return "lvl 71-80 ~ Midnight Concept Maker 🌑 ✍️"
    elif level >= 61: return "lvl 61-70 ~ Aqua Vision Artist 🌊 🎨"
    elif level >= 51: return "lvl 51-60 ~ Sky Palette Poet 🫧 🎨"
    elif level >= 41: return "lvl 41-50 ~ Neon Art Sprite 💖 ⚡"
    elif level >= 31: return "lvl 31-40 ~ Blossom Illustrator 🌸 🎨"
    elif level >= 21: return "lvl 21-30 ~ Velvet Canvas Dreamer 🎨 ☁️"
    elif level >= 16: return "lvl 16-20 ~ Passion Painter 🔥 🎨"
    elif level >= 11: return "lvl 11-15 ~ Curious Line Crafter 🧐 🖋️"
    elif level >= 6: return "lvl 6-10 ~ Honey Sketchling 🍯 🖋️"
    else: return "lvl 1-5 ~ Tiny Doodle Bean 🌸 🖋️"

@client.event
async def on_ready():
    print(f"L'ange {client.user.name} est réveillé !")

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
        except FileNotFoundError:
            await channel.send(msg)

@client.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    user_id = str(message.author.id)
    if user_id not in user_data:
        user_data[user_id] = {"xp": 0, "level": 0}

    # Gain d'XP (10 par message)
    user_data[user_id]["xp"] += 10
    current_xp = user_data[user_id]["xp"]
    current_lvl = user_data[user_id]["level"]

    # Calcul du niveau (1 niveau tous les 100 XP)
    new_lvl = current_xp // 100

    if new_lvl > current_lvl:
        user_data[user_id]["level"] = new_lvl
        rank_name = get_rank(new_lvl)
        
        channel = client.get_channel(ID_SALON_LEVELUP)
        if channel:
            lvl_msg = f"GG {message.author.mention}, you reached **level {new_lvl}** ! ✨ You unlocked the rank **{rank_name}** !"
            
            # Alternance des images (level_a.jpg ou level_b.jpg)
            img_name = random.choice(['level_a.jpg', 'level_b.jpg'])
            try:
                with open(img_name, 'rb') as f:
                    picture = discord.File(f)
                    await channel.send(content=lvl_msg, file=picture)
            except FileNotFoundError:
                await channel.send(lvl_msg)

        # Attribution automatique du rôle
        role = discord.utils.get(message.guild.roles, name=rank_name)
        if role:
            try:
                await message.author.add_roles(role)
            except discord.Forbidden:
                print(f"Erreur : Je n'ai pas les permissions pour donner le rôle {rank_name}")

    await client.process_commands(message)

async def main():
    keep_alive()
    async with client:
        # Priorité à la variable d'environnement 'TOKEN' de Render
        token = os.getenv('TOKEN') or "TON_TOKEN_ICI"
        await client.start(token)

if __name__ == "__main__":
    asyncio.run(main())