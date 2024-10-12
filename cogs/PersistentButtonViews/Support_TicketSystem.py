import discord
from discord.ext import commands
from discord import ui

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tickets = {}  # Dictionary to keep track of channels for tickets
        self.user_ticket_count = {}  # Dictionary to keep track of the number of tickets per user

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} has connected to Discord!")

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if isinstance(interaction, discord.Interaction) and interaction.type == discord.InteractionType.component:
            if interaction.data["custom_id"] == "createticket":
                await self.create_ticket(interaction)

    async def create_ticket(self, interaction):
        user_id = interaction.user.id

        # Get the number of existing tickets for this user
        user_ticket_count = self.user_ticket_count.get(user_id, 0)
        print(f"User {user_id} currently has {user_ticket_count} tickets.")
        if user_ticket_count >= 1:
            await interaction.response.send_message("(1) Ticket Per Member.", ephemeral=True)
            return

        guild = self.bot.get_guild(interaction.guild_id)
        if guild is None:
            await interaction.response.send_message("Guild not found.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel_name = f"ticket-{interaction.user.name}"
        channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

        # Track the created ticket channel
        self.tickets[channel.id] = user_id
        # Update the user's ticket count
        self.user_ticket_count[user_id] = user_ticket_count + 1
        print(f"Ticket created for user {user_id}, channel ID: {channel.id}. Total tickets: {self.user_ticket_count[user_id]}")

        # Send a message to the user with an invite to the new channel
        embed_user = discord.Embed(
            title="Ticket Created",
            description=f"Your ticket has been created in {channel.mention}. Support will be with you shortly.",
            color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed_user, ephemeral=True)

        # Send an embed message to the ticket channel
        embed_channel = discord.Embed(
            title="New Ticket",
            description=f"Welcome to your support ticket channel, {interaction.user.mention}. Support will be with you shortly.",
            color=discord.Color.blurple())
        await channel.send(embed=embed_channel)

    @commands.Cog.listener()
    async def on_channel_delete(self, channel):
        """Removes the ticket record when a channel is deleted."""
        if channel.type == discord.ChannelType.text and channel.id in self.tickets:
            user_id = self.tickets.pop(channel.id)
            # Decrease the ticket count for the user
            if user_id in self.user_ticket_count:
                self.user_ticket_count[user_id] -= 1
                if self.user_ticket_count[user_id] <= 0:
                    del self.user_ticket_count[user_id]
            print(f"Removed ticket for user {user_id}, channel ID: {channel.id}. Remaining tickets: {self.user_ticket_count.get(user_id, 0)}")

    @commands.command()
    @commands.has_any_role("Admin,Discord Helper")  # Restrict to users with the "popcorn" role
    async def close_ticket(self, ctx, channel: discord.TextChannel):
        if channel.id in self.tickets:
            user_id = self.tickets.pop(channel.id)
            # Decrease the ticket count for the user
            if user_id in self.user_ticket_count:
                self.user_ticket_count[user_id] -= 1
                if self.user_ticket_count[user_id] <= 0:
                    del self.user_ticket_count[user_id]
            await channel.delete()
            await ctx.send(f"Ticket channel {channel.mention} has been closed.")
        else:
            await ctx.send("This channel is not a valid ticket channel.")

    @close_ticket.error
    async def dm_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="Permissions Error",
                description="You Don't Have Permissions to Use That Command",
                colour=discord.Colour.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
    @commands.command()
    async def support(self, ctx):
        embed = discord.Embed(
            title="Contact Support",
            description="Click the button below to create a support ticket.",
            color=discord.Color.blurple())
        embed.set_image(url="https://www.stylevore.com/wp-content/uploads/2020/01/cfab1e91af14fbd7c172fd0e9ed660e8.png")
        view = SupportView()
        await ctx.send(embed=embed, view=view)


class SupportView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Set timeout to None to make the view persistent

    @ui.button(label="Create Ticket", style=discord.ButtonStyle.blurple, custom_id="createticket")
    async def create_ticket_button(self, button: ui.Button, interaction: discord.Interaction):
        pass


async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
