import disnake
import asyncio
import random
from disnake.ext import commands
from datetime import datetime
from utils.load_lang import giveaway_lang as langText

class Giveaway:
    def __init__(self, bot: commands.Bot, guild: disnake.Guild, duration: int, winners: int = 1, message: disnake.Message | None = None, prize: str = "Aucun prix défini"):
        self._bot: commands.Bot = bot
        self.participants: list[disnake.Member] = []
        self.start_timestamp: int = int(datetime.now().timestamp())
        self.end_timestamp: int = self.start_timestamp + duration
        self.duration: int = duration
        self.winners: list[disnake.Member] = []
        self.winner_count: int = winners
        self.finished: bool = False
        self.message: disnake.Message | None = message
        self.prize: str = prize
        self.guild: disnake.Guild = guild
        self._embed: disnake.Embed = None
        self._old_len: int = 0
        self._old_duration: int = duration
        self._button: GiveawayButton | DisabledGiveawayButton = GiveawayButton(giveaway=self)

    def add_participant(self, member: disnake.Member) -> bool:
        """
        Add a member to the giveaway participants list
        :param member: The member to add
        :return: True if the member has been added, False otherwise
        """
        if member in self.participants:
            return False
        self.participants.append(member)
        return True
    
    def remove_participant(self, member: disnake.Member) -> bool:
        """
        Remove a member from the giveaway participants list
        :param member: The member to remove
        :return: True if the member has been removed, False otherwise
        """
        if member not in self.participants:
            return False
        self.participants.remove(member)
        return True
    
    def member_participate(self, member: disnake.Member) -> bool:
        """
        Verify if a member is participating in the giveaway
        :param member: The member to verify
        :return: True if the member is participating, False otherwise
        """
        return member in self.participants
    
    def add_time(self, time: int) -> None:
        """
        Add time to the giveaway duration
        :param time: The time to add in seconds
        :return: None
        """
        self.end_timestamp += time
        self.duration += time

    def remove_time(self, time: int) -> bool:
        """
        Remove time from the giveaway duration
        :param time: The time to remove in seconds
        :return: True if the time has been removed, False otherwise
        """
        if self.duration - time < 0:
            return False
        else:
            self.end_timestamp -= time
            self.duration -= time

    def choose_winner(self) -> None:
        """
        Choose the giveaway winners
        :return: None
        """
        if len(self.participants) <= self.winner_count:
            self.winners = self.participants
        else:
            self.winners = random.sample(self.participants, self.winner_count)

    def reroll(self) -> None:
        """
        Reroll the giveaway
        :return: None
        """
        self.choose_winner()
        self.update_message()
        self.send_win_message()

    def build_embed(self) -> disnake.Embed:
        """
        Build the giveaway embed
        :return: The giveaway embed
        """
        if self.finished:
            embed = disnake.Embed(title=langText["FINISHED_TITLE"],
                                    color=disnake.Color.red())
            embed.add_field(name=langText["FIELD_ENDED_NAME"], value=f"<t:{str(self.end_timestamp)}:R>")
            embed.add_field(name=langText["FIELD_PRIZE_NAME"], value=", ".join([winner.mention for winner in self.winners]) if self.winners else langText["NO_PARTICIPANTS_END"])
            embed.add_field(name=langText["FIELD_WINNER_NAME"], value=self.prize)
            embed.set_footer(text=langText["GIVEAWAY_FOOTER"].format(guild=self.guild.name))
        else:
            embed = disnake.Embed(title=langText["GIVEAWAY_TITLE"],
                                    color=disnake.Color.green())
            embed.add_field(name=langText["FIELD_END_NAME"], value=f"<t:{str(self.end_timestamp)}:R>")
            embed.add_field(name=langText["FIELD_PARTICIPANTS_NAME"], value=f"{str(len(self.participants))} participant{'s' if len(self.participants) > 1 else ''}")
            embed.add_field(name=langText["FIELD_PRIZE_NAME"], value=self.prize)
            embed.set_footer(text=langText["GIVEAWAY_FOOTER"].format(guild=self.guild.name))
        return embed

    def send_win_message(self) -> None:
        """
        Send the giveaway win message
        :return: None
        """
        if self.finished:
            if self.winners:
                for winner in self.winners:
                    asyncio.run_coroutine_threadsafe(self.message.channel.send(f"Félicitations à {winner.mention} qui vient de remporter **{self.prize}** !"), self._bot.loop)
            else:
                asyncio.run_coroutine_threadsafe(self.message.channel.send("Personne n'a participé au giveaway..."), self._bot.loop)
    
    def update_message(self) -> None:
        """
        Update the giveaway message
        :return: None
        """
        embed = self.build_embed()
        if self.message:
            asyncio.run_coroutine_threadsafe(self.message.edit(content="", embed=embed, view=self._button), self._bot.loop)

    def render_participant_text(self) -> str:
        """
        Render the participant text
        """
        if len(self.participants) == 0:
            return langText["NO_PARTICIPANTS"]
        elif len(self.participants) == 1:
            return langText["ONE_PARTICIPANT"]
        else:
            return langText["MULTIPLE_PARTICIPANTS"].format(participants=len(self.participants))
    
    def update(self) -> None:
        """
        Update the giveaway
        :return None:
        """
        event = False
        # Verify if the member is on the guild
        for participant in self.participants:
            if participant not in self.guild.members:
                self.participants.remove(participant)
                event = True
        # Verify if the giveaway is finished
        if self.end_timestamp <= int(datetime.now().timestamp()):
            self.finished = True
            self._button = DisabledGiveawayButton()
            if len(self.participants) <= self.winner_count:
                self.winners = self.participants
            else:
                self.winners = random.sample(self.participants, self.winner_count)
            self.send_win_message()
            event = True
        # Verify if the length of the participants list has changed
        if self._old_len != len(self.participants):
            self._old_len = len(self.participants)
            event = True
        # Verify if the duration has changed
        if self._old_duration != self.duration:
            self._old_duration = self.duration
            event = True
        # Update the embed if an event has been detected
        if event:
            self.update_message()


class GiveawayButton(disnake.ui.View):
    def __init__(self, giveaway: Giveaway):
        super().__init__()
        self.giveaway = giveaway

    @disnake.ui.button(label=langText["PARTICIPATION_BUTTON"], style=disnake.ButtonStyle.green)
    async def participate(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if not self.giveaway.member_participate(interaction.user):
            self.giveaway.add_participant(interaction.user)
            await interaction.response.send_message("Vous avez bien été ajouté à la liste des participants !", ephemeral=True)
        else:
            self.giveaway.remove_participant(interaction.user)
            await interaction.response.send_message("Vous avez bien été retiré de la liste des participants !", ephemeral=True)

class DisabledGiveawayButton(disnake.ui.View):
    def __init__(self):
        super().__init__()

    @disnake.ui.button(label=langText["PARTICIPATION_BUTTON"], style=disnake.ButtonStyle.green, disabled=True)
    async def participate(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        pass