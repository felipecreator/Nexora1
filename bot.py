import discord
from discord.ext import commands
from discord.ui import Select, View, Button
import asyncio
from datetime import datetime

# ==================== CONFIGURAÇÕES ====================
TOKEN = "MTUzMzk5MzM2OTQzNTUwODg1Ng.GkWoou.Z12oJ7duO2pvlrCbwr_k-se8s5kO-ewWGdBQRs"
CATEGORY_TICKETS = 1533999834003144846   # ID da categoria de tickets
STAFF_ROLE_ID = 1530307314530390060

COR_NEXORA = 0x5865F2

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== VIEW DOS BOTÕES DENTRO DO TICKET ====================
class TicketView(View):
    def __init__(self, ticket_owner):
        super().__init__(timeout=None)
        self.ticket_owner = ticket_owner

    @discord.ui.button(label="Sair do ticket", style=discord.ButtonStyle.secondary, emoji="↪️")
    async def sair(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.ticket_owner.id and STAFF_ROLE_ID not in [r.id for r in interaction.user.roles]:
            return await interaction.response.send_message("❌ Só o dono do ticket ou staff pode sair.", ephemeral=True)
        
        await interaction.channel.set_permissions(self.ticket_owner, view_channel=False)
        await interaction.response.send_message(f"✅ {interaction.user.mention} saiu do ticket.")

    @discord.ui.button(label="Deletar", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def deletar(self, interaction: discord.Interaction, button: Button):
        if STAFF_ROLE_ID not in [r.id for r in interaction.user.roles]:
            return await interaction.response.send_message("❌ Só staff pode deletar.", ephemeral=True)
        
        await interaction.response.send_message("🗑️ Deletando ticket em 5 segundos...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

# ==================== MENU DE SELEÇÃO (PAINEL) ====================
class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Suporte",
                description="Assuntos relacionados ao suporte",
                emoji="🛠️",
                value="suporte"
            ),
            discord.SelectOption(
                label="Compras",
                description="Assuntos relacionados a compras",
                emoji="🛒",
                value="compras"
            )
        ]
        super().__init__(placeholder="Clique aqui para selecionar...", options=options, custom_id="ticket_select")

    async def callback(self, interaction: discord.Interaction):
        categoria = self.values[0]

        # Verifica se a pessoa já tem um ticket aberto
        for channel in interaction.guild.channels:
            if channel.name == f"ticket-{interaction.user.name.lower()}" or channel.name == f"{categoria}-{interaction.user.name.lower()}":
                return await interaction.response.send_message("❌ Você já possui um ticket aberto!", ephemeral=True)

        category = bot.get_channel(CATEGORY_TICKETS)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True, manage_channels=True),
            interaction.guild.get_role(STAFF_ROLE_ID): discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)
        }

        channel = await interaction.guild.create_text_channel(
            name=f"{categoria}-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(color=COR_NEXORA)
        embed.title = f"{interaction.user.name} — Atendimento ao Cliente"
        embed.description = f"**Atendimento — {categoria.title()}**\n\n👋 Olá {interaction.user.mention}, a equipe da **Nexora** já está ciente da abertura do seu ticket.\nEnquanto aguarda um staff, sinta-se à vontade para informar seu problema."

        embed.add_field(name="📁 Atendimento:", value=f"`{categoria.title()}`", inline=True)
        embed.add_field(name="👤 Cliente:", value=f"`{interaction.user.name}`", inline=True)
        embed.add_field(name="👮 Staff Comandante:", value="`Aguardando...`", inline=True)
        embed.set_footer(text=f"Nexora • {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        view = TicketView(interaction.user)
        await channel.send(content=interaction.user.mention, embed=embed, view=view)

        await interaction.response.send_message(f"✅ Seu ticket foi criado: {channel.mention}", ephemeral=True)

class TicketPanel(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# ==================== COMANDO PARA ENVIAR O PAINEL ====================
@bot.command()
@commands.has_permissions(administrator=True)
async def painel(ctx):
    embed = discord.Embed(
        title="🎫 Sistema Automático de Tickets",
        description="Para receber **SUPORTE** ou falar sobre **COMPRAS**, abra um ticket selecionando uma opção no menu abaixo.\n\n❗ Abra tickets apenas quando necessário.",
        color=COR_NEXORA
    )
    embed.set_footer(text="Nexora • Atendimento")

    await ctx.send(embed=embed, view=TicketPanel())
    await ctx.message.delete()

@bot.event
async def on_ready():
    print(f"✅ Bot Nexora online como {bot.user}")
    bot.add_view(TicketPanel())  # Mantém o menu funcionando mesmo após reiniciar

bot.run(TOKEN)