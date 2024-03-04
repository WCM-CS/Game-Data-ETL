import requests

class TwitchAPIClient:
    def __init__(self, client_id, client_secret):
        self.client_id = 'di7gbmcflsjq5tmvubn5do24a2q95y'
        self.client_secret = 's6e0fq6zleou5bd4n90ueor7acn9ae'
        self.access_token = None
    
    # function to authenticate API calls
    def authenticate(self):
        # make post request
        url = 'https://id.twitch.tv/oauth2/token'
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        response = requests.post(url, data=payload)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            return True
        else:
            print("Failed to obtain access token. Status code:", response.status_code)
            return False

    # Functioin to fetch data from the API
    def fetch_data_from_igdb(self):
        if not self.access_token:
            authenticated = self.authenticate()
            if not authenticated:
                return None
            
    # Make requests to IGDB.com API using the obtained access token
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Client-ID': self.client_id,
        }
        body = "feilds *; where name=\"Halo Reach\";"
        
        # Example: Fetching data from IGDB.com API
        url = 'https://api.igdb.com/v4/games'
        response = requests.get(url, headers=headers, params=body)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("Failed to fetch data from IGDB.com API. Status code:", response.status_code)
            return None
    