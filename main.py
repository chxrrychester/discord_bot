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
def home(): return "L'ange Angel est bien en ligne !"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURATION DU BOT ---
intents = discord.Intents.all()
intents.members = True 
client = commands.Bot(command_prefix="!", intents=intents)

# Remplace ces ID par les tiens (Clic droit sur le salon -> Copier l'ID)
 = 123456789012345678  # Salon #Welcome
ID_SALON_LEVELUP = 123456789012345678  # Salon #level-up

# Base de données très simple (en mémoire) pour l'XP
# Note: Si le bot redémarre sur Render, l'XP revient à zéro. 
# Pour garder l'XP à vie, il faudrait une vraie base de données.
user_data = {} 

def get_rank(level):
    if level >= 91: return "lvl 91-100 ~ Legendary Art Deity 🌌 ✨"
    if level >= 81: return "lvl 81-90 ~ Galaxy Master Illustrator 🌌 🎨"
    if level >= 71: return "lvl 71-80 ~ Midnight Concept Maker 🌑 ✍️"
    if level >= 61: return "lvl 61-70 ~ Aqua Vision Artist 🌊 🎨"
    if level >= 51: return "lvl 51-60 ~ Sky Palette Poet 🫧 🎨"
    if level >= 41: return "lvl 41-50 ~ Neon Art Sprite 💖 ⚡"
    if level >= 31: return "lvl 31-40 ~ Blossom Illustrator 🌸 🎨"
    if level >= 21: return "lvl 21-30 ~ Velvet Canvas Dreamer 🎨 ☁️"
    if level >= 16: return "lvl 16-20 ~ Passion Painter 🔥 🎨"
    if level >= 11: return "lvl 11-15 ~ Curious Line Crafter 🧐 🖋️"
    if level >= 6: return "lvl 6-10 ~ Honey Sketchling 🍯 🖋️"
    return "lvl 1-5 ~ Tiny Doodle Bean 🌸 🖋️"

@client.event
async def on_ready():
    print(f"L'ange {client.user.name} est réveillé !")

@client.event
async def on_member_join(member):
    channel = client.get_channel(1499019793318285343)
    if channel:
        msg = (f"Hello {member.mention} ! ╰ ( ≧ ⩊ ≦ ) ╯\n"
               f"Welcome to our community ☆ : . 。 o ( ≧ ▽ ≦ ) o . . : ☆\n\n"
               f"Make sure to read the rules in <#ID_DU_SALON_RULES> ! Have fun and don't forget to keep it cool ╰(°▽°)╯")
        
        # Envoi du message avec l'image jaune (nommée welcome.jpg)
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

    # Gain d'XP
    user_data[user_id]["xp"] += 10
    current_xp = user_data[user_id]["xp"]
    current_lvl = user_data[user_id]["level"]

    # Calcul du niveau (tous les 100 XP)
    new_lvl = current_xp // 100

    if new_lvl > current_lvl:
        user_data[user_id]["level"] = new_lvl
        rank_name = get_rank(new_lvl)
        
        channel = client.get_channel(1499039238015160390)
        if channel:
            # Message de level up
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
            await message.author.add_roles(role)

    await client.process_commands(message)

async def main():
    keep_alive()
    async with client:
        # Utilise os.getenv si tu as mis ton token dans les variables Render
        # Sinon remplace par "TON_TOKEN"
        token = os.getenv('TOKEN') or "TON_TOKEN_ICI"
        await client.start(token)

if __name__ == "__main__":
    asyncio.run(main())