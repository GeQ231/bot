import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
import os
from dotenv import load_dotenv




# Carica il token dal file .env (crea un file .env con TOKEN=TUO_TOKEN)
load_dotenv()
TOKEN = os.getenv("token")
bot.run(TOKEN)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🎵 Bot connesso come {bot.user}")

@bot.command()
async def ciao(ctx):
    await ctx.send("Yippie! Come va?")
    
def search_youtube(query):
    """Cerca un video su YouTube e restituisce il primo link disponibile."""
    ydl_opts = {
        "quiet": False,
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
    vc = await voice_channel.connect() if not ctx.voice_client else ctx.voice_client

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
        ctx.voice_client.stop()  # ⬅️ Ferma la musica ma NON disconnette il bot
        await ctx.send("⏹️ Musica fermata!")
    else:
        await ctx.send("❌ Nessuna musica in riproduzione.")

bot.run(TOKEN)