import ConfigParser
import os.path
import re


class ConfigurationError(Exception):
    pass


class Config(object):

    def load(self, path):
        config = self.read_config_file(path)
        self.validate_config(config)
        self.apply_config(config)

    def read_config_file(self, path):
        config = ConfigParser.ConfigParser()

        with open(path) as configfile:
            try:
                config.readfp(configfile)
            except ConfigParser.Error, exc:
                raise ConfigurationError('%s: %s' % (type(exc).__name__, str(exc)))

        return config

    def validate_config(self, config):
        sections = config.sections()
        if sections != ['watchlist']:
            raise ConfigurationError(
                'The config file should have exactly one section called "watchlist",'
                ' got: %s' % (sections and ', '.join(sorted(config.sections()))
                              or 'none'))

        required_options = ('github-login', 'github-oauth-token', 'watchlist')
        missing_options = set(required_options) - set(config.options('watchlist'))
        if len(missing_options) > 0:
            raise ConfigurationError('Missing configuration options: %s' % (
                    ', '.join(sorted(missing_options))))

        empty_options = [name for name in ('github-login', 'github-oauth-token')
                         if not config.get('watchlist', name)]
        if len(empty_options) > 0:
            raise ConfigurationError('Values required for the options %s.' % (
                    ' and '.join(empty_options)))

        unexpected_options = set(config.options('watchlist')) - set(required_options)
        if len(unexpected_options) > 0:
            raise ConfigurationError(
                'Unexpected configuration options: %s.' % (
                    ', '.join(sorted(unexpected_options))) +
                ' Is the watchlist not properly indented?')

    def apply_config(self, config):
        self.github_login = config.get('watchlist', 'github-login')
        self.github_oauth_token = config.get('watchlist', 'github-oauth-token')

        self.watchlist = []
        watchlist_value = config.get('watchlist', 'watchlist')
        if watchlist_value.strip():
            watchlist_items = map(str.strip, watchlist_value.strip().split('\n'))
        else:
            watchlist_items = []

        item_xpr = re.compile('^(watching|not-watching): *(\S*)$')
        for line in watchlist_items:
            match = item_xpr.match(line)
            if not match:
                raise ConfigurationError('Unexpected format of watchlist item: %s' % (
                        line))
            self.watchlist.append(match.groups())


def add_config_argument_to_argparser(argparser):
    default_config_file_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'config.ini'))

    argparser.add_argument(
        '-c', '--configfile', dest='configfile',
        help='Path to the config file (Default: %s)' % default_config_file_path,
        default=default_config_file_path)
