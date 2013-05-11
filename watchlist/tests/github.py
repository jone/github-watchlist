
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
            "notifications"
            ]
        }
