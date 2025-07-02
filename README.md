
# Music Bot

A music bot that plays audio from URLs or searches for songs by name. It also supports predefined links to lofi, Hogwarts, and phonk music.

**Getting Started**

1. Clone this repository: `git clone https://github.com/your-username/music-bot.git`
2. Create a new file named `.env` in the root directory of your project.
3. Add your Discord token to the `.env` file: `DISCORD_TOKEN=YOUR_TOKEN_HERE`
4. Install the dependencies by running: `pip install -r requirements.txt`
5. Run the bot using: `python bot.py`

**Commands**

The music bot supports the following commands:

* `/play <URL or song name>`: Plays audio from the given URL or searches for the song name.
* `/pause`: Pauses the currently playing audio.
* `/resume`: Resumes the paused audio.
* `/stop`: Stops the audio and disconnects from the voice channel.
* `/skip`: Skips the currently playing song.
* `/help`: Displays this help message.
* `/lofi`, `/hogwarts`, `/phonk`: Plays predefined links to lofi, Hogwarts, and phonk music.

**Predefined Links**

The bot supports predefined links to lofi, Hogwarts, and phonk music. You can use the following commands to play these songs:

* `/lofi`
* `/hogwarts`
* `/phonk`

**Keep Alive**

This project uses a keep alive script to keep the server running indefinitely. The script is located in `keep_alive.py` and can be run using: `python keep_alive.py`.

**Acknowledgments**

The music bot uses several libraries, including Discord.py, youtube-dl, and ffmpeg.

