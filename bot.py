import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp as youtube_dl
import imageio_ffmpeg as ffmpeg
from collections import deque
from dotenv import load_dotenv

from keep_alive import keep_alive
keep_alive()

# Define the required intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

# Initialize the bot with a command prefix and intents
bot = commands.Bot(command_prefix='/', intents=intents)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

voice_clients = {}
queues = {}  # Dictionary to manage queues for each server

yt_dl_opts = {'format': 'bestaudio/best'}
ytdl = youtube_dl.YoutubeDL(yt_dl_opts)

# Define predefined links
links = {
    "hogwarts": "https://youtu.be/slxPFAJN9UM?si=JncmPFczmexQb7tc",
    "phonk": "https://youtu.be/d9C14QqYT48?si=cWkfGHvyf4bMy3wC",
    "lofi": "https://youtu.be/CMNyHBx1gak?si=dlr-xU2w9pkiIMKx"
}

async def search_youtube(query):
    search_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'default_search': 'ytsearch',
    }
    ytdl_search = youtube_dl.YoutubeDL(search_opts)
    info = await asyncio.to_thread(lambda: ytdl_search.extract_info(query, download=False))
    if 'entries' in info:
        # Return the URL of the first result
        return info['entries'][0]['url']
    return None

async def play_next(voice_client):
    if voice_client.guild.id in queues and queues[voice_client.guild.id]:
        url = queues[voice_client.guild.id].popleft()
        data = await asyncio.to_thread(lambda: ytdl.extract_info(url, download=False))
        song = data['url']

        ffmpeg_exe = ffmpeg.get_ffmpeg_exe()
        player = discord.FFmpegOpusAudio(song, executable=ffmpeg_exe)

        # Play the next song in the queue
        voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(voice_client), bot.loop).result())
    else:
        # Wait for new songs to be added to the queue
        while not queues.get(voice_client.guild.id):
            await asyncio.sleep(5)  # Check every 5 seconds for new songs

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="type /help"))
    # Sync commands
    await bot.tree.sync()

@bot.tree.command(name='play', description='Play a song from a URL or name')
async def play(interaction: discord.Interaction, query: str):
    try:
        if interaction.user.voice is None:
            await interaction.response.send_message("You need to be in a voice channel to use this command.")
            return

        if interaction.guild.id not in voice_clients or not voice_clients[interaction.guild.id].is_connected():
            voice_client = await interaction.user.voice.channel.connect()
            voice_clients[interaction.guild.id] = voice_client

        if query in links:
            url = links[query]
        else:
            url = await search_youtube(query)
            if not url:
                await interaction.response.send_message("Could not find the song. Please check the song name or try again.")
                return

        if interaction.guild.id not in queues:
            queues[interaction.guild.id] = deque()

        queues[interaction.guild.id].append(url)

        if not voice_clients[interaction.guild.id].is_playing():
            await play_next(voice_clients[interaction.guild.id])

        await interaction.response.send_message(f"Added {query} to the queue.")
    except Exception as e:
        print(f"Error: {e}")
        await interaction.response.send_message("An error occurred while trying to play the song.")

@bot.tree.command(name='pause', description='Pause the currently playing song')
async def pause(interaction: discord.Interaction):
    try:
        if interaction.guild.id in voice_clients:
            voice_clients[interaction.guild.id].pause()
            await interaction.response.send_message("Paused the song.")
    except Exception as e:
        print(f"Error pausing song: {e}")
        await interaction.response.send_message("An error occurred while trying to pause the song.")

@bot.tree.command(name='resume', description='Resume the paused song')
async def resume(interaction: discord.Interaction):
    try:
        if interaction.guild.id in voice_clients:
            voice_clients[interaction.guild.id].resume()
            await interaction.response.send_message("Resumed the song.")
    except Exception as e:
        print(f"Error resuming song: {e}")
        await interaction.response.send_message("An error occurred while trying to resume the song.")

@bot.tree.command(name='stop', description='Stop the audio and disconnect from the voice channel')
async def stop(interaction: discord.Interaction):
    try:
        if interaction.guild.id in voice_clients:
            if voice_clients[interaction.guild.id].is_playing():
                voice_clients[interaction.guild.id].stop()
            await voice_clients[interaction.guild.id].disconnect()
            del voice_clients[interaction.guild.id]
            del queues[interaction.guild.id]
            await interaction.response.send_message("Stopped the song and disconnected.")
        else:
            await interaction.response.send_message("No audio is currently playing.")
    except Exception as e:
        print(f"Error stopping song: {e}")
        await interaction.response.send_message(f"An error occurred while trying to stop the song: {e}")

@bot.tree.command(name='skip', description='Skip the currently playing song')
async def skip(interaction: discord.Interaction):
    try:
        if interaction.guild.id in voice_clients:
            if voice_clients[interaction.guild.id].is_playing():
                voice_clients[interaction.guild.id].stop()
            if not queues.get(interaction.guild.id):
                await interaction.response.send_message("This is the last song. Add more songs to skip further.")
            else:
                await play_next(voice_clients[interaction.guild.id])
                await interaction.response.send_message("Skipped the song.")
    except Exception as e:
        print(f"Error skipping song: {e}")
        await interaction.response.send_message("An error occurred while trying to skip the song.")

@bot.tree.command(name='help', description='Display help message')
async def help_command(interaction: discord.Interaction):
    help_message = (
        "**Available Commands:**\n"
        "/play <URL or song name> - Plays the audio from the given URL or searches for the song name.\n"
        "/pause - Pauses the currently playing audio.\n"
        "/resume - Resumes the paused audio.\n"
        "/stop - Stops the audio and disconnects from the voice channel.\n"
        "/skip - Skips the currently playing song.\n"
        "Type /help to see this message."
    )
    await interaction.response.send_message(help_message)

bot.run(TOKEN)
