# crypto-volume-bot

Note 1: This is not complete (though it does work). There's a to do list:
- Rework algo that triggers alerts (only display top volume breakouts)
- Add support for dex-only tokens
- Add other alert methods vs just Discord (directly to command line, telegram, whatever else)
- Error handling
- Hosting
- Clean up code (made this in a very short period of time)

Note 2: I recommend not using the Twitter follows feature unless you're familiar with the Twitter developer's API and its rate limits. Comments in the code explain why. It also takes more setup than the volume feature.

## What does this do?
It scans for volume spikes on specific tokens (exchange/tickers can be edited in the code), as well as scans for specific Twitter users following new accounts. Alerts can be posted to Discord channels. 

## Layout
All files are commented to explain any of this further, but here's a broad overview:
- .env.template - Template for environment variables
- requirements.txt - List of requirements (install with pip or preferred package manager)
- bot.py - Entry point. Initializes things, begins the scanning loop, and takes care of sending out alerts
- worker.py - Takes care of scanning for volume spikes, including making calls to the exchange and running the logic to determine what a spike is
- followed.py - Takes care of scanning for when specific Twitter users follow someone new

## Running
Requirements:
- Discord channel with a bot that you have the token for and that has the ability to send messages in the channel you want
- Create a .env file and fill in according to the template
- Ensure dependencies are installed (requirements.txt lists them)
- Run through code to ensure it is grabbing what you want (see Defaults below)
- A Twitter Developer's account is required for the Twitter feature, as you need a key and secret to call it

If you just want to detect volume spikes, run "python3 bot.py" or "python bot.py", whatever works for you.

If you want to detect new Twitter follows as well, make sure you have looked into follows.py and updated code accordingly. You also should read the comments. To run it with this feature as well, run "python3 bot.py -t".

## Defaults
All defaults can be changed directly in the files.

By default, the bot scans for volume spikes every 30 minutes. It scans Binance perps using the tickers defined in worker.py, and alerts are triggered according to the algorithm defined in bot.py (determineAlert function). Default tickers scanned are:
'FTM', 'AVAX', 'NEAR', 'RUNE', 'DOT', 'AXS', 'ENJ', 'LINK','MATIC', 'FTT', 'SRM', 'MKR', 'XTZ', 'ATOM', 'CHZ', 'ALGO','1INCH', 'MANA', 'LRC', 'YFI', 'GRT', 'SNX', 'SUSHI', 'LUNA', 'SOL'

If you run the Twitter part as well, it will scan for the users you request (must edit the code yourself for this, and beware rate limits) every time it scans for volume as well.
