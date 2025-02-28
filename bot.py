#!/usr/bin/env python3
"""MLB daily times and scores bot for Discord."""

import logging
import sys
import datetime
import os

import discord
import statsapi
import pytz

from table2ascii import table2ascii as t2a, PresetStyle

BOT_TOKEN = os.getenv("BOT_TOKEN")

TEAM_DATA = {
    "Arizona Diamondbacks": "ARI",
    "Atlanta Braves": "ATL",
    "Baltimore Orioles": "BAL",
    "Boston Red Sox": "BOS",
    "Chicago White Sox": "CWS",
    "Chicago Cubs": "CHC",
    "Cincinnati Reds": "CIN",
    "Cleveland Guardians": "CLE",
    "Colorado Rockies": "COL",
    "Detroit Tigers": "DET",
    "Houston Astros": "HOU",
    "Kansas City Royals": "KC ",
    "Los Angeles Angels": "LAA",
    "Los Angeles Dodgers": "LAD",
    "Miami Marlins": "MIA",
    "Milwaukee Brewers": "MIL",
    "Minnesota Twins": "MIN",
    "New York Yankees": "NYY",
    "New York Mets": "NYM",
    "Athletics": "OAK",
    "Philadelphia Phillies": "PHI",
    "Pittsburgh Pirates": "PIT",
    "San Diego Padres": "SD ",
    "San Francisco Giants": "SF ",
    "Seattle Mariners": "SEA",
    "St. Louis Cardinals": "STL",
    "Tampa Bay Rays": "TB ",
    "Texas Rangers": "TEX",
    "Toronto Blue Jays": "TOR",
    "Washington Nationals": "WSH"
}

# Set up logging to stdout
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, handlers=[handler])

# Manage discord intents
intents = discord.Intents.default()
intents.message_content = True

# Create Discord client
client = discord.Client(intents=intents)

async def get_games(date):
    """Get game data."""
    sched = statsapi.schedule(date=date)
    return sched

async def display_game_info():
    """Get, format, and return game data."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    games = await get_games(today)
    now = datetime.datetime.now(pytz.utc)
    eastern_zone = pytz.timezone("America/New_York")
    embed = discord.Embed(title=f"MLB Game Schedule - {today}", color=discord.Color.blue())

    table_data = []

    for game in games:
        utc_time_str = game['game_datetime']
        utc_time = datetime.datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
        utc_time = pytz.utc.localize(utc_time)
        eastern_time = utc_time.astimezone(eastern_zone)
        formatted_time = eastern_time.strftime("%I:%M %p").lstrip("0")

        home_abv = TEAM_DATA[game['home_name']]
        away_abv = TEAM_DATA[game['away_name']]

        if now < utc_time:
            # Game is in the future
            table_data.append([away_abv, "", home_abv, "", formatted_time])
        else:
            # Game is in the past or ongoing
            if game['status'] == 'Final':
                if game['current_inning'] > 9:
                    table_data.append([away_abv, game['away_score'],
                                       home_abv, game['home_score'],
                                       f"FINAL/{game['current_inning']}"])
                else:
                    table_data.append([away_abv,
                                        game['away_score'],
                                        home_abv,
                                        game['home_score'],
                                        "FINAL"])
            else:
                table_data.append([away_abv, game['away_score'],
                                   home_abv, game['home_score'],
                                   f"{game['inning_state']} {game['current_inning']}"])

    formatted_table = t2a(
        header=["AWAY", "SCORE", "HOME", "SCORE", "TIME/INNING"],
        body=table_data,
        style=PresetStyle.thin_box
    )

    embed.description = f"```{formatted_table}```"

    return embed

@client.event
async def on_ready():
    """Ready Events."""
    logging.info('We have logged in as %s', client.user)

@client.event
async def on_message(message):
    """Main Function"""
    if message.author == client.user:
        return
    try:
        if message.content.startswith('.mlb'):
            logging.info('Received message: %s from %s', message.content, message.author)
            embed = await display_game_info()
            await message.channel.send(embed=embed)
    except discord.DiscordException as e:
        logging.error('Discord error: %s', e)
    except Exception as e:
        logging.error('Unexpected error: %s', e)

client.run(BOT_TOKEN, log_handler=handler, root_logger=True)
