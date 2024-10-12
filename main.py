import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from configparser import ConfigParser
import _webServer
from cogs.PersistentButtonViews.Support_TicketSystem import SupportView
from cogs.PersistentButtonViews.Vehicle_Embed_Application import VehicleButtons

config = ConfigParser()
config.read('config.ini')
load_dotenv()

# Config.ini configurations(Change the settings)
guild_id = config['BotSettings']['Guild_Id']
event_pings = config['BotSettings']['Event_Pings']
allow_ping_role = config['BotSettings']['Allow_Ping_Role']
blacklisted_words = config['BotSettings']['BlackListedWords']
ARDatabase = config['Database']['DBName']
welcome_channel = config['BotSettings']['Welcome_Channel']
discord_hook = config['BotSettings']['DISCORD_HOOK']
# Discord Token
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']


intents = discord.Intents.all()


class Client(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            owner_id=787565560677662720,
            intents=intents,
            case_insensitive=False,
            help_command=None
        )

    async def on_ready(self):
        print(f"{self.user} Has Logged In")

        # Print the number of guilds the bot is in
        guild_count = len(self.guilds)
        print(f"Connected to {guild_count} guilds:")

        # Print information for each guild
        for guild in self.guilds:
            print(f" - {guild.name} (ID: {guild.id}) - {len(guild.members)} members")

        # Print the total number of users
        user_count = sum(len(guild.members) for guild in self.guilds)
        print(f"Total users across all guilds: {user_count}")

        await self.change_presence(
            activity=discord.Game(name="Playing World of Warcraft"),
            status=discord.Status.online

        )

        try:
            synced = await self.tree.sync(guild=discord.Object(id=guild_id))
            print(f"{len(synced)} command(s)")
        except Exception as e:
            print(e)
# this is how you create persistent interaction messages
    # that don't time out even after the bot restarts
    async def setup_hook(self):
        self.add_view(SupportView())
        self.add_view(VehicleButtons())

    async def load_cogs(self, path="cogs"):
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isdir(file_path):
                await self.load_cogs(file_path)
            elif filename.endswith(".py"):
                cog_name = file_path.replace(os.path.sep, '.')[:-3]
                await self.load_extension(cog_name)



if __name__ == "__main__":
    async def main():
        bot = Client()
        await bot.load_cogs()
        _webServer.keep_alive()
        await bot.start(DISCORD_TOKEN)


    asyncio.run(main())
