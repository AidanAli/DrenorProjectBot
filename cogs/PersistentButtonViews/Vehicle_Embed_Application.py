import sqlite3
import discord
from discord.ext import commands
from discord import ui
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

DatabaseFile = config['Database']['DBName']

# SQLite3 database connection
conn = sqlite3.connect(DatabaseFile)
cursor = conn.cursor()


class vehicleApplication(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Updated tables with server_name column
        cursor.execute('''CREATE TABLE IF NOT EXISTS iron_clad_users (
                            user_id INTEGER,
                            server_name TEXT,
                            PRIMARY KEY (user_id, server_name)
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS wheeled_mortar_users (
                            user_id INTEGER,
                            server_name TEXT,
                            PRIMARY KEY (user_id, server_name)
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS speedster_cars_users (
                            user_id INTEGER,
                            server_name TEXT,
                            PRIMARY KEY (user_id, server_name)
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS strada_users (
                            user_id INTEGER,
                            server_name TEXT,
                            PRIMARY KEY (user_id, server_name)
                        )''')
        conn.commit()

    @commands.command()
    @commands.has_permissions(manage_messages=True)  # Permission Settings
    async def vehicle(self, ctx):
        embed = discord.Embed(title="Vehicle Application",
                              description="East Faction Vehicle Application")
        embed.add_field(name=" (ONLY) Select Vehicles That you Own", value="**Vehicle List**\n"
                                                                           "- Iron CLad\n"
                                                                           "- Wheeled Mortar\n"
                                                                           "- Speedsters/Cars\n"
                                                                           "- Strada\n")
        embed.set_image(url="https://github.com/Moonsight91/discrap/blob/main/ArcheAge_Screenshot_2024.05.09_-_18.17"
                            ".33.02.png?raw=true")
        embed.set_thumbnail(url="https://na.archerage.to/static/images/logonew.png")

        view = VehicleButtons()
        message = await ctx.send(embed=embed, view=view)
        await ctx.message.delete()

    @vehicle.error
    async def d_error(self, ctx, error):
        await ctx.send(str(error), ephemeral=True)


class VehicleButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # Updated database check to include server name
    def check_user_in_database(self, user_id, server_name, table_name):
        cursor.execute(f"SELECT user_id FROM {table_name} WHERE user_id = ? AND server_name = ?",
                      (user_id, server_name))
        return cursor.fetchone() is not None

    # Updated button callback to include server name
    async def handle_button_click(self, interaction, button_label, table_name):
        errorIco = '<:icon_x:1238013626883899402>'
        user_id = interaction.user.id
        server_name = interaction.user.display_name

        if self.check_user_in_database(user_id, server_name, table_name):
            await interaction.response.send_message(
                f"{errorIco} You have already applied for {button_label}{server_name}.",
                ephemeral=True
            )
        else:
            cursor.execute(
                f"INSERT INTO {table_name} (user_id, server_name) VALUES (?, ?)",
                (user_id, server_name)
            )
            conn.commit()
            await interaction.response.send_message(
                f"✅You have successfully applied for {button_label} {server_name}.",
                ephemeral=True
            )

    @discord.ui.button(label="Iron Clad", custom_id="ironcladBtn", style=discord.ButtonStyle.blurple)
    async def iron_clad_btn(self, interaction, button):
        await self.handle_button_click(interaction, "IronClad", "iron_clad_users")

    @discord.ui.button(label="Wheeled Mortar", custom_id="wheeledMortarBtn", style=discord.ButtonStyle.blurple)
    async def eznan_cutter_button(self, interaction, button):
        await self.handle_button_click(interaction, "Wheeled Mortar", "wheeled_mortar_users")

    @discord.ui.button(label="Speedster(Any Car)", custom_id="speedsterBtn", style=discord.ButtonStyle.blurple)
    async def speedster_btn(self, interaction, button):
        await self.handle_button_click(interaction, "Speedster", "speedster_cars_users")

    @discord.ui.button(label="Strada", custom_id="stradaBtn", style=discord.ButtonStyle.blurple)
    async def strada_btn(self, interaction, button):
        await self.handle_button_click(interaction, "Strada", "strada_users")


async def setup(client):
    await client.add_cog(vehicleApplication(client))