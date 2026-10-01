import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

class MiddlemanModal(discord.ui.Modal, title="Middleman Request Form"):
    other_trader = discord.ui.TextInput(
        label="Other traders User/id",
        placeholder="e.g. @Username or User ID",
        required=True,
        style=discord.TextStyle.short
    )
    your_trade = discord.ui.TextInput(
        label="Your part of the trade",
        placeholder="Describe what you are giving...",
        required=True,
        style=discord.TextStyle.paragraph
    )
    their_trade = discord.ui.TextInput(
        label="Their part of the trade",
        placeholder="Describe what they are giving...",
        required=True,
        style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel_name = f"mm-{user.name}".lower().replace(" ", "-")
        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            overwrites=overwrites,
            reason=f"Middleman request by {user}"
        )

        ticket_embed = discord.Embed(
            title="🎮 Middleman Request Received",
            color=discord.Color.purple()
        )
        ticket_embed.add_field(name="Requestor", value=user.mention, inline=False)
        ticket_embed.add_field(name="Other Trader User/ID", value=self.other_trader.value, inline=False)
        ticket_embed.add_field(name="Your Part of Trade", value=self.your_trade.value, inline=False)
        ticket_embed.add_field(name="Their Part of Trade", value=self.their_trade.value, inline=False)

        await ticket_channel.send(
            content=f"{user.mention} Welcome! A verified Middleman will be with you shortly.",
            embed=ticket_embed
        )

        await interaction.response.send_message(
            f"✅ Ticket created successfully! Go to {ticket_channel.mention}",
            ephemeral=True
        )

class PanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Request a Middleman",
        style=discord.ButtonStyle.primary,
        emoji="💎",
        custom_id="mm_request_button"
    )
    async def request_mm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MiddlemanModal())

@bot.event
async def on_ready():
    bot.add_view(PanelView())
    print(f"Bot connected as {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def sendpanel(ctx):
    description = (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "REQUEST A MIDDLEMAN · TRADE SAFELY\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Trade with complete confidence. Our verified Middlemen ensure every deal is completed safely, fairly, and scam-free.\n\n"
        "**✦ How It Works**\n"
        "Find a trade partner and agree on terms first\n"
        "Click 💎 Request a Middleman below\n"
        "Select who you're trading with & describe the deal\n"
        "A verified MM joins and holds all assets securely\n"
        "Both sides confirm → MM releases the trade ✅\n\n"
        "**✦ Fee Structure**\n"
        "💳 In-game items — 2% of total trade value\n"
        "💵 Real money trades — 1% of total trade value\n\n"
        "**✦ What Is a Middleman?**\n"
        "A Middleman (MM) is a trusted, verified staff member who facilitates trades between two parties. They hold items, accounts, or payments and only release them once both parties confirm the trade is complete.\n\n"
        "**✦ How Does a Middleman Work?**\n"
        "1️⃣ Buyer & Seller agree to use MM\n"
        "2️⃣ Seller gives item/account to MM\n"
        "3️⃣ Buyer sends payment to MM\n"
        "4️⃣ MM verifies everything & finalises the trade\n\n"
        "**✦ Why Choose Our Service?**\n"
        "🛡️ Scam-proof — assets held until both sides confirm\n"
        "🤝 Fair & transparent — every step is documented\n"
        "⭐ Community-trusted — verified by our staff team\n"
        "⚡ Fast — experienced MMs ready to assist"
    )

    embed = discord.Embed(
        title="🎮 Verified Middleman Service",
        description=description,
        color=discord.Color.from_rgb(114, 137, 218)
    )

    await ctx.send(embed=embed, view=PanelView())

token = os.getenv(MTU0MzQ4NTg5OTU4MzUyNDkyNA.GQrouk.8hFcf6Sk0b0dNoc-vz69jobg62HUiKP_EDL0MQ)
if not token:
    raise ValueError("DISCORD_TOKEN environment variable is missing!")

bot.run(token)
      
