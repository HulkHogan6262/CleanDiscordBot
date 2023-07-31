import disnake
from disnake.ext import commands
import json

class OtherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('========== ⚙️ Music ⚙️ ==========')
        print('🔩 /help has been loaded')
        print('🔩 /ping has been loaded')
        print('🔩 /poll has been loaded')

    @commands.slash_command(name="help", description="Show the list of available commands")
    async def help(self, ctx):
        embed = disnake.Embed(title="Need Help ?", color=disnake.Color.blurple())
        embed.description = f"📚  Welcome to the command list of **{self.bot.user.name}**!\nHere you can find all the available commands and their usage."
        embed.add_field(name="Commands List", value="🔗  To view the list of commands, click [**here**](https://github.com/Zerbaib/CleanDiscordBot/blob/main/CMD.md)", inline=False)
        embed.set_footer(text="Clean Discord Bot", icon_url=self.bot.user.avatar.url)
        await ctx.response.defer()
        await ctx.send(ephemeral=True, embed=embed)

    @commands.slash_command(name="ping", description="Get the bot's latency",)
    async def ping(self, ctx):
        try:
            embed = disnake.Embed(
                title=f"Pong!",
                description=f"The ping is around `{round(self.bot.latency * 1000)}ms`",
                color=disnake.Color.random()
                )
            embed.set_footer(text=f'Command executed by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.response.defer()
            await ctx.send(ephemeral=True, embed=embed)
        except Exception as e:
            embed = disnake.Embed(
                title=f"Error during the ``/ping``",
                description=f"```{e}```",
                color=disnake.Color.red()
                )
            embed.set_footer(text=f'Command executed by {ctx.author}', icon_url=ctx.author.avatar.url)
            await ctx.response.send_message(embed=embed)

    @commands.slash_command(name="poll", description="Create a poll")
    async def poll(self, ctx, question: str):
        try:
            with open("config.json", 'r') as config_file:
                config = json.load(config_file)
            channel_id = config.get("POLL_ID")

            if not channel_id:
                await ctx.send("Poll channel ID is not specified in the configuration.")
                return

            channel = self.bot.get_channel(channel_id)
            if not channel:
                await ctx.send("Invalid poll channel ID.")
                return

            embed = disnake.Embed(
                title="New Poll",
                description=f"```{question}```",
                color=disnake.Color.blurple()
            )
            embed.set_footer(text=f"New poll from {ctx.author}")
            
            message = await channel.send(embed=embed)
            await message.add_reaction("👍")
            await message.add_reaction("◻️")
            await message.add_reaction("👎")

            await ctx.response.defer()
            await ctx.send("Poll created successfully.", ephemeral=True)
        except Exception as e:
            embed = disnake.Embed(
                title="Error during `/poll`",
                description=f"```{e}```",
                color=disnake.Color.dark_red()
            )
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(OtherCog(bot))
