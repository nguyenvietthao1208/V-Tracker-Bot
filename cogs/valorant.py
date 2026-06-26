import discord
from discord.ext import commands
from discord import app_commands
from services.account import get_account
from services.mmr import get_mmr
import datetime
from views.profile_view import ProfileView

RANK_COLORS = {
    "Iron": 0x5B5B5B,
    "Bronze": 0x8C6239,
    "Silver": 0xC0C0C0,
    "Gold": 0xFFD700,
    "Platinum": 0x00C896,
    "Diamond": 0x6DA8FF,
    "Ascendant": 0x9B59B6,
    "Immortal": 0xE74C3C,
    "Radiant": 0xF5C542
}

class Valorant(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
    name="valorant",
    description="Kiểm tra thông tin tài khoản Valorant"
    )
    @app_commands.describe(
    riot_id="Tên Riot",
    tag="Tag Riot"
    )
    async def valorant(
        self,
        interaction: discord.Interaction,
        riot_id: str,
        tag: str
    ):

        await interaction.response.defer()

        data = await get_account(riot_id, tag)

        if data is None:
            await interaction.followup.send(
                "❌ Không tìm thấy tài khoản hoặc API lỗi."
            )
            return

        player = data["data"]

        mmr = await get_mmr(
            player["region"],
            riot_id,
            tag
        )

        import json

        print(json.dumps(mmr, indent=4, ensure_ascii=False))

        if mmr is None:
            await interaction.followup.send(
                "Không lấy được dữ liệu Rank."
            )
            return
        
        current = mmr["data"]["current"]
        peak = mmr["data"]["peak"]

        rank_name = current["tier"]["name"]

        embed_color = 0x7C3AED

        for key, color in RANK_COLORS.items():
            if key in rank_name:
                embed_color = color
                break

        embed = discord.Embed(
            title="🎮 VALORANT TRACKER",
            description=f"**{player['name']}#{player['tag']}**",
            color=embed_color
        )

        embed.add_field(
            name="👤 Riot ID",
            value=f'{player["name"]}#{player["tag"]}',
            inline=False
        )

        embed.add_field(
            name="🏆 Competitive Rank",
            value=f"**{current['tier']['name']}** • {current['rr']} RR",
            inline=False
        )

        embed.add_field(
            name="🥇 Peak Rank",
            value=peak["tier"]["name"],
            inline=True
        )

        embed.add_field(
            name="⭐ Account Level",
            value=str(player["account_level"]),
            inline=True
        )

        embed.add_field(
            name="🌍 Region",
            value=player["region"].upper(),
            inline=True
        )

        embed.set_image(
            url=player["card"]["wide"]
        )

        embed.set_footer(
            text="OWLS • Powered by HenrikDev API"
        )

        embed.timestamp = datetime.datetime.now(datetime.timezone.utc)

        await interaction.followup.send(
            embed=embed,
            view=ProfileView(
            player["region"],
            riot_id,
            tag
        )
        ) 

async def setup(bot):
    await bot.add_cog(Valorant(bot))