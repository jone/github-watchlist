from watchlist import github
import json


class SubscriptionsUpdater(object):

    def __init__(self, config):
        self.config = config

    def update(self, data):
        self.create_subscriptions(data['watch'])
        self.delete_subscriptions(data['unwatch'])

    def create_subscriptions(self, repositories):
        watch_payload = json.dumps({'subscribed': True, 'ignored': False})

        for reponame in repositories:
            github.put('%s/subscription' % reponame, self.config,
                       payload=watch_payload)

    def delete_subscriptions(self, repositories):
        for reponame in repositories:
            github.delete('%s/subscription' % reponame, self.config)
