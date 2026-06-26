import discord
from services.match import get_matches
from dateutil import parser
from views.match_history_view import MatchHistoryView
from services.overview import get_overview
from services.mmr import get_mmr

class ProfileView(discord.ui.View):

    def __init__(self, region, name, tag):
        super().__init__(timeout=300)

        self.region = region
        self.name = name
        self.tag = tag

    @discord.ui.button(
        label="Overview",
        emoji="📊",
        style=discord.ButtonStyle.green
    )
    async def overview(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.defer()

        data = await get_overview(
            self.region,
            self.name,
            self.tag
        )

        mmr = await get_mmr(
            self.region,
            self.name,
            self.tag
        )

        if mmr is None:
            await interaction.followup.send(
                "Không lấy được MMR.",
                ephemeral=True
            )
            return
        
        rank = mmr["data"]["current"]["tier"]["name"]

        rr = mmr["data"]["current"]["rr"]

        peak = mmr["data"]["peak"]["tier"]["name"]

        if data is None:
            await interaction.followup.send(
                "Không lấy được dữ liệu.",
                ephemeral=True
            )
            return
        
        print("Overview matches:", len(data["data"]))
        
        kills = 0
        deaths = 0
        assists = 0

        damage = 0
        rounds = 0

        headshots = 0
        bodyshots = 0
        legshots = 0

        wins = 0
        losses = 0

        recent_form = []

        agent_count = {}

        best_match = None
        best_score = -1

        for match in data["data"]:

            player = None

            for p in match["players"]:

                if (
                    p["name"] == self.name
                    and
                    p["tag"] == self.tag
                ):
                    player = p
                    break
            
            if player is None:
                continue

            my_team = next(
                    t for t in match["teams"]
                    if t["team_id"] == player["team_id"]
                )

            kills += player["stats"]["kills"]
            deaths += player["stats"]["deaths"]
            assists += player["stats"]["assists"]

            damage += player["stats"]["damage"]["dealt"]

            rounds += (
                my_team["rounds"]["won"]
                + my_team["rounds"]["lost"]
            )

            headshots += player["stats"]["headshots"]
            bodyshots += player["stats"]["bodyshots"]
            legshots += player["stats"]["legshots"]

            if player["stats"]["score"] > best_score:

                best_score = player["stats"]["score"]

                best_match = player

                best_rounds = (
                    my_team["rounds"]["won"]
                    + my_team["rounds"]["lost"]
                )

            if my_team["won"]:
                wins += 1
            else:
                losses += 1
            
            recent_form.append(
                "🟢" if my_team["won"] else "🔴"
            )

            agent = player["agent"]["name"]

            agent_count[agent] = (
                agent_count.get(agent, 0) + 1
            )

        if best_match:

            best_adr = round(
                best_match["stats"]["damage"]["dealt"] /
                best_rounds
            )

        else:

            best_adr = 0

        favorite_agent = max(
            agent_count,
            key=agent_count.get
        )

        favorite_games = agent_count[favorite_agent]
        
        matches = wins + losses

        form = "".join(recent_form[::-1])

        if matches == 0:

            embed = discord.Embed(
                title=f"📊 {self.name}#{self.tag}",
                description="No competitive matches.",
                color=0x7C3AED
            )

            await interaction.followup.send(embed=embed)
            return

        shots = headshots + bodyshots + legshots

        hs = round(headshots / shots * 100, 1) if shots else 0

        avg_kills = round(kills / matches, 1)
        avg_deaths = round(deaths / matches, 1)
        avg_assists = round(assists / matches, 1)

        kd = round(kills / deaths, 2) if deaths else 0

        adr = round(damage / rounds, 1) if rounds else 0

        winrate = round(wins / matches * 100, 1)

        embed = discord.Embed(
            title=f"📊 {self.name}#{self.tag}",
            description=f"Last **{matches}** Competitive Matches",
            color=0x7C3AED
        )

        embed.add_field(
            name="🏅 Current Rank",
            value=(
                f"🥉 **{rank}** • **{rr} RR**\n"
                f"⭐ Peak **{peak}**"
            ),
            inline=False
        )

        embed.add_field(
            name="\u200b",
            value="────────────────────",
            inline=False
        )

        embed.add_field(
            name="📈 Recent Form",
            value=(
                f"{form}\n"
                "Oldest → Newest"
            ),
            inline=False
        )

        embed.add_field(
            name="\u200b",
            value="────────────────────",
            inline=False
        )

        embed.add_field(
            name="🏆 Record",
            value=(
                f"**Wins:** {wins}\n"
                f"**Losses:** {losses}\n"
                f"**Winrate:** {winrate}%"
            ),
            inline=True
        )

        embed.add_field(
            name="\u200b",
            value="────────────────────",
            inline=False
        )

        embed.add_field(
            name="⚔ Combat",
            value=(
                f"⚔ KDA {avg_kills}/{avg_deaths}/{avg_assists}\n"
                f"📈 K/D {kd}\n"
                f"💥 ADR {adr}\n"
                f"🎯 HS {hs}%"
            ),
            inline=True
        )

        embed.add_field(
            name="\u200b",
            value="────────────────────",
            inline=False
        )

        embed.add_field(
            name="🎯 Favorite Agent",
            value=(
                f"{favorite_agent}\n"
                f"{favorite_games} Games"
            ),
            inline=True
        )

        embed.add_field(
            name="\u200b",
            value="────────────────────",
            inline=False
        )

        best_kda = (
            f"{best_match['stats']['kills']}/"
            f"{best_match['stats']['deaths']}/"
            f"{best_match['stats']['assists']}"
        )

        embed.add_field(
            name="🔥 Best Match",
            value=(
                f"{best_kda}\n"
                f"{best_adr} ADR"
            ),
            inline=False
        )

        await interaction.followup.send(embed=embed)

    @discord.ui.button(
        label="Matches",
        emoji="📜",
        style=discord.ButtonStyle.blurple
    )
    async def matches(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.defer()

        print("\n========== MATCHES ==========")
        print("Searching:", repr(self.name), repr(self.tag))

        data = await get_matches(
            self.region,
            self.name,
            self.tag,
            size=10
        )

        if data is None:
            await interaction.followup.send(
                "❌ Không lấy được Match History.",
                ephemeral=True
            )
            return

        print("Data keys:", data.keys())
        print("Matches:", len(data["data"]))

        embeds = []

        for index, match in enumerate(data["data"], start=1):

            try:

                print(f"\n------ MATCH {index} ------")

                metadata = match["metadata"]

                print(metadata)

                print("\nPlayers:")

                player = None

                for p in match["players"]:

                    print(
                        repr(p["name"]),
                        repr(p["tag"])
                    )

                    if (
                        p["name"] == self.name
                        and
                        p["tag"] == self.tag
                    ):
                        player = p

                        highest_score = max(
                            p["stats"]["score"]
                            for p in match["players"]
                        )

                        is_mvp = (
                            player["stats"]["score"] == highest_score
                        )

                        break

                if player is None:
                    print(">>> PLAYER NOT FOUND <<<")
                    continue

                print("FOUND PLAYER!")

                my_team = next(
                    t
                    for t in match["teams"]
                    if t["team_id"] == player["team_id"]
                )

                

                if my_team["won"]:
                    if my_team["rounds"]["won"] < my_team["rounds"]["lost"]:
                        result = "🟢 Victory (Enemy FF)"
                    else:
                        result = "🟢 Victory"
                else:
                    result = "🔴 Defeat"

                score = (
                    f'{my_team["rounds"]["won"]}-'
                    f'{my_team["rounds"]["lost"]}'
                )

                rounds = (
                    my_team["rounds"]["won"]
                    + my_team["rounds"]["lost"]
                )

                acs = round(
                    player["stats"]["score"] / rounds
                )

                headshots = player["stats"]["headshots"]
                bodyshots = player["stats"]["bodyshots"]
                legshots = player["stats"]["legshots"]

                total_hits = headshots + bodyshots + legshots

                if total_hits > 0:
                    hs = round(headshots / total_hits * 100, 1)
                else:
                    hs = 0

                minutes = metadata["game_length_in_ms"] // 60000

                started = parser.isoparse(metadata["started_at"])

                timestamp = int(started.timestamp())

                value = (
                    f"🏅 Rank: {player['tier']['name']}\n"
                    f"🎯 Agent: {player['agent']['name']}\n"
                    f"⚔️ KDA: {player['stats']['kills']}/"
                    f"{player['stats']['deaths']}/"
                    f"{player['stats']['assists']}\n"
                    f"⭐ ACS: {acs}\n"
                    f"🎯 HS: {hs}%\n"
                    f"⏱️ {minutes} min\n"
                    f"📅 <t:{timestamp}:R>\n"
                    f"🔵 Score: {score}"
                )

                if is_mvp:
                    value += "\n👑 Match MVP"

                embed = discord.Embed(
                    title="📜 Match History",
                    color=0x7C3AED
                )

                embed.add_field(
                    name=f"{result} • {metadata['map']['name']}",
                    value=value,
                    inline=False
                )

                embeds.append(embed)

            except Exception as e:
                print(f"\n❌ ERROR MATCH {index}")
                print(type(e))
                print(e)

        print("\nFIELDS:", len(embed.fields))

        if len(embed.fields) == 0:

            embed.description = (
                "⚠️ Không tìm thấy dữ liệu của người chơi trong các trận đấu."
            )

        view = MatchHistoryView(embeds)

        view.page_button.label = f"1/{len(embeds)}"

        await interaction.followup.send(
            embed=embeds[0],
            view=view
        )

    @discord.ui.button(
        label="Agents",
        emoji="🎯",
        style=discord.ButtonStyle.gray
    )
    async def agents(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.defer()

        data = await get_matches(
            self.region,
            self.name,
            self.tag,
            size=10
        )

        if data is None:
            await interaction.followup.send(
                "Không lấy được dữ liệu."
            )
            return
        
        agent_stats = {}

        for match in data["data"]:

            player = None

            for p in match["players"]:

                if (
                    p["name"] == self.name
                    and
                    p["tag"] == self.tag
                ):
                    player = p
                    break

            if player is None:
                continue

            my_team = next(
                t
                for t in match["teams"]
                if t["team_id"] == player["team_id"]
            )

            agent = player["agent"]["name"]

            if agent not in agent_stats:

                agent_stats[agent] = {

                    "games": 0,

                    "wins": 0,

                    "kills": 0,

                    "deaths": 0,

                    "assists": 0,

                    "damage": 0,

                    "rounds": 0,

                    "headshots": 0,

                    "bodyshots": 0,

                    "legshots": 0

                }

            stats = agent_stats[agent]

            stats["games"] += 1

            stats["kills"] += player["stats"]["kills"]

            stats["deaths"] += player["stats"]["deaths"]

            stats["assists"] += player["stats"]["assists"]

            stats["damage"] += player["stats"]["damage"]["dealt"]

            stats["headshots"] += player["stats"]["headshots"]

            stats["bodyshots"] += player["stats"]["bodyshots"]

            stats["legshots"] += player["stats"]["legshots"]

            stats["rounds"] += (
                my_team["rounds"]["won"]
                +
                my_team["rounds"]["lost"]
            )

            if my_team["won"]:
                stats["wins"] += 1
        
        embed = discord.Embed(
            title="🎯 Agent Statistics",
            color=0x7C3AED
        )
        embed.description = "Last **10** Competitive Matches"

        if not agent_stats:

            await interaction.followup.send(
                "Không có dữ liệu Agent."
            )
            return

        sorted_agents = sorted(

            agent_stats.items(),

            key=lambda x: x[1]["games"],

            reverse=True

        )

        medals = ["🥇", "🥈", "🥉"]

        for i, (agent, stats) in enumerate(sorted_agents):

            if i < 3:
                name = f"{medals[i]} {agent}"
            else:
                name = f"🎯 {agent}"

            kd = round(
                stats["kills"] /
                stats["deaths"],
                2
            ) if stats["deaths"] else 0

            adr = round(
                stats["damage"] /
                stats["rounds"],
                1
            ) if stats["rounds"] else 0

            shots = (
                stats["headshots"]
                +
                stats["bodyshots"]
                +
                stats["legshots"]
            )

            hs = round(
                stats["headshots"] /
                shots *
                100,
                1
            ) if shots else 0

            winrate = round(
                stats["wins"] /
                stats["games"] *
                100,
                1
            )

            avg_kills = round(
                stats["kills"] /
                stats["games"],
                1
            )

            avg_deaths = round(
                stats["deaths"] /
                stats["games"],
                1
            )

            avg_assists = round(
                stats["assists"] /
                stats["games"],
                1
            )

            embed.add_field(

                name=name,

                value=(

                    f"🎮 Games: **{stats['games']}**\n"

                    f"🏆 Winrate: **{winrate}%**\n"

                    f"⚔️ KDA: **{avg_kills}/{avg_deaths}/{avg_assists}**\n"

                    f"💥 ADR: **{adr}**\n"

                    f"🎯 HS: **{hs}%**"

                ),

                inline=False
            )

            if i != len(sorted_agents) - 1:
                embed.add_field(
                    name="\u200b",
                    value="────────────────────",
                    inline=False
                )

        embed.set_footer(
            text=f"{len(sorted_agents)} Agents Played"
        )

        await interaction.followup.send(embed=embed)

    @discord.ui.button(
        label="Refresh",
        emoji="🔄",
        style=discord.ButtonStyle.red
    )
    async def refresh(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "Đang làm mới dữ liệu...",
            ephemeral=True
        )