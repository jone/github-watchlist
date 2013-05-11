import json
import requests


class OAuthTokenCreator(object):

    def create_token(self, username, password):
        request_data = {'scopes': ['notifications'],
                'note': 'github-watchlist'}

        response = requests.post('https://api.github.com/authorizations',
                                 auth=(username, password),
                                 data=json.dumps(request_data))

        response.raise_for_status()
        response_data = json.loads(response.text)
        return response_data.get('token')
