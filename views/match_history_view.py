import discord


class MatchHistoryView(discord.ui.View):

    def __init__(self, embeds):
        super().__init__(timeout=300)

        self.embeds = embeds
        self.page = 0

    async def update_message(
        self,
        interaction: discord.Interaction
    ):

        self.page_button.label = (
            f"{self.page + 1}/{len(self.embeds)}"
        )

        await interaction.response.edit_message(
            embed=self.embeds[self.page],
            view=self
        )

    @discord.ui.button(
        emoji="⬅️",
        style=discord.ButtonStyle.gray
    )
    async def previous(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if self.page > 0:
            self.page -= 1

        await self.update_message(interaction)

    @discord.ui.button(
        label="1/1",
        style=discord.ButtonStyle.blurple,
        disabled=True
    )
    async def page_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        pass

    @discord.ui.button(
        emoji="➡️",
        style=discord.ButtonStyle.gray
    )
    async def next(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if self.page < len(self.embeds) - 1:
            self.page += 1

        await self.update_message(interaction)

    async def on_timeout(self):

        for item in self.children:
            item.disabled = True