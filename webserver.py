from flask import Flask
import threading
import bot  # Import the bot module

app = Flask(__name__)

@app.route('/')
def home():
    return "Discord Bot is running."

def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # Run Flask in a separate thread
    threading.Thread(target=run_flask).start()
    # Run the Discord bot
    bot.client.run(bot.TOKEN)
