import json
import requests


GITHUB_API = 'https://api.github.com/'


def get(path, config):
    url = make_github_url(path, config)
    response = requests.get(url)
    response.raise_for_status()
    return json.loads(response.text)


def put(path, config, payload):
    url = make_github_url(path, config)
    response = requests.put(url, data=payload)
    response.raise_for_status()
    return json.loads(response.text)


def delete(path, config):
    url = make_github_url(path, config)
    response = requests.delete(url)
    response.raise_for_status()
    return response


def make_github_url(path, config):
    url = GITHUB_API + path.lstrip('/')
    if '?' in url:
        url += '&access_token=%s' % config.github_oauth_token
    else:
        url += '?access_token=%s' % config.github_oauth_token
    return url
