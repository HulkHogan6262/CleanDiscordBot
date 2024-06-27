import subprocess

# Config files
configFilesFolder = "./config/"
envFilePath = f"{configFilesFolder}.env"
configFilePath = f"{configFilesFolder}config.json"
badWordFilePath = f"{configFilesFolder}bad_words.json"

# Parameters
dataFileLoad = True
multiplicator = 65
minXpIncrement = 1
maxXpIncrement = 5

# Time gestion
timeSeconds = 1
timeMinutes = timeSeconds * 60
timeHours = timeMinutes * 60
timeDays = timeHours * 24
timeWeeks = timeDays * 7
timeMonths = timeDays * 30
timeYears = timeDays * 365

cooldownTime = timeHours * 2

timeUnits = {
    "s": timeSeconds,
    "m": timeMinutes,
    "h": timeHours,
    "D": timeDays,
    "W": timeWeeks,
    "M": timeMonths,
    "A": timeYears
}

# Language possible
langPossible = [
    "EN",
    "FR",
]

# Data files
dataFilePath = {
    "giveaway": "./data/giveaway.json"
}
dataDbFilePath = "./data/data.db"

# Cogs folder
cogsFolder = "./cogs/"

# Repos link
githubLink = "https://github.com"
githubRawLink = "https://raw.githubusercontent.com"
gitBranch = f"/{subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode().strip()}"
repoGithub = "/Zerbaib/CleanDiscordBot"

# Version link
localVersionFilePath = "./version.txt"
versionLink = "/version.txt"
onlineVersion = f"{githubRawLink}{repoGithub}{gitBranch}{versionLink}"
