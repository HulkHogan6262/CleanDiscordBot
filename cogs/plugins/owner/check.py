import disnake
import requests
from disnake.ext import commands

from cogs.utils import error
from cogs.utils.color import hex_to_discord_color
from cogs.utils.embed import create_embed
from cogs.utils.lang_loader import load_owner_lang

langText = load_owner_lang()


class OwnerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.online_version_url = "https://raw.githubusercontent.com/Zerbaib/CleanDiscordBot/main/version.txt"

    @commands.Cog.listener()
    async def on_ready(self):
        print('🔩 /check has been loaded')

    def get_local_version(self):
        with open("version.txt", "r") as version_file:
            local_version = version_file.read().strip()
        return local_version

    @commands.slash_command(name="check", description=langText.get("CHECK_DESCRIPTION"))
    @commands.is_owner()
    async def check(self, ctx):
        try:
            
            response = requests.get(self.online_version_url)
            if response.status_code == 200:
                online_version = response.text.strip()
                local_version = self.get_local_version()

                embed = disnake.Embed(
                    title=langText.get("CHECK_TITLE"),
                )
                if online_version == local_version:
                    embed.description = langText.get("CHECK_UPTODATE")
                    embed.colour = disnake.Color.brand_green()
                else:
                    embed.description = langText.get("CHECK_OUTDATED")
                    embed.colour = disnake.Color.brand_red()

                embed.add_field(name=langText.get("CHECK_LOCAL"), value=f"```{local_version}```", inline=True)
                embed.add_field(name=langText.get("CHECK_REMOTE"), value=f"```{online_version}```", inline=True)
                await ctx.response.defer()
                await ctx.send(embed=embed)

        except Exception as e:
            embed = error.error_embed(e)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(OwnerCommands(bot))
