import json
import os
import platform
import i18n
from dotenv import load_dotenv

import aiohttp
import disnake
from disnake.ext import commands


if not os.path.exists(".env"):
    token = input("Enter the bot's token:\n")
    lang_choice = input("Enter the bot's language (en / fr):\n")
    lang_possible = ["en", "fr", "EN", "FR"]
    if lang_choice in lang_possible:
        lang_choice = lang_choice.upper()
    else:
        print("Invalid language, default language is English")
        lang_choice = "EN"
    with open(".env", 'w') as env_file:
        env = f'LANGUAGE="{lang_choice}"'
        env += f'\nTOKEN="{token}"'
        env_file.write(env)

config_file_path = "config.json"
badWord_file_path = "bad_words.json"
casino_data_file_path = "data/casino.json"
rank_data_file_path = "data/ranks.json"
casino_cooldown_data_file_path = "data/cooldown.json"
online_version = "https://raw.githubusercontent.com/Zerbaib/CleanDiscordBot/main/version.txt"

if not os.path.exists(casino_data_file_path):
    with open(casino_data_file_path, 'w') as casino_file:
        json.dump({}, casino_file)
if not os.path.exists(casino_cooldown_data_file_path):
    with open(casino_cooldown_data_file_path, 'w') as casino_cooldown_file:
        json.dump({}, casino_cooldown_file)
if not os.path.exists(rank_data_file_path):
    with open(rank_data_file_path, 'w') as rank_file:
        json.dump({}, rank_file)
if not os.path.exists(badWord_file_path):
    badword_data = {
        "bad_words": [
            "badword1",
            "badword2",
            "badword3"
        ]
    }
    with open(badWord_file_path, 'w') as badword_file:
        json.dump(badword_data, badword_file, indent=4)

if not os.path.exists(config_file_path):
    with open(config_file_path, 'w') as config_file:
        prefix = input("Enter the bot's prefix:\n")
        log_id = int(input("Enter the log's channel ID:\n"))
        poll_id = int(input("Enter the poll's channel ID:\n"))
        join_id = int(input("Enter the join's channel ID:\n"))
        leave_id = int(input("Enter the leave's channel ID:\n"))
        voice_id = int(input("Enter the voice's channel ID\nUsed for create salon on join:\n"))
        id_client = int(input("Enter your Discord ID:\n"))
        mute_id = int(input("Enter role id of muted role:\n"))
        rank1 = int(input("Enter role id of level 10 role:\n"))
        rank2 = int(input("Enter role id of level 25 role:\n"))
        rank3 = int(input("Enter role id of level 50 role:\n"))
        config_data = {
            "PREFIX": prefix,
            "LOG_ID": log_id,
            "POLL_ID": poll_id,
            "JOIN_ID": join_id,
            "LEAVE_ID": leave_id,
            "AUTO_VOICE_ID": voice_id,
            "YOUR_ID": id_client,
            "MUTE_ROLE_ID": mute_id,
            "del_time": 3,
            "level_roles": {
                "10": rank1,
                "25": rank2,
                "50": rank3
            }
        }
        json.dump(config_data, config_file, indent=4)
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)
else:
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)

load_dotenv()

token = os.environ["TOKEN"]
prefix = config["PREFIX"]
ln = os.environ["LANGUAGE"]
ln_lower = ln.lower()

i18n.load_path = ["lang"]
i18n.set = ({
    "file_format": "json",
    "filename_format": "{namespace}.{format}",
    "namespace_delimiter": ":",
    "skip_locale_root_data": True,
    "use_locale_dirs": True,
})

bot = commands.Bot(
    command_prefix=prefix,
    intents=disnake.Intents.all(),
    case_insensitive=True
)
bot.remove_command('help')

@bot.event
async def on_ready():
    if bot.user.discriminator == 0:
        nbot = bot.user.name
    else:
        nbot = bot.user.name + "#" + bot.user.discriminator

    async with aiohttp.ClientSession() as session:
        async with session.get(online_version) as response:
            if response.status == 200:
                bot_repo_version = await response.text()
            else:
                bot_repo_version = "Unknown"

    with open('version.txt', 'r') as version_file:
        bot_version = version_file.read().strip()

    if bot_version != bot_repo_version:
        print()
        print('===============================================')
        print('🛑 You are not using the latest version!')
        print('🛑 Please update the bot.')
        print('🛑 Use "git fetch && git pull" to update your bot.')
    print('===============================================')
    print(f"🔱 The bot is ready!")
    print(f'🔱 Logged in as {nbot} | {bot.user.id}')
    print(f'🔱 Language: {ln.upper()}')
    print(f'🔱 Bot local version: {bot_version}')
    print(f'🔱 Bot online version: {bot_repo_version}')
    print(f"🔱 Disnake version: {disnake.__version__}")
    print(f"🔱 Running on {platform.system()} {platform.release()} {os.name}")
    print(f"🔱 Python version: {platform.python_version()}")
    print('===============================================')

bot.load_extension('cogs.utils.logger')
bot.load_extension('cogs.utils.automod')
bot.load_extension('cogs.utils.status')
bot.load_extension('cogs.utils.voice')

for element in os.listdir(f'cogs/plugins/'):
    try:
        element_dir = f"cogs/plugins/{element}"
        if os.path.isdir(element_dir):
            for filename in os.listdir(element_dir):
                if filename.endswith('.py'):
                    cog_name = filename[:-3]
                    try:
                        bot.load_extension(f'cogs.plugins.{element}.{cog_name}')
                    except Exception as e:
                        print(f"🌪️  Error during '{cog_name}' loading:\n\n{e}")
    except Exception as e:
        print(f"🌪️  Error during '{element}' loading:\n\n{e}")


bot.run(token)