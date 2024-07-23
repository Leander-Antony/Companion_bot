import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)

# Registering application commands (slash commands)
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()  # Sync all commands with Discord
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Slash command for hello
@bot.tree.command(name="hello", description="Sends a hello message")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message('Hello!')

# Ensure directories exist
if not os.path.exists('notes'):
    os.makedirs('notes')

# Command to upload a note (file)
@bot.command()
async def upload_note(ctx, subject: str):
    if len(ctx.message.attachments) == 0:
        await ctx.send("Please attach a file.")
        return

    attachment = ctx.message.attachments[0]
    file_path = f'notes/{subject}/{attachment.filename}'
    
    if not os.path.exists(f'notes/{subject}'):
        os.makedirs(f'notes/{subject}')
    
    await attachment.save(file_path)
    await ctx.send(f"File uploaded successfully: {file_path}")

# Command to retrieve a note (link)
@bot.command()
async def get_note(ctx, subject: str, filename: str):
    file_path = f'notes/{subject}/{filename}'
    
    if os.path.exists(file_path):
        await ctx.send(f"Here is your file: {file_path}")
    else:
        await ctx.send("File not found.")

# Slash command for info
@bot.tree.command(name="info", description="Displays information about the bot")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Information", description="Some useful information about the bot.", color=0x00ff00)
    embed.add_field(name="Author", value="Leander", inline=False)
    embed.add_field(name="Server count", value=f"{len(bot.guilds)}", inline=False)
    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
