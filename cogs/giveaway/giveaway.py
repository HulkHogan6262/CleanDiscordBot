import datetime
import random
import asyncio
import disnake
from disnake.ext import commands, tasks
from datetime import datetime

from data.var import timeUnits, dataFilePath
from utils.load_lang import giveaway_lang as langText
from utils import error
from utils import giveaway as gw_utils


class GiveawayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giveaways: list[gw_utils.Giveaway] = []

    @tasks.loop(seconds=1)
    async def check_giveaways(self):
        for giveaway_ in self.giveaways:
            if not giveaway_.finished:
                giveaway_.update()

    @commands.Cog.listener()
    async def on_ready(self):
        print('⚠️ 🔩 /giveaway has been loaded')
        await self.check_giveaways.start()

    @commands.slash_command(name='giveaway', description=langText["GIVEAWAY_DESCRIPTION"])
    async def giveaway(self, interaction: disnake.ApplicationCommandInteraction):
        pass

    @giveaway.sub_command(name="start", description=langText["COMMAND_DESCRIPTION"]["COMMAND_START"])
    async def start(self, interaction: disnake.ApplicationCommandInteraction, prize: str, winners: int, duration: int):
        await interaction.response.defer(ephemeral=True)
        if duration <= 0:
            embed = disnake.Embed(title=langText["ERROR"]["TITLE"],
                                  description=langText["ERROR"]["DURATION_LESS_THAN_0"],
                                  color=disnake.Color.red())
            await interaction.followup.send(embed=embed)
            return
        if winners <= 0:
            embed = disnake.Embed(title=langText["ERROR"]["TITLE"],
                                  description=langText["ERROR"]["WINNERS_LESS_THAN_0"],
                                  color=disnake.Color.red())
            await interaction.followup.send(embed=embed)
            return
        message = await interaction.channel.send("Préparation du giveaway...")
        gw = gw_utils.Giveaway(self.bot, interaction.guild, duration, winners, message=message, prize=prize)
        self.giveaways.append(gw)
        gw.update_message()
        embed = disnake.Embed(title=langText["EMBED"]["START_TITLE"],
                              description=langText["EMBED"]["START_DESCRIPTION"],
                              color=disnake.Color.green())
        await interaction.followup.send(embed=embed)

    @giveaway.sub_command(name="add-time", description=langText["COMMAND_DESCRIPTION"]["COMMAND_ADD_TIME"])
    async def add_time(self, interaction: disnake.ApplicationCommandInteraction, duration: int, giveaway: str):
        await interaction.response.defer(ephemeral=True)
        for gw in self.giveaways:
            if str(gw.message.id) == giveaway:
                giveaway = gw
                break
        giveaway.add_time(duration)
        giveaway.update_message()
        embed = disnake.Embed(title=langText["EMBED"]["ADDTIME_TITLE"],
                              description=langText["EMBED"]["ADDTIME_DESCRIPTION"].format(time=duration),
                              color=disnake.Color.green())
        await interaction.followup.send(embed=embed)

    @giveaway.sub_command(name="remove-time", description=langText["COMMAND_DESCRIPTION"]["COMMAND_REMOVE_TIME"])
    async def remove_time(self, interaction: disnake.ApplicationCommandInteraction, duration: int, giveaway: str):
        await interaction.response.defer(ephemeral=True)
        for gw in self.giveaways:
            if str(gw.message.id) == giveaway:
                giveaway: gw_utils.Giveaway = gw
                break
        if duration > giveaway.duration:
            embed = disnake.Embed(title=langText["ERROR"]["TITLE"],
                                  description=langText["ERROR"]["TIME_LESS_THAN_0"],
                                  color=disnake.Color.red())
            await interaction.followup.send(embed=embed)
            return
        giveaway.remove_time(duration)
        embed = disnake.Embed(title=langText["EMBED"]["REMOVED_TIME_TITLE"],
                              description=langText["EMBED"]["REMOVED_TIME_TITLE"].format(time=duration),
                              color=disnake.Color.green())
        await interaction.followup.send(embed=embed)

    @giveaway.sub_command(name="end", description=langText["COMMAND_DESCRIPTION"]["COMMAND_END"])
    async def end(self, interaction: disnake.ApplicationCommandInteraction, giveaway: str):
        await interaction.response.defer(ephemeral=True)
        for gw in self.giveaways:
            if str(gw.message.id) == giveaway:
                giveaway: gw_utils.Giveaway = gw
                break
        giveaway.end_timestamp = int(datetime.now().timestamp()) + 1
        embed = disnake.Embed(title=langText["EMBED"]["END_TITLE"],
                              description=langText["EMBED"]["END_DESCRIPTION"],
                              color=disnake.Color.green())
        await interaction.followup.send(embed=embed)

    @giveaway.sub_command(name="reroll", description=langText["COMMAND_DESCRIPTION"]["COMMAND_REROLL"])
    async def reroll(self, interaction: disnake.ApplicationCommandInteraction, giveaway: str):
        await interaction.response.defer(ephemeral=True)
        for gw in self.giveaways:
            if str(gw.message.id) == giveaway:
                giveaway: gw_utils.Giveaway = gw
                break
        if not giveaway.finished:
            embed = disnake.Embed(title=langText["ERROR"]["TITLE"],
                                  description=langText["ERROR"]["NOT_FINISHED"],
                                  color=disnake.Color.red())
            await interaction.followup.send(embed=embed)
            return
        giveaway.reroll()
        embed = disnake.Embed(title=langText["EMBED"]["REROLL_TITLE"],
                              description=langText["EMBED"]["REROLL_DESCRIPTION"],
                              color=disnake.Color.green())
        await interaction.followup.send(embed=embed)

    @giveaway.sub_command(name="list", description=langText["COMMAND_DESCRIPTION"]["COMMAND_LIST"])
    async def list(self, interaction: disnake.ApplicationCommandInteraction):
        await interaction.response.defer(ephemeral=True)
        embed = disnake.Embed(title=langText["EMBED"]["LIST_TITLE"],
                              description=langText["EMBED"]["LIST_DESCRIPTION"],
                              color=disnake.Color.blue())
        for gw in self.giveaways:
            if not gw.finished:
                embed.add_field(name="__" + gw.prize + "__",
                                value=langText["EMBED"]["LIST_FIELD"].format(gw_participants=len(gw.participants), end_timestamp=gw.end_timestamp, channel_mention=gw.message.channel.mention),
                                inline=False)
        await interaction.followup.send(embed=embed)

    @add_time.autocomplete("giveaway")
    @remove_time.autocomplete("giveaway")
    @end.autocomplete("giveaway")
    async def gw_running_autocomplete(self, interaction: disnake.ApplicationCommandInteraction, value: str):
        print(self.giveaways)
        choices = {}
        for gw in self.giveaways:
            if not gw.finished:
                choices[f"{gw.prize} - {gw.render_participant_text()}"] = str(gw.message.id)
        if len(choices) == 0:
            return [langText["NO_GIVEAWAY_FOUND"]]
        return choices
    
    @reroll.autocomplete("giveaway")
    async def gw_autocomplete(self, interaction: disnake.ApplicationCommandInteraction, value: str):
        choices = {}
        for gw in self.giveaways:
            choices[f"{gw.prize} - {gw.render_participant_text()}"] = str(gw.message.id)
        if len(choices) == 0:
            return [langText["NO_GIVEAWAY_FOUND"]]
        return choices

def setup(bot):
    bot.add_cog(GiveawayCog(bot))
