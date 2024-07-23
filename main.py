import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)

# Store links globally
notes_links = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        # Sync all commands with Discord
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Slash command for hello
@bot.tree.command(name="hello", description="Sends a hello message")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message('Hello!')

# Slash command for adding a link
@bot.tree.command(name="add_link", description="Add a link for a subject")
async def add_link(interaction: discord.Interaction, subject: str, link: str):
    if subject not in notes_links:
        notes_links[subject] = []
    notes_links[subject].append(link)
    await interaction.response.send_message(f"Link added for {subject}.")

# Slash command for getting links
@bot.tree.command(name="get_links", description="Get all links for a subject")
async def get_links(interaction: discord.Interaction, subject: str = None):
    if subject is None:
        subjects = list(notes_links.keys())
        if subjects:
            subjects_list = "\n".join(subjects)
            await interaction.response.send_message(f"Available subjects:\n{subjects_list}")
        else:
            await interaction.response.send_message("No subjects found.")
    elif subject in notes_links:
        links = "\n".join(notes_links[subject])
        await interaction.response.send_message(f"Links for {subject}:\n{links}")
    else:
        await interaction.response.send_message(f"No links found for {subject}.")


# Slash command for questin paperlink
@bot.tree.command(name="question_paper", description="provides the drive link")
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