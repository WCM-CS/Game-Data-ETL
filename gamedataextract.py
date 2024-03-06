"""
This module extracts data from IGDB based on user input of a game's name.
This is the Extract layer of an ETL dataflow.
Goal: Turn this into a python lambda in AWS &
connect via gateway to a front end hosted in S3.
Potentially attach a DB for further use cases.
"""

import requests
import pandas as pd
from twitchdata import TwitchData

def get_user_input(prompt):
    """
    Prompt the user for input.
    """
    return input(prompt)

def authenticate_twitch(twitch_data):
    """
    Authenticate request.
    """
    auth_url = twitch_data.get_auth()
    client_id = twitch_data.get_id()
    client_secret = twitch_data.get_secret()

    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    # Auth post request
    response = requests.post(auth_url, data=payload, timeout=10)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()
        access_token = data['access_token']
        return access_token
    else:
        error_msg = f'Failed to obtain access token. Status code: {response.status_code}'
        raise ValueError(error_msg)

def fetch_game_data(access_token_param, user_game_param, twitch_data_param):
    """
    Return the data for the requested game.
    """
    client_id = twitch_data_param.get_id()

    bearer = f'Bearer {access_token_param}'
    headers = {
        'Client-ID': client_id,
        'Authorization': bearer,
    }

    params = {
        'fields': 'id,name,rating,first_release_date',
        'search': user_game_param,
    }

    # IGDB API endpoint
    main_url = 'https://api.igdb.com/v4/games'

    # IGDB Get Request
    response = requests.get(main_url, headers=headers, params=params, timeout=10)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()
        if data:
            # Turns the JSON into a pandas DataFrame
            df = pd.DataFrame(data)
            # Transforms Unix timestamp into datetime format
            df['first_release_date'] = pd.to_datetime(df['first_release_date'], unit='s')
            # Drops rows without rating because it's not a game, it's a DLC or extra add ons
            df_filtered = df.dropna(subset=['rating'])
            # Sorts by Game ID ascending because the lowest ID will likely be the main game
            df_sorted = df_filtered.sort_values(by='id', ascending=True)
            # Prints the given row after converting to a string
            transformed_data = df_sorted.head(1).to_string(index=False)
            return transformed_data
        else:
            alt_msg = "No data found, retry the title."
            return alt_msg
    else:
        error_msg = f'Failed to fetch data from IGDB.com API. Status code: {response.status_code}'
        raise ValueError(error_msg)

# Main block of code
if __name__ == '__main__':
    # Initialize data class
    data_instance = TwitchData()

    while True:
        # Prompt users answer
        user_game_input = get_user_input("Enter the name of a game: ")
        twitch_access_token = authenticate_twitch(data_instance)
        game_data_results = fetch_game_data(twitch_access_token, user_game_input, data_instance)
        print(game_data_results)
