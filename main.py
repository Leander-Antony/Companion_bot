import os
import discord
from discord.ext import commands
import youtube_dl
from dotenv import load_dotenv
from discord import app_commands

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

ytdl_options = {
    'format': 'bestaudio/best',
    'noplaylist': True
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

# Global notes_links variable
notes_links = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        # Sync all commands with Discord
        await bot.tree.sync()
        print("Commands synced.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="join", description="Join the voice channel")
async def join(interaction: discord.Interaction):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message("Joined the voice channel!")
    else:
        await interaction.response.send_message("You need to be in a voice channel to use this command.")

@bot.tree.command(name="leave", description="Leave the voice channel")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Left the voice channel!")
    else:
        await interaction.response.send_message("I'm not connected to any voice channel.")

@bot.tree.command(name="play", description="Play a song from a YouTube URL")
async def play(interaction: discord.Interaction, url: str):
    if not interaction.guild.voice_client:
        await interaction.response.send_message("I'm not connected to a voice channel. Use /join to connect.")
        return

    ydl = youtube_dl.YoutubeDL(ytdl_options)
    info = ydl.extract_info(url, download=False)
    url2 = info['formats'][0]['url']

    if interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()

    current_song = discord.FFmpegPCMAudio(url2, **ffmpeg_options)
    interaction.guild.voice_client.play(current_song)
    await interaction.response.send_message(f'Now playing: {info["title"]}')

@bot.tree.command(name="pause", description="Pause the current song")
async def pause(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.pause()
        await interaction.response.send_message("Playback paused.")
    else:
        await interaction.response.send_message("No audio is playing.")

@bot.tree.command(name="resume", description="Resume the paused song")
async def resume(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
        interaction.guild.voice_client.resume()
        await interaction.response.send_message("Playback resumed.")
    else:
        await interaction.response.send_message("Playback is not paused.")

@bot.tree.command(name="skip", description="Skip the current song")
async def skip(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("Skipped the current song.")
    else:
        await interaction.response.send_message("No audio is playing.")

@bot.tree.command(name="stop", description="Stop the current song")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("Playback stopped.")
    else:
        await interaction.response.send_message("No audio is playing.")

# Slash command for hello
@bot.tree.command(name="hello", description="Sends a hello message")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message('Hello!')

# Slash command for adding a link
@bot.tree.command(name="add_link", description="Add a link for a subject")
async def add_link(interaction: discord.Interaction, subject_code: str, link: str):
    if subject_code not in notes_links:
        notes_links[subject_code] = []
    notes_links[subject_code].append(link)
    await interaction.response.send_message(f"Link added for {subject_code}.")

# Slash command for getting links
@bot.tree.command(name="get_links", description="Get all links for a subject")
async def get_links(interaction: discord.Interaction, subject_code: str):
    if subject_code in notes_links:
        links = "\n".join(notes_links[subject_code])
        await interaction.response.send_message(f"Links for {subject_code}:\n{links}")
    else:
        await interaction.response.send_message(f"No links found for {subject_code}.")

# Slash command for question paper link
@bot.tree.command(name="question_paper", description="Provides the drive link")
async def question_paper(interaction: discord.Interaction):
    link = "https://drive.google.com/drive/folders/1jgUywox4M9qGfXDoRf-UMVrFfaKvruOm?usp=sharing"
    await interaction.response.send_message(link)

# Slash command for displaying bot information
@bot.tree.command(name="info", description="Displays information about the bot")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Information", description="Some useful information about the bot.", color=0x00ff00)
    embed.add_field(name="Author", value="Leander", inline=False)
    embed.add_field(name="Server count", value=f"{len(bot.guilds)}", inline=False)
    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
