import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN_STUDY')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

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

# Slash commands
@bot.tree.command(name="hello", description="Sends a hello message")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message('Hello!')

@bot.tree.command(name="add_link", description="Add a link for a subject")
async def add_link(interaction: discord.Interaction, subject_code: str, link: str):
    if subject_code not in notes_links:
        notes_links[subject_code] = []
    notes_links[subject_code].append(link)
    await interaction.response.send_message(f"Link added for {subject_code}.")

@bot.tree.command(name="get_links", description="Get all links for a subject")
async def get_links(interaction: discord.Interaction, subject_code: str):
    if subject_code in notes_links:
        links = "\n".join(notes_links[subject_code])
        await interaction.response.send_message(f"Links for {subject_code}:\n{links}")
    else:
        await interaction.response.send_message(f"No links found for {subject_code}.")

@bot.tree.command(name="question_paper", description="Provides the drive link")
async def question_paper(interaction: discord.Interaction):
    link = "https://drive.google.com/drive/folders/1jgUywox4M9qGfXDoRf-UMVrFfaKvruOm?usp=sharing"
    await interaction.response.send_message(link)

@bot.tree.command(name="info", description="Displays information about the bot")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Information", description="Some useful information about the bot.", color=0x00ff00)
    embed.add_field(name="Author", value="Leander", inline=False)
    embed.add_field(name="Server count", value=f"{len(bot.guilds)}", inline=False)
    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
