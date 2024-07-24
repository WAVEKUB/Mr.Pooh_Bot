import discord
import os
from discord.ext import commands
import yt_dlp
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

queues = {}
voice_clients = {}
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

@client.event
async def on_ready():
    print(f'{client.user} is now jamming')

async def next(ctx):
    if queues[ctx.guild.id] != []:
        link = queues[ctx.guild.id].pop(0)
    await play(ctx, link)
        
@client.command(name="play")
async def play(ctx, link):

    try:
        voice_client = await ctx.author.voice.channel.connect()
        voice_clients[voice_client.guild.id] = voice_client
    except Exception as e:
        print(e)

    try:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(link, download=False))

        song = data['url']
        player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

        voice_clients[ctx.guild.id].play(player, after=lambda e:asyncio.run_coroutine_threadsafe(next(ctx), client.loop))
    except Exception as e:
        print(e)

@client.command(name="pause")
async def pause(ctx):
    try:
        voice_clients[ctx.guild.id].pause()
    except Exception as e:
        print(e)

@client.command(name="resume")
async def resume(ctx):
    try:
        voice_clients[ctx.guild.id].resume()
    except Exception as e:
        print(e)

@client.command(name="stop")
async def stop(ctx):
    try:
        voice_clients[ctx.guild.id].stop()
        await voice_clients[ctx.guild.id].disconnect()
    except Exception as e:
        print(e)

@client.command(name="queue")
async def queue(ctx, link):
    if ctx.guild.id not in queues:
        queues[ctx.guild.id]=[]
    queues[ctx.guild.id].append(link)
    await ctx.send("Added to queue!")


client.run(TOKEN)
