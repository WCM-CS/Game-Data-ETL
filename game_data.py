# Imports
import requests
import pandas as pd
from twitchdata import TwitchData
from bs4 import BeautifulSoup 

# Game data class to store extract and merge functions 
class GameData:
    # Default constuctor
    def __init__(self):
        # Private Attributes
        self.__game_prices_dict = {
            'Assassin\'s Creed II': 59.99, 
            'Batman: Arkham Asylum': 49.99, 
            'Call of Duty: Black Ops': 59.99, 
            'Dying Light': 59.99, 
            'Far Cry 3': 59.99, 
            'Grand Theft Auto V': 59.99, 
            'Halo: Reach': 59.99, 
            'Portal 2': 49.99
        }
        self.__ign_game_url = [
            'https://www.ign.com/games/halo-reach',
            'https://www.ign.com/games/portal-2',
            'https://www.ign.com/games/assassins-creed-ii',
            'https://www.ign.com/games/far-cry-3',
            'https://www.ign.com/games/batman-arkham-asylum',
            'https://www.ign.com/games/dying-light',
            'https://www.ign.com/games/grand-theft-auto-v',
            'https://www.ign.com/games/call-of-duty-black-ops'
        ]
        self.__metacritic_game_url = [
            'https://www.metacritic.com/game/halo-reach/',
            'https://www.metacritic.com/game/portal-2/',
            'https://www.metacritic.com/game/assassins-creed-ii/',
            'https://www.metacritic.com/game/far-cry-3/',
            'https://www.metacritic.com/game/batman-arkham-asylum/',
            'https://www.metacritic.com/game/dying-light/',
            'https://www.metacritic.com/game/grand-theft-auto-v/',
            'https://www.metacritic.com/game/call-of-duty-black-ops/'
        ]
        
        self.__headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"} 
        
        self.__sales_game_list = list(self.__game_prices_dict.keys())
        
        self.__sales_df = pd.DataFrame()
        self.__ign_df = pd.DataFrame()
        self.__metacritic_df = pd.DataFrame()
        self.__igdb_df = pd.DataFrame()
        self.__main_df = pd.DataFrame()
        
        self.__void = 0
        
    def set_sales_df(self, df):
        self.__sales_df = df
    def get_sales_df(self):
        return self.__sales_df
    
    def set_ign_df(self, df):
        self.__ign_df = df
    def get_ign_df(self):
        return self.__ign_df
    
    def set_metacritic_df(self, df):
        self.__metacritic_df = df
    def get_metacritic_df(self):
        return self.__metacritic_df
    
    def set_igdb_df(self, df):
        self.__igdb_df = df
    def get_igdb_df(self):
        return self.__igdb_df
    
    
    def igdb_authenticate(self, twitch_data):
        """
        Authenticate IGDB API request.
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
    
    def fetch_game_data(self, access_token_param, user_game_param, twitch_data_param):
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
            'fields': 'id,name,total_rating,first_release_date',
            'search': user_game_param,
        }

        # IGDB API endpoint
        main_url = twitch_data_param.get_main()

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
                #df_filtered = df.dropna(subset=['rating'])
                df_filtered = df.dropna(subset=['total_rating'])
            # df_filtered['total_rating'] = df_filtered['total_rating'].round(2)
                df_filtered.loc[:, 'total_rating'] = df_filtered['total_rating'].round(2)
                # Sorts by Game ID ascending because the lowest ID will likely be the main game
                df_sorted = df_filtered.sort_values(by='id', ascending=True)
                return df_sorted.head(1)
            else:
                alt_msg = "No data found, retry the title."
                return alt_msg
        else:
            error_msg = f'Failed to fetch data from IGDB.com API. Status code: {response.status_code}'
            raise ValueError(error_msg)
        
    # Returns the game sales data (merges prices dict into ouput)
    def get_sales_data(self):
        #Create datframe from csv file
        df = pd.read_csv('Sales_data/vgsales.csv')

        #filter dataframe based on the game_list
        filtered_df = df[df['Name'].str.lower().isin(x.lower() for x in self.__sales_game_list)]

        # Select only 'Name', 'Genre', 'Global_Sales', and 'NA_Sales' columns
        filtered_df = filtered_df[['Name', 'Genre', 'Global_Sales', 'NA_Sales']]

        # Group by game name and sum up the global sales, using an alias for the aggregated column
        total_sales = filtered_df.groupby(['Name','Genre']).agg(
            sum_global_sales=('Global_Sales', lambda x: round(x.sum(), 2)),
            sum_NA_sales=('NA_Sales', lambda x: round(x.sum(), 2))
            ).reset_index()
        
        # Create dataframe from class attribute prices dictionary
        price_df = pd.DataFrame(self.__game_prices_dict.items(), columns=['Name', 'Price'])
        
        # Merge the total_sales and the gam_prices dataframes on name
        merged_df = pd.merge(total_sales, price_df, on = 'Name', how = 'left')
        # Set the df to the class attribute
        self.set_sales_df(merged_df)
        return self.__void
    
    # Returns the ign data
    def get_ign_data(self):
        # Create temp df
        df = pd.DataFrame(columns=['Name', 'IGN_Rating'])
        # Iterate through url list
        for url in self.__ign_game_url:
            # Request html
            html_page = requests.get(url, headers=self.__headers)

            # Parse HTML with beautiful soup
            soup = BeautifulSoup(html_page.content, 'html.parser')

            # Extract the outer most parent div containing the game name and rating
            main_element = soup.find('main', id='main-content')

            # Find the inner parent div
            parent_div = main_element.find('div', class_='stack jsx-1500469411 object-header')

            # Extract the required elements 
            game_name = parent_div.find('h1', class_='display-title').text.strip()
            rating = parent_div.find('span', class_='hexagon-content-wrapper').text.strip()
            
            # Load data into df
            df = df._append({'Name': game_name, 'IGN_Rating': rating}, ignore_index=True)
        df_sorted = df.sort_values(by='Name')
        self.set_ign_df(df_sorted)
        return self.__void
    
    # Returns the metacritic data
    def get_metacritic_data(self):
        # Create temp df
        df = pd.DataFrame(columns=['Name', 'Metacritic_Rating'])
        # Iterate through url list
        for url in self.__metacritic_game_url:
            # Request html
            html_page = requests.get(url, headers=self.__headers)

            # Parse HTML with beautiful soup
            soup = BeautifulSoup(html_page.content, 'html.parser')

            # Extract the outer most parent div containing the game name and rating
            main_element = soup.find('div', class_='c-productHero')

            # Extract game name
            game_name = main_element.find('div', class_='c-productHero_title').h1.get_text(strip=True)

            # Extract Metascore rating
            rating = main_element.find('div', class_='c-productScoreInfo_scoreNumber').span.get_text(strip=True)

            # Load data into df
            df = df._append({'Name': game_name, 'Metacritic_Rating': rating}, ignore_index=True)
        df_sorted = df.sort_values(by='Name')
        self.set_metacritic_df(df_sorted)
        return self.__void
    
    # Returns the igdb data
    def get_igdb_data(self):
        # Initialize data class
        data_instance = TwitchData()
        
        # list to store dataframes
        igdb_ls = []
        
        # iterate through games list grabbing data and storing in the df 
        for game in self.__sales_game_list:
            twitch_access_token = self.igdb_authenticate(data_instance)
            game_data_results = self.fetch_game_data(twitch_access_token, game, data_instance)
            igdb_ls.append(game_data_results) 
            
        # concatenate all dataframes in the list
        igdb_df = pd.concat(igdb_ls, ignore_index=True)
        igdb_df_transformed= igdb_df.drop(columns=['id'])
        
        # Rename columns
        igdb_df_transformed.rename(columns={'name': 'Name', 'total_rating': 'Total_Rating', 'first_release_date': 'First_Release_Date'}, inplace=True)
        self.set_igdb_df(igdb_df_transformed)
        return self.__void
    
    def merge_data(self):
        return self.__void
    

gd = GameData()

gd.get_sales_data()
print(gd.get_sales_df())

gd.get_ign_data()
print(gd.get_ign_df())

gd.get_metacritic_data()
print(gd.get_metacritic_df())

gd.get_igdb_data()
print(gd.get_igdb_df())

