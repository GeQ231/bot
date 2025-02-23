import os
import time
import discord
from discord.ext import commands, tasks
import yt_dlp
from dotenv import load_dotenv

# Carica il token dal file .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True
intents.voice_states = True  # Aggiunto per controllare chi è nei canali vocali

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🎵 Bot connesso come {bot.user}")
    check_users_online.start()

@tasks.loop(minutes=5)  # Controlla ogni 5 minuti
async def check_users_online():
    for guild in bot.guilds:
        active_members = [
            m for m in guild.members if not m.bot and m.status != discord.Status.offline
        ]
        active_voice_users = [
            m for vc in guild.voice_channels for m in vc.members if not m.bot
        ]

        if not active_members and not active_voice_users:  # Nessuno online o in vocale
            print("Nessun utente attivo nel server. Spegnimento...")
            await bot.close()
            break

@bot.command()
async def ciao(ctx):
    await ctx.send("Yippie! Come va?")

def search_youtube(query):
    """Cerca un video su YouTube e restituisce il primo link disponibile."""
    ydl_opts = {
        "quiet": True,
        "default_search": "ytsearch",
        "noplaylist": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if not info or "entries" not in info or not info["entries"]:
                return None
            return info["entries"][0].get("url") or info["entries"][0].get("webpage_url")
    except Exception as e:
        print(f"❌ ERRORE yt_dlp: {e}")
        return None

@bot.command()
async def join(ctx):
    """Fa entrare il bot nel canale vocale dell'utente."""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(f"🔊 Sono entrato in {channel.name}")
    else:
        await ctx.send("❌ Devi essere in un canale vocale per usare questo comando!")

@bot.command()
async def leave(ctx):
    """Fa uscire il bot dal canale vocale."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Uscito dal canale vocale!")
    else:
        await ctx.send("❌ Non sono in nessun canale vocale!")

@bot.command()
async def play(ctx, *, query):
    """Riproduce una canzone cercandola su YouTube senza uscire dal canale dopo."""
    
    if not ctx.author.voice:
        await ctx.send("❌ Devi essere in un canale vocale per usare questo comando!")
        return
    
    voice_channel = ctx.author.voice.channel
    vc = ctx.voice_client if ctx.voice_client else await voice_channel.connect()

    url = search_youtube(query)
    
    if not url:
        await ctx.send("❌ Nessun risultato trovato per la ricerca.")
        return

    await ctx.send(f"🎵 **Riproducendo:** {url}")

    ffmpeg_options = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn"
    }

    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info["url"]

    vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_options))

@bot.command()
async def stop(ctx):
    """Ferma la musica senza far uscire il bot dal canale."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏹️ Musica fermata!")
    else:
        await ctx.send("❌ Nessuna musica in riproduzione.")

# Loop di Keep-Alive per il riavvio automatico
while True:
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Errore: {e}. Riavvio in 10 secondi...")
        time.sleep(10)
