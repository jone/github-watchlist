import json


def authorization_token_data(token):
    return {
        "id": 123123123,
        "url": "https://api.github.com/authorizations/123123123",
        "app": {
            "name": "github-watchlist (API)",
            "url": "http://developer.github.com/v3/oauth/#oauth-authorizations-api",
            "client_id": "xx123123xx"
            },
        "token": token,
        "note": "github-watchlist",
        "note_url": None,
        "created_at": "2013-05-11T11:39:44Z",
        "updated_at": "2013-05-11T11:39:44Z",
        "scopes": [
            "notifications",
            "repo"
            ]
        }

def repositories(repositories):
    result = []
    for full_name in repositories:
        result.append(repository(full_name))
    return json.dumps(result)


def repository(full_name):
    login, name = full_name.split('/')
    return {'name': name,
            'full_name': full_name,
            'owner': {'login': login,}}


def organisations(organisations):
    result = []
    for name in organisations:
        result.append({"login": name})
    return json.dumps(result)


def subscription(reponame):
    return json.dumps({
            "subscribed": True,
            "ignored": False,
            "reason": None,
            "created_at": "2013-05-12T11:25:02Z",
            })
