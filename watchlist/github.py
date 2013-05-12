import json
import requests


GITHUB_API = 'https://api.github.com/'


def get(path, config):
    url = make_github_url(path, config)
    response = requests.get(url)
    response.raise_for_status()
    return json.loads(response.text)


def make_github_url(path, config):
    url = GITHUB_API + path.lstrip('/')
    if '?' in url:
        url += '&access_token=%s' % config.github_oauth_token
    else:
        url += '?access_token=%s' % config.github_oauth_token
    return url
