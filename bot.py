import os
import discord
from discord.ext import tasks, commands
from worker import detect
from dotenv import load_dotenv
import argparse

# To do list:
# Rework algo that triggers alerts (only display top volume breakouts)
# Add support for dex-only tokens
# Add other alert methods (directly to command line, telegram, whatever else)
# Error handling
# Hosting
# Clean up code


# ===========================================================================================================
# //                                    Volume Spikes + New Twitter Follows                                //
# //                                                - bHeau                                                //
# ===========================================================================================================

# NOTE: To run the Twitter aspect of this, you need a Twitter developer's account
# If you don't have one or don't wish to run the Twitter part, don't use the -t flag


#================================================ VARIABLES ================================================

# Load env and parse args
load_dotenv()
parser = argparse.ArgumentParser()
parser.add_argument('-t', action='store_true')
args = parser.parse_args()

# Env variables
discord_token = os.getenv('DISCORD_TOKEN')
channel1_id = os.getenv('DISCORD_CHANNELID_VOL')
channel2_id = None

# Discord bot client
client = commands.Bot(command_prefix="/")

# Discord channels, uninitialized but global
channel1 = None
channel2 = None

# List of tokens, should be readable version of list defined in worker.py
tokenList2 = ['FTM', 'AVAX', 'NEAR', 'RUNE', 'DOT', 'AXS', 'ENJ', 'LINK',
            'MATIC', 'FTT', 'SRM', 'MKR', 'XTZ', 'ATOM', 'CHZ', 'ALGO',
            '1INCH', 'MANA', 'LRC', 'YFI', 'GRT', 'SNX', 'SUSHI', 'LUNA', 'SOL']

# Unnecessary unless running the Twitter follows feature (-t flag)
# Twitter API will rate limit the "following" requests to 15 per 15 mins
# Ensure your frequency of calls (defined below above myLoop func) does not hit this
twitterList = ['user1readable', 'user2readable']


#================================================ PRODUCTION ================================================

# Run when bot is started, initializes channels & sends custom message
@client.event
async def on_ready():
    global channel1
    global channel2
    channel1 = client.get_channel(int(channel1_id))
    print("Bot is ready")
    tokenListAlphabetized = sorted(tokenList2, key=str.lower)
    tokensWatched = ", ".join(tokenListAlphabetized)
    await channel1.send("Volume bot is live, watching: " + tokensWatched + '\n\n')
    if(args.t):
        channel2 = client.get_channel(int(channel2_id))
        twittersWatched = ", ".join(twitterList)
        await channel2.send("Also watching twitter accounts: " + twittersWatched + '\n\n')
    myLoop.start()

# Scan for volume spikes and new follows every x amount of minutes
# Can change the frequency in line below
@tasks.loop(minutes=30.0)
async def myLoop():
    scan = detect()
    if(scan != None):
        for x in scan:
            message = str(x)
            await channel1.send(message)
    if(args.t):
        scan2 = scanTwitters()
        if(scan2 != None):
            for y in scan2:
                message = str(y)
                await channel2.send(message)

# Run the bot
if(args.t):
    from followed import prepare, scanTwitters
    channel2_id = os.getenv('DISCORD_CHANNELID_TWIT')
    prepare()
client.run(discord_token)
