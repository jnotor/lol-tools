import re
import requests

class RiotClient:
    _base_url = 'https://americas.api.riotgames.com/'

    def  __init__(self, riot_api_key: str, summoner_name: str, tagline: str) -> None:
        ''' Constructor

        @param summoner_name: in game name
        @param tagline: in game #
        '''
        self.riot_api_key = riot_api_key
        self.puuid = self._set_player_puuid(summoner_name, tagline)

    def _process_game(self, game: dict, target_key_pattern: str = '') -> dict:
        ''' Method parses an individual game for the init'd player's specific data
        filtering for keys matching target_key_pattern

        @param game: game data
        @param target_key_pattern: optional regex key pattern to match

        :return ret: filtered player participant data
        '''
        # iterate over the participants until we find the init'd player's puuid.
        # we can assume its there since we got the game using their puuid
        target_player = [p for p in game if p['puuid'] == self.puuid][0]

        ret = {}

        for key, value in target_player.items():
            tkp = re.search(target_key_pattern, key)

            if target_key_pattern and tkp is not None:
                ret[key] = value

        return ret

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

    def get_players_recent_games_data(self, game_type: str = '', target_key_pattern: str = '') -> dict:
        ''' Method gets recent games for the initialized player

        @param game_type: for optional filtering of games
        @param target_key_pattern: optional filtering of game data based on regex pattern of keys
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
            if response.status_code != 200:
                continue

            game = response.json().get('info', {})

            if game_type and game['gameType'] != game_type:
                continue

            processed_game = self._process_game(
                game=game.get('participants', []),
                target_key_pattern=f'{target_key_pattern}'
            )

            ret.append(processed_game)

        return ret
