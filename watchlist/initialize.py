from datetime import datetime
from requests import HTTPError
from watchlist.config import add_config_argument_to_argparser
import argparse
import getpass
import json
import os.path
import re
import requests


class OAuthTokenCreator(object):

    def create_token(self, username, password):
        request_data = {'scopes': ['notifications'],
                'note': 'github-watchlist'}

        response = requests.post('https://api.github.com/authorizations',
                                 auth=(username, password),
                                 data=json.dumps(request_data))

        if response.status_code == 422:
            # It seems that there is already a token with the same note.
            # For not breaking anything we just add a new token with
            # the timestamp in the note.
            request_data['note'] += ' ' + datetime.now().isoformat()
            response = requests.post('https://api.github.com/authorizations',
                                     auth=(username, password),
                                     data=json.dumps(request_data))

        response.raise_for_status()
        response_data = json.loads(response.text)
        return response_data.get('token')


class InitializeWatchlistConfiguration(object):

    def __call__(self, path):
        self.print_welcome_message(path)
        login = self.ask_for_github_login()

        while True:
            try:
                password = self.ask_for_github_password()

                if not password:
                    token = self.ask_for_oauth_token(login)
                else:
                    token = OAuthTokenCreator().create_token(login, password)

            except HTTPError, exc:
                print str(exc)
                print ''

            else:
                break

        self.generate_config_file(path, login, token)

    def print_welcome_message(self, path):
        print '\n'.join((
                'Welcome to github-watchlist!',
                '',
                'This wizard sets up a watchlist configuration which saved to:',
                '  %s' %path,
                '',
                'For running the watchlist a GitHub OAuth token is required.',
                'See: http://developer.github.com/v3/oauth/',
                'The token only uses the scope "notifications" for managing '
                'your subscriptions.',
                '',
                ''))

    def ask_for_github_login(self):
        validation = re.compile('^[A-Za-z0-9.][A-Za-z0-9.-]*$')

        while True:
            login = raw_input('Your GitHub username: ').strip()
            if validation.match(login):
                print ''
                return login

            else:
                print 'Invalid: Username may only contain alphanumeric characters' \
                    ' or dashes and cannot begin with a dash'

    def ask_for_github_password(self):
        print '\n'.join((
                'In order to automatically create a GitHub OAuth token for later use',
                'we must ask you once for your github password.',
                'Your password is not stored and only used for creating an OAuth',
                'token, granting access to the "notifications" scope to this script.',
                '',
                'If you whish to create the token by yourself, you will be asked',
                'for the token if you do not enter a password and just hit enter.',
                ''))

        return getpass.getpass('Your GitHub password: ')

    def ask_for_oauth_token(self, login):
        print '\n'.join((
                'Since you did not enter a password I assume you want to generate'
                'the OAuth token yourself',
                '',
                'You can easily create a token using curl:',
                '  curl -i -u %s -d \'{"scopes": ["notifications"], ' % login + \
                    '"note": "github-watchlist"}\' ' + \
                    'https://api.github.com/authorizations',
                '',
                ))

        return raw_input('GitHub OAuth token: ')

    def generate_config_file(self, path, login, token):
        if os.path.exists(path):
            print 'There is already a file at %s' % path
            print 'Should the file be replaced?'
            raw_input('Confirm replacing file with ENTER or abort with Ctrl-C: ')

        with open(path, 'w+') as file_:
            file_.write('\n'.join((
                        '[watchlist]',
                        'github-login = %s' % login,
                        'github-oauth-token = %s' % token,
                        '',
                        '# Example watchlist:',
                        '# watchlist =',
                        '#     not-watching:  mylogin/idontcare',
                        '#     watching:      mylogin/.*',
                        '',
                        'watchlist =',
                        ''
                        )))

        print ''
        print 'The config file was generated to: %s' % path
        print 'Next you should edit the config file and configure your watchlist.'
        print 'When finished, run bin/update-watchlist'


def initialize_command():
    parser = argparse.ArgumentParser(description='Setup github watchlist.')
    add_config_argument_to_argparser(parser)
    args = parser.parse_args()

    initializer = InitializeWatchlistConfiguration()
    initializer(args.configfile)
