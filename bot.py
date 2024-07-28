import os
import discord
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

# Discord bot Initialization with intents
client = discord.Client(intents=intents)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

voice_clients = {}
queues = {}  # Dictionary to manage queues for each server

yt_dl_opts = {'format': 'bestaudio/best'}
ytdl = youtube_dl.YoutubeDL(yt_dl_opts)

# Define predefined links
links = {
    "?play_hogwarts": "https://youtu.be/slxPFAJN9UM?si=JncmPFczmexQb7tc",
    "?play_phonk": "https://youtu.be/d9C14QqYT48?si=cWkfGHvyf4bMy3wC",
    "?play_lofi": "https://youtu.be/CMNyHBx1gak?si=dlr-xU2w9pkiIMKx"
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
        voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(voice_client), client.loop).result())
    else:
        # Disconnect if there are no more songs in the queue
        await voice_client.disconnect()
        del voice_clients[voice_client.guild.id]
        del queues[voice_client.guild.id]

@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")
    await client.change_presence(activity=discord.Game(name="type ?help"))

@client.event
async def on_message(msg):
    if msg.content.startswith("?play"):
        try:
            # Check if the user is in a voice channel
            if msg.author.voice is None:
                await msg.channel.send("You need to be in a voice channel to use this command.")
                return

            if msg.guild.id not in voice_clients or not voice_clients[msg.guild.id].is_connected():
                voice_client = await msg.author.voice.channel.connect()
                voice_clients[msg.guild.id] = voice_client

            # Extract the URL or song name from the message
            args = msg.content.split(maxsplit=1)
            if len(args) > 1:
                query = args[1]
            else:
                query = None

            if query is None:
                # If no URL or song name is provided, use predefined commands
                url = links.get(msg.content, None)
                if not url:
                    await msg.channel.send("Please provide a URL or use a predefined command to play a song.")
                    return
            else:
                # Search YouTube for the song name
                url = await search_youtube(query)
                if not url:
                    await msg.channel.send("Could not find the song. Please check the song name or try again.")
                    return

            if msg.guild.id not in queues:
                queues[msg.guild.id] = deque()

            # Add the URL to the queue
            queues[msg.guild.id].append(url)

            if not voice_clients[msg.guild.id].is_playing():
                # Pass the voice client to play_next
                await play_next(voice_clients[msg.guild.id])
        except Exception as e:
            print(f"Error: {e}")
            await msg.channel.send("An error occurred while trying to play the song.")

    if msg.content.startswith("?pause"):
        try:
            if msg.guild.id in voice_clients:
                voice_clients[msg.guild.id].pause()
        except Exception as e:
            print(f"Error pausing song: {e}")

    if msg.content.startswith("?resume"):
        try:
            if msg.guild.id in voice_clients:
                voice_clients[msg.guild.id].resume()
        except Exception as e:
            print(f"Error resuming song: {e}")

    if msg.content.startswith("?stop"):
        try:
            if msg.guild.id in voice_clients:
                # Stop the currently playing audio and disconnect from the voice channel
                if voice_clients[msg.guild.id].is_playing():
                    voice_clients[msg.guild.id].stop()
                await voice_clients[msg.guild.id].disconnect()
                del voice_clients[msg.guild.id]
                del queues[msg.guild.id]
            else:
                await msg.channel.send("No audio is currently playing.")
        except Exception as e:
            print(f"Error stopping song: {e}")
            await msg.channel.send(f"An error occurred while trying to stop the song: {e}")

    if msg.content.startswith("?skip"):
        try:
            if msg.guild.id in voice_clients:
                if voice_clients[msg.guild.id].is_playing():
                    voice_clients[msg.guild.id].stop()
                if not queues.get(msg.guild.id):
                    await msg.channel.send("This is the last song. Add more songs to skip further.")
                else:
                    await play_next(voice_clients[msg.guild.id])
        except Exception as e:
            print(f"Error skipping song: {e}")

    if msg.content.startswith("?help"):
        help_message = (
            "**Available Commands:**\n"
            "`?play <URL>` - Plays the audio from the given URL.\n"
            "`?play_hogwarts` - Plays the Hogwarts theme.\n"
            "`?play_phonk` - Plays Chill Phonk music.\n"
            "`?play_lofi` - Plays Lofi music.\n"
            "`?pause` - Pauses the currently playing audio.\n"
            "`?resume` - Resumes the paused audio.\n"
            "`?stop` - Stops the audio and disconnects from the voice channel.\n"
            "`?skip` - Skips the currently playing song.\n"
            "Type `?help` to see this message."
        )
        await msg.channel.send(help_message)

client.run(TOKEN)
