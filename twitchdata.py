"""
Module for managing Twitch API authentication and URLs.
"""

# Create data class
class TwitchData:
    """
    Class for managing Twitch API authentication and URLs.
    """
    def __init__(self):
        self.auth_url = 'https://id.twitch.tv/oauth2/token'
        self.client_id = 'di7gbmcflsjq5tmvubn5do24a2q95y'
        self.client_secret = 'rfx0slvvx8za16iycvchqhponzd01d'
        self.main_url = 'https://api.igdb.com/v4/games'

    def get_auth(self):
        """
        Get the authentication URL.
        """
        return self.auth_url

    def get_id(self):
        """
        Get the client ID.
        """
        return self.client_id

    def get_secret(self):
        """
        Get the client secret.
        """
        return self.client_secret

    def get_main(self):
        """
        Get the main URL.
        """
        return self.main_url
