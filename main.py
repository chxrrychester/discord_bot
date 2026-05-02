import discord
import asyncio
import os
import random
import sys
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
ID_SERVEUR = 1499002734748111039  # ID du serveur Discord d'Angel    

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
    """Crée une jauge d'XP avec dégradé jaune vers rose"""
    # Emojis dégradé jaune -> orange -> rouge -> rose
    colors = ['🟨', '🟨', '🟧', '🟧', '🟥', '🟥', '🟪', '🟪', '🟪']
    empty = '⬜'
    
    filled = int((current_xp / xp_needed) * length)
    
    # Crée la barre avec dégradé
    bar = ''
    for i in range(filled):
        # Sélectionne la couleur selon la progression
        color_index = min(int((i / length) * len(colors)), len(colors) - 1)
        bar += colors[color_index]
    
    # Complète avec des carrés vides
    bar += empty * (length - filled)
    
    return f"{bar} {current_xp}/{xp_needed} XP"

def create_xp_progress_image(current_xp, xp_needed, username):
    """Crée une image de jauge d'XP avec dégradé rose"""
    width, height = 400, 50
    
    img = Image.new('RGB', (width, height), color=(40, 40, 40))
    draw = ImageDraw.Draw(img)
    
    bar_padding = 10
    bar_height = 30
    bar_y = (height - bar_height) // 2
    
    # Barre de fond (gris foncé)
    draw.rectangle(
        [(bar_padding, bar_y), (width - bar_padding, bar_y + bar_height)],
        fill=(60, 60, 60),
        outline=(150, 150, 150),
        width=2
    )
    
    # Calculer la progression
    progress = max(0, min(1, current_xp / xp_needed))
    bar_width = width - (2 * bar_padding) - 4
    filled_width = max(1, int(bar_width * progress))  # Au moins 1 pixel pour voir la barre
    
    print(f"DEBUG XP Bar: current_xp={current_xp}, xp_needed={xp_needed}, progress={progress}, filled_width={filled_width}", flush=True)
    
    if filled_width > 0:
        # Créer le gradient rose dégradé (jaune → rose → violet)
        for x in range(filled_width):
            ratio = x / max(filled_width, 1)
            
            # Dégradé: Jaune (255,255,0) -> Orange (255,165,0) -> Rose (255,105,180) -> Violet (200,100,180)
            if ratio < 0.5:
                # Jaune -> Rose
                t = ratio * 2
                r = int(255)
                g = int(255 - (t * 150))  # 255 -> 105
                b = int(t * 180)  # 0 -> 180
            else:
                # Rose -> Violet
                t = (ratio - 0.5) * 2
                r = int(255 - (t * 55))  # 255 -> 200
                g = int(105 - (t * 5))  # 105 -> 100
                b = int(180 + (t * 0))  # 180
            
            # Tracer une ligne verticale de cette couleur
            draw.line([(bar_padding + 2 + x, bar_y + 2), (bar_padding + 2 + x, bar_y + bar_height - 2)], 
                     fill=(r, g, b), width=1)
    
    # Sauvegarder en bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return discord.File(img_bytes, filename='xp_bar.png')

@client.event
async def on_ready():
    try:
        print(f"📡 Connexion établie avec {client.user.name}#{client.user.discriminator}", flush=True)
        print(f"🔄 Synchronisation des commandes slash...", flush=True)
        sys.stdout.flush()
        
        # Synchroniser les commandes GLOBALEMENT
        await client.tree.sync()
        print(f"✅ Synchronisation globale complétée", flush=True)
        
        # Synchroniser aussi pour le serveur spécifique
        try:
            guild = discord.Object(id=ID_SERVEUR)
            synced = await client.tree.sync(guild=guild)
            print(f"✅ Commandes synchronisées pour le serveur {ID_SERVEUR}: {len(synced)} commandes", flush=True)
            for cmd in synced:
                print(f"   - {cmd.name}: {cmd.description}", flush=True)
        except Exception as e:
            print(f"⚠️ Erreur lors de la synchronisation serveur: {e}", flush=True)
        
        print(f"✅ L'ange {client.user.name} est prêt ! Rôles configurés.", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"⚠️ Erreur lors de la synchronisation des commandes: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.stdout.flush()

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

@client.command(name="level", description="Affiche votre niveau et votre rang")
async def level_prefix_command(ctx):
    """Commande prefix !level pour afficher le niveau"""
    try:
        print(f"⚡ !level called by {ctx.author.name}", flush=True)
        sys.stdout.flush()
        
        user_id = str(ctx.author.id)
        
        if user_id not in user_data:
            user_data[user_id] = {"xp": 0, "level": 0}
        
        current_level = user_data[user_id]["level"]
        current_xp = user_data[user_id]["xp"]
        xp_needed = 100
        xp_in_level = current_xp % xp_needed
        
        print(f"DEBUG: User {ctx.author.name} - level={current_level}, xp={current_xp}, xp_in_level={xp_in_level}", flush=True)
        
        rank_name = get_rank_name(current_level)
        
        # Récupérer les rôles de l'utilisateur
        roles = [role.name for role in ctx.author.roles if role.name != "@everyone"]
        roles_str = ", ".join(roles) if roles else "Aucun rôle"
        
        xp_bar_file = create_xp_progress_image(xp_in_level, xp_needed, ctx.author.name)
        
        embed = discord.Embed(
            title=f"📊 Niveau de {ctx.author.name}",
            description=f"**Niveau :** {current_level}\n**Rang Système :** {rank_name}",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="📍 Vos rôles Discord",
            value=roles_str,
            inline=False
        )
        embed.add_field(
            name="⚡ Progression XP",
            value=f"{xp_in_level}/{xp_needed} XP",
            inline=False
        )
        embed.set_image(url="attachment://xp_bar.png")
        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        await ctx.send(embed=embed, file=xp_bar_file)
        print(f"✅ !level response sent", flush=True)
        
    except Exception as e:
        print(f"❌ ERREUR DANS !level: {e}", flush=True)
        import traceback
        traceback.print_exc()
        await ctx.send(f"❌ Erreur: {str(e)[:100]}")

@client.tree.command(name="level", description="Affiche votre niveau et votre rang")
@discord.app_commands.guilds(discord.Object(id=ID_SERVEUR))
async def level_command(interaction: discord.Interaction):
    """Commande slash /level pour afficher le niveau d'un utilisateur"""
    try:
        print(f"🔥 /level called by {interaction.user.name} in {interaction.channel.name if interaction.channel else 'DM'}", flush=True)
        sys.stdout.flush()
        
        user_id = str(interaction.user.id)
        
        if user_id not in user_data:
            user_data[user_id] = {"xp": 0, "level": 0}
        
        current_level = user_data[user_id]["level"]
        current_xp = user_data[user_id]["xp"]
        xp_needed = 100
        xp_in_level = current_xp % xp_needed
        
        print(f"DEBUG: User {interaction.user.name} - level={current_level}, xp={current_xp}, xp_in_level={xp_in_level}", flush=True)
        
        rank_name = get_rank_name(current_level)
        
        # Récupérer le vrai rôle de l'utilisateur sur le serveur
        member = interaction.user
        roles = [role.name for role in member.roles if role.name != "@everyone"]
        roles_str = ", ".join(roles) if roles else "Aucun rôle"
        
        # Créer l'image de la jauge
        xp_bar_file = create_xp_progress_image(xp_in_level, xp_needed, interaction.user.name)
        
        embed = discord.Embed(
            title=f"📊 Niveau de {interaction.user.name}",
            description=f"**Niveau :** {current_level}\n**Rang Système :** {rank_name}",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="📍 Vos rôles Discord",
            value=roles_str,
            inline=False
        )
        embed.add_field(
            name="⚡ Progression XP",
            value=f"{xp_in_level}/{xp_needed} XP",
            inline=False
        )
        embed.set_image(url="attachment://xp_bar.png")
        embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)
        
        await interaction.response.send_message(embed=embed, file=xp_bar_file)
        print(f"✅ /level response sent successfully", flush=True)
        sys.stdout.flush()
        
    except Exception as e:
        print(f"❌ ERREUR DANS /level: {type(e).__name__}: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        
        try:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur: {str(e)[:150]}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e2:
            print(f"Impossible d'envoyer le message d'erreur: {e2}", flush=True)

async def main():
    print("🤖 Initialisation du bot Discord...", flush=True)
    sys.stdout.flush()
    
    keep_alive()
    
    async with client:
        token = os.getenv('TOKEN')
        
        print(f"🔍 Vérification du TOKEN...", flush=True)
        sys.stdout.flush()
        
        if not token:
            print("❌ ERREUR: Variable d'environnement 'TOKEN' manquante!", flush=True)
            print("➡️  Ajoute ton TOKEN DISCORD dans les variables d'environnement Render", flush=True)
            sys.stdout.flush()
            return
        
        print("✅ TOKEN trouvé, démarrage du bot...", flush=True)
        sys.stdout.flush()
        
        try:
            await client.start(token)
        except Exception as e:
            print(f"❌ Erreur au démarrage du bot: {e}", flush=True)
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
            raise

if __name__ == "__main__":
    try:
        print("=" * 50, flush=True)
        print("🚀 Démarrage du bot Angel", flush=True)
        print("=" * 50, flush=True)
        sys.stdout.flush()
        
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Bot arrêté par l'utilisateur", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"❌ Erreur fatale: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.stdout.flush()