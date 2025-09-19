import requests
import json

class RiotClient:
    _base_url = 'https://americas.api.riotgames.com/'

    def  __init__(self, riot_api_key: str, summoner_name: str, tagline: str) -> None:
        ''' Constructor

        @param summoner_name: in game name
        @param tagline: in game #
        '''
        self.riot_api_key = riot_api_key
        self.puuid = self._set_player_puuid(summoner_name, tagline)

    def _set_player_puuid(self, summoner_name: str, tagline: str) -> str:
        ''' Method sets the puuid for the initialized player

        @param summoner_name: in game name
        @param tagline: in game #

        :return: the puuid of the player
        '''
        # Make request
        url = f'{self._base_url}riot/account/v1/accounts/by-riot-id'
        response = requests.get(f'{url}/{summoner_name}/{tagline}?api_key={self.riot_api_key}')

        if response.status_code != 200:
            raise ValueError(f'Summoner {summoner_name}#{tagline} not found. {response.content}')

        response = response.json()

        return response.get('puuid', '')

    def get_recent_game_ids(self) -> dict:
        ''' Method gets recent games for the initialized player

        :return: list of game dicts
        '''
        url = f'{self._base_url}/lol/match/v5/matches/by-puuid/{self.puuid}/ids'
        response = requests.get(f'{url}?api_key={self.riot_api_key}')

        if response.status_code != 200:
            print('No game data found')

        response = response.json()

        ret = []
        url = f'{self._base_url}lol/match/v5/matches'
        for game_id in response:
            response = requests.get(f'{url}/{game_id}?api_key={self.riot_api_key}')
            if response.status_code == 200:
                ret.append(response.json())

        return response
