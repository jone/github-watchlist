from watchlist import github
import json
import logging


class SubscriptionsUpdater(object):

    def __init__(self, config):
        self.config = config

    def update(self, data):
        self.create_subscriptions(data['watch'])
        self.delete_subscriptions(data['unwatch'])

    def create_subscriptions(self, repositories):
        watch_payload = json.dumps({'subscribed': True, 'ignored': False})

        for reponame in repositories:
            logging.info('create subscription: %s' % reponame)
            github.put('repos/%s/subscription' % reponame, self.config,
                       payload=watch_payload)

    def delete_subscriptions(self, repositories):
        for reponame in repositories:
            logging.info('delete subscription: %s' % reponame)
            github.delete('repos/%s/subscription' % reponame, self.config)
