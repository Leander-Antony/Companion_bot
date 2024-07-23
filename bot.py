import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

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

# Slash command for info
@bot.tree.command(name="info", description="Displays information about the bot")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Information", description="Some useful information about the bot.", color=0x00ff00)
    embed.add_field(name="Author", value="Leander", inline=False)
    embed.add_field(name="Server count", value=f"{len(bot.guilds)}", inline=False)
    await interaction.response.send_message(embed=embed)

if __name__ == "__main__":
    import threading
    def run_bot():
        bot.run(TOKEN)

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
