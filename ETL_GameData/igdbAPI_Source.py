import requests
import pandas as pd

while True:
    user_game = input("Enter name of a game: ")

    # Connect to Twitch
    auth_url = 'https://id.twitch.tv/oauth2/token'
    client_id = 'di7gbmcflsjq5tmvubn5do24a2q95y'
    client_secret = 'rfx0slvvx8za16iycvchqhponzd01d'

    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    
    response = requests.post(auth_url, data=payload)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()
        access_token = data['access_token']
    else:
        print("Failed to obtain access token. Status code:", response.status_code)

    bearer = 'Bearer %s' % access_token

    headers = {
        'Client-ID': client_id,
        'Authorization': bearer,
    }

    params = {
        'fields': 'id, name, rating, first_release_date',
        'search': user_game,
    }

    main_url = 'https://api.igdb.com/v4/games'
    response = requests.get(main_url, headers=headers, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()
        if data:
            df = pd.DataFrame(data)
            df['first_release_date'] = pd.to_datetime(df['first_release_date'], unit='s')
            df_filtered = df.dropna(subset=['rating'])
            df_sorted = df_filtered.sort_values(by='id', ascending=True)
            print(df_sorted.head(1).to_string(index=False))
        else:
            print("No data found")
    else:
        print("Failed to fetch data from IGDB.com API. Status code:", response.status_code)
        