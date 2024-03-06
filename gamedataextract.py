"""
This module extracts data from IGDB based on user input of a game's name.
This is the Extract layer of a ETL dataflow.
Goal: Turn this into a python lambda in AWS &
connect via gateway to a front end hosted in S3.
Potentially attach a DB for further use cases.
"""

# Imports
import requests
import pandas as pd

# continues to run until program is closed
if __name__ == '__main__':
    while True:
        # Prompt user answer
        user_game = input("Enter name of a game: ")
        # Twitch authentication variables
        AUTH_URL = 'https://id.twitch.tv/oauth2/token'
        CLIENT_ID = 'di7gbmcflsjq5tmvubn5do24a2q95y'
        CLIENT_SECRET = 'rfx0slvvx8za16iycvchqhponzd01d'

        payload = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'client_credentials'
        }

        # Auth post request
        response = requests.post(AUTH_URL,data=payload,timeout=10)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            access_token = data['access_token']
        else:
            print(f'Failed to obtain access token. Status code: {response.status_code}')

        bearer = f'Bearer {access_token}'

        headers = {
            'Client-ID': CLIENT_ID,
            'Authorization': bearer,
        }

        params = {
            'fields': 'id,name,rating,first_release_date',
            'search': user_game,
        }

        # IGDB API endpoint
        MAIN_URL = 'https://api.igdb.com/v4/games'

        # IGDB Get Request
        response = requests.get(MAIN_URL,headers=headers,params=params,timeout=10)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            if data:
                # Turns the json into a pandas dataframe
                df = pd.DataFrame(data)
                # Transforms unix timestamp into data time format
                df['first_release_date'] = pd.to_datetime(df['first_release_date'],unit='s')
                # Drops rows without rating because it's not a game its a DLC or extra add ons
                df_filtered = df.dropna(subset=['rating'])
                # Sorts by Game ID Ascending because the lowest ID will likely be the main game
                df_sorted = df_filtered.sort_values(by='id',ascending=True)
                # Prints the given row after converting to a string
                print(df_sorted.head(1).to_string(index=False))
            else:
                print("No data found")
        else:
            print(f'Failed to fetch data from IGDB.com API. Status code: {response.status_code}')
