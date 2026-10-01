import os
import discord
from discord.ext import commands

# Enable necessary bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# In-memory storage for vouches (Resets on restart; use a database for persistence)
vouch_counts = {}

# ---------------------------------------------------------
# UI Views (Tickets & Middleman)
# ---------------------------------------------------------
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Create Ticket", style=discord.ButtonStyle.primary, custom_id="create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        # Check if ticket already exists
        channel_name = f"ticket-{user.name.lower()}"
        existing = discord.utils.get(guild.text_channels, name=channel_name)
        if existing:
            await interaction.response.send_message(f"❌ You already have an open ticket: {existing.mention}", ephemeral=True)
            return

        # Permissions: Only user and admins can see the channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
        await channel.send(f"👋 Hello {user.mention}, welcome to your support ticket! An admin will be with you shortly.")
        await interaction.response.send_message(f"✅ Ticket created: {channel.mention}", ephemeral=True)


class MiddlemanView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🤝 Request Middleman", style=discord.ButtonStyle.success, custom_id="req_mm_btn")
    async def request_mm(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(name=f"mm-{user.name.lower()}", overwrites=overwrites)
        await channel.send(f"🤝 Middleman Request by {user.mention}.\nPlease state the details of the deal (users involved, items/amount).")
        await interaction.response.send_message(f"✅ Middleman ticket opened: {channel.mention}", ephemeral=True)


# ---------------------------------------------------------
# Bot Events & Commands
# ---------------------------------------------------------
@bot.event
async def setup_hook():
    # Register persistent views for buttons so they work after bot restarts
    bot.add_view(TicketView())
    bot.add_view(MiddlemanView())


@bot.event
async def on_ready():
    print(f"✅ Logged in successfully as {bot.user} (ID: {bot.user.id})")


@bot.command(name="setup_ticket")
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    """Sends the Ticket creation panel."""
    embed = discord.Embed(
        title="🎫 Support Tickets",
        description="Click the button below to open a private ticket with staff.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=TicketView())


@bot.command(name="setup_mm")
@commands.has_permissions(administrator=True)
async def setup_mm(ctx):
    """Sends the Middleman request panel."""
    embed = discord.Embed(
        title="🤝 Middleman Services",
        description="Click below to request an official middleman for a deal.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=MiddlemanView())


@bot.command(name="vouch")
async def vouch(ctx, user: discord.Member, *, reason: str = "No reason provided"):
    """Auto-vouch system command: !vouch @user reason"""
    if user.id == ctx.author.id:
        await ctx.send("❌ You cannot vouch for yourself!")
        return

    vouch_counts[user.id] = vouch_counts.get(user.id, 0) + 1
    await ctx.send(f"✅ **+1 Vouch** added to {user.mention}! (Total Vouches: **{vouch_counts[user.id]}**)\n*Reason:* {reason}")


@bot.command(name="vouches")
async def check_vouches(ctx, user: discord.Member = None):
    """Check how many vouches a user has."""
    target = user or ctx.author
    count = vouch_counts.get(target.id, 0)
    await ctx.send(f"⭐ {target.mention} has **{count}** vouch(es).")


@bot.command(name="close")
async def close_ticket(ctx):
    """Closes and deletes a ticket or middleman channel."""
    if ctx.channel.name.startswith("ticket-") or ctx.channel.name.startswith("mm-"):
        await ctx.send("🔒 Closing this channel in 5 seconds...")
        import asyncio
        await asyncio.sleep(5)
        await ctx.channel.delete()
    else:
        await ctx.send("❌ This command can only be used inside a ticket channel.")


# ---------------------------------------------------------
# Start Bot
# ---------------------------------------------------------
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ ERROR: DISCORD_TOKEN environment variable is missing!")
        
