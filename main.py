import discord
from discord.ext import commands
import yt_dlp as youtube_dl  # Replace youtube_dl with yt_dlp
from youtubesearchpython import VideosSearch
import asyncio


# Set up YouTube downloader options for yt-dlp
ytdl_options = {
    'format': 'bestaudio[ext=m4a]/bestaudio/best',  # Prioritize m4a for more stable playback
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    'extract_flat': False,
}
ytdl = youtube_dl.YoutubeDL(ytdl_options)
# Define FFmpeg options
ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

# Setup intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.queue = []
        self.autoplay = False
        print("Music cog initialized")

    async def join_voice_channel(self, ctx):
        try:
            channel = ctx.author.voice.channel
            if channel:
                print(f"Attempting to join channel: {channel.name}")
                self.voice_client = await channel.connect()
                print("Joined the voice channel")
            else:
                await ctx.send("You need to join a voice channel first!")
        except discord.errors.ClientException as e:
            print(f"ClientException error: {e}")
            await ctx.send("Bot is already in a voice channel.")
        except Exception as e:
            print(f"Unexpected error: {e}")
            await ctx.send("An unexpected error occurred while trying to join the voice channel.")

    async def leave_voice_channel(self, ctx):
        if self.voice_client and self.voice_client.is_connected():
            await self.voice_client.disconnect()
            print("Left the voice channel")

    async def play_song(self, ctx, url, retries=3):
        try:
            print("Extracting audio info...")
            info = ytdl.extract_info(url, download=False)
            url2 = info['url'] if 'url' in info else info['formats'][0]['url']
            print(f"Streaming audio from URL: {url2}")

            ffmpeg_path = r'systemPathToFFMPEG' #replace with your system path to ffmpeg.exe

            source = discord.FFmpegPCMAudio(
                url2,
                executable=ffmpeg_path,
                **ffmpeg_options
            )

            def after_playing(error):
                if error:
                    print(f"Error during playback: {error}")
                    if retries > 0:
                        print(f"Retrying... ({3 - retries + 1}/3)")
                        self.bot.loop.create_task(self.play_song(ctx, url, retries - 1))
                    else:
                        print("Failed to play after 3 attempts.")
                        self.play_next(ctx)
                else:
                    self.play_next(ctx)

            self.voice_client.play(
                source, 
                after=after_playing
            )
            print("Started playing the song.")
        except Exception as e:
            print(f"Error in play_song: {e}")
            await ctx.send("An error occurred while trying to play the audio.")

    def play_next(self, ctx):
        if self.queue and not self.voice_client.is_playing():
            next_url = self.queue.pop(0)  # Get the next song URL from the queue
            self.bot.loop.create_task(self.play_song(ctx, next_url))  # Play it
        elif self.autoplay and not self.queue:  # Check for autoplay when the queue is empty
            last_song = self.queue[-1] if self.queue else None
            if last_song:
                print("Autoplay is enabled. Attempting to find a related song.")
                related_url = self.find_related_song(last_song)
                if related_url:
                    self.queue.append(related_url)
                    print(f"Autoplay added: {related_url}")
                    self.bot.loop.create_task(self.play_song(ctx, related_url))
                else:
                    print("No related video found for autoplay.")
                    self.bot.loop.create_task(ctx.send("No related video found for autoplay."))
                    self.bot.loop.create_task(self.leave_voice_channel(ctx))  # Disconnect if nothing to play
            else:
                print("No last song found for autoplay.")
                self.bot.loop.create_task(self.leave_voice_channel(ctx))  # Disconnect if nothing to play
        else:
            print("Queue is empty. Leaving voice channel.")
            self.bot.loop.create_task(ctx.send("Queue is empty. Leaving voice channel."))
            self.bot.loop.create_task(self.leave_voice_channel(ctx))  # Disconnect if nothing to play

    def find_related_song(self, url):
        search = VideosSearch(url, limit=5)
        results = search.result()
        for result in results['result']:
            if result['link'] != url:
                return result['link']
        return None

    async def ray(self, ctx):
        self.bot.loop.create_task(ctx.send(":eggplant:"))

    async def nio(self, ctx):
        emoji = discord.utils.get(bot.emojis, name='ASS')
        self.bot.loop.create_task(ctx.send('<a:ASS:997021159478530139>'))

    @commands.command(name="autoplay")
    async def toggle_autoplay(self, ctx):
        self.autoplay = not self.autoplay
        status = "enabled" if self.autoplay else "disabled"
        await ctx.send(f"Autoplay is now {status}.")
        print(f"Autoplay is now {status}.")

    @commands.command(name="join")
    async def join(self, ctx):
        print("Received join command")
        await self.join_voice_channel(ctx)

    @commands.command(name="leave")
    async def leave(self, ctx):
        print("Received leave command")
        await self.leave_voice_channel(ctx)

    @commands.command(name="play")
    async def play(self, ctx, *, search_query):
        url = self.search_youtube(search_query)
        print(f"Received play command with query: {search_query}")
        if not self.voice_client or not self.voice_client.is_connected():
            await self.join_voice_channel(ctx)

        if self.voice_client.is_playing():
            self.queue.append(url)
            await ctx.send(f"Added to queue: {search_query}\nURL: {url}")
            print(f"Added to queue: {url}")
        else:
            await self.play_song(ctx, url)
            await ctx.send(f"Now playing: {search_query}\nURL: {url}")

    @commands.command(name="stop")
    async def stop(self, ctx):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
            await ctx.send("Playback stopped.")
            print("Playback stopped.")
        else:
            await ctx.send("No audio is currently playing.")

    @commands.command(name="queue")
    async def view_queue(self, ctx):
        if self.queue:
            queue_list = "\n".join([f"{i + 1}. {url}" for i, url in enumerate(self.queue)])
            await ctx.send(f"Current Queue:\n{queue_list}")
        else:
            await ctx.send("The queue is empty.")

    @commands.command(name="skip")
    async def skip(self, ctx):
        if self.voice_client and self.voice_client.is_playing():
            await ctx.send("Skipping current song...")
            print("Skipping current song.")
            self.voice_client.stop()
        else:
            await ctx.send("No song is currently playing to skip.")
    @commands.command(name="next")
    async def next_song(self, ctx):
        if self.voice_client and self.voice_client.is_playing():
            await ctx.send("Skipping to the next song...")
            print("Skipping current song to the next in queue.")
            self.voice_client.stop()  # This will trigger play_next to play the next song
        else:
            await ctx.send("No song is currently playing to skip.")

    def search_youtube(self, query):
        search = VideosSearch(query, limit=1)
        result = search.result()
        if result['result']:
            print(f"Found video for '{query}': {result['result'][0]['link']}")
            return result['result'][0]['link']
        else:
            print(f"No results found for '{query}'")
            return None


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

async def main():
    print("Starting bot...")
    async with bot:
        await bot.add_cog(Music(bot))
        print("Music cog added")
        await bot.start("yourBotTokenHere")  # Replace with your actual bot token
        print("Bot started")

asyncio.run(main())
