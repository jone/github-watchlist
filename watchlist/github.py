import json
import re
import requests


GITHUB_API = 'https://api.github.com/'


def get(path, config):
    url = make_github_url(path, config)
    return _get_follow_pagingation(url, config)


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


def _get_follow_pagingation(url, config):
    response = requests.get(url)
    response.raise_for_status()
    data = json.loads(response.text)

    links = _extract_link_header(response)
    if links.get('next'):
        next_url = add_access_token_to_url(links.get('next'), config)
        data.extend(_get_follow_pagingation(next_url, config))

    return data


def _extract_link_header(response):
    links = response.headers.get('link', None)
    if not links:
        return {}

    links = map(str.strip, links.split(','))
    xpr = re.compile('<([^>]*)>; *rel="([^"]*)"')

    result = {}
    for link in links:
        match = xpr.match(link)
        result[match.groups()[1]] = match.groups()[0]

    return result


def make_github_url(path, config):
    url = GITHUB_API + path.lstrip('/')
    return add_access_token_to_url(url, config)


def add_access_token_to_url(url, config):
    if 'access_token=' in url:
        return url
    if '?' in url:
        url += '&access_token=%s' % config.github_oauth_token
    else:
        url += '?access_token=%s' % config.github_oauth_token
    return url
