# Discord Music Bot
This is a Python-based Discord bot that provides music playback functionality for Discord servers. The bot is built using the discord.py library, along with yt_dlp and youtubesearchpython libraries for audio streaming and YouTube search.

## Features
- Play Music: Search for and play songs directly from YouTube.
- Queue Management: Add songs to a queue for continuous playback.
- Pause and Resume: Pause or resume currently playing songs.
- Skip Tracks: Skip to the next song in the queue.
- Autoplay: Automatically find and play related songs when the queue is empty.
- Custom Commands: Includes fun and utility commands like ray and nio.

## Setup
### Prerequisites
1. Install Python (3.8 or later).
2. Install FFmpeg and ensure it is added to your system's PATH.
3. Install required Python libraries:
```bash
pip install discord.py yt_dlp youtubesearchpython
```
### Configuration
1. Replace the placeholder bot token in main.py with your actual Discord bot token:
```python
await bot.start("YOUR_BOT_TOKEN")
```
2. Ensure FFmpeg is correctly installed, and update the ffmpeg_path variable in the play_song method if necessary.

## Usage
1. Run the bot:
```bash
python main.py
```
2. Invite the bot to your Discord server using your bot’s client ID.
3. Use the following commands in a server where the bot is active:
   - `!join`: Bot joins your voice channel.
   - `!play` <song name or YouTube URL>: Plays the requested song.
   - `!queue`: Displays the current song queue.
   - `!skip`: Skips the current song.
   - `!pause`: Pauses the playback.
   - `!resume`: Resumes playback.
   - `!autoplay`: Toggles autoplay mode.
  
## Libraries Used
- discord.py: For Discord API integration.
- yt_dlp: For extracting and streaming YouTube audio.
- youtubesearchpython: For efficient YouTube search functionality.

## Future Enhancements
- Add error handling for unsupported YouTube links.
- Implement volume control commands.
- Support playlists and shuffle functionality.
