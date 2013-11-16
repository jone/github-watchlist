from watchlist.config import Config
from watchlist.config import add_config_argument_to_argparser
from watchlist.loader import CurrentSubscriptionsLoader
from watchlist.log import add_log_argument_to_argparse
from watchlist.log import setup_logging
from watchlist.strategy import UpdateStrategy
from watchlist.updater import SubscriptionsUpdater
from watchlist.utils import confirmation_prompt
import argparse
import os
import sys


class UpdateCommand(object):

    def __init__(self, config):
        self.config = config

    def __call__(self, confirmed=False):
        data = CurrentSubscriptionsLoader(self.config).load_current_subscriptions()
        data = UpdateStrategy(self.config).apply_watchlist(data)

        if not confirmed:
            self.report_changes_to_make(data)
            self.confirm_subscription_changes()

        SubscriptionsUpdater(self.config).update(data)

    def report_changes_to_make(self, data):
        print 'NO SUBSCRIPTION CHANGES:'

        for repo in data['keep-not-watching']:
            print ' - keep not watching:', repo

        for repo in data['keep-watching']:
            print ' - keep watching:', repo

        print ''
        print 'SUBSCRIPTION CHANGES:'

        for repo in data['watch']:
            print ' - add subscription:', repo

        for repo in data['unwatch']:
            print ' - remove subscription:', repo

        print ''
        print 'SUMMARY:'
        print ' - Keep watching:', len(data['keep-watching'])
        print ' - Keep not watching:', len(data['keep-not-watching'])
        print ' - Start watching:', len(data['watch'])
        print ' - Stop watching:', len(data['unwatch'])

    def confirm_subscription_changes(self):
        print ''
        if not confirmation_prompt('Continue updating subscriptions?'):
            print 'Aborted.'
            sys.exit(1)
        return True


def update_command():
    parser = argparse.ArgumentParser(description='Setup github watchlist.')
    add_config_argument_to_argparser(parser)
    add_log_argument_to_argparse(parser)

    parser.add_argument(
        '-C', '--confirmed', action='store_true',
        dest='confirmed',
        help='Update the subscriptions without user confirmation.'
        ' This is useful when running as cronjob.')

    parser.add_argument(
        '-D', '--debug', action='store_true',
        dest='debug',
        help='Start post mortem debugger on python exceptions.')

    parser.add_argument(
        '-v', '--verbose', action='store_true',
        dest='verbose',
        help='Print more verbose informations about whats happening.')

    args = parser.parse_args()
    if args.debug:
        sys.excepthook = post_mortem_debugging_hook
    if args.verbose:
        os.environ['VERBOSE'] = '1'
    setup_logging(args)

    config = Config()
    config.load(args.configfile)

    UpdateCommand(config)(confirmed=args.confirmed)


def post_mortem_debugging_hook(type, value, tb):
    if hasattr(sys, 'ps1') or not sys.stderr.isatty():
        # we are in interactive mode or we don't have a tty-like
        # device, so we call the default hook
        sys.__excepthook__(type, value, tb)
    else:
        import traceback, pdb
        # we are NOT in interactive mode, print the exception...
        traceback.print_exception(type, value, tb)
        print
        # ...then start the debugger in post-mortem mode.
        pdb.pm()
