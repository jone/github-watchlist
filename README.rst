==================
 github-watchlist
==================

**Manage your watched GitHub repositories per script**


When participanting in large organisations on GitHub and watching all
repositories it's getting noisy. Although the watched repositories are
`configureable <https://github.com/watching>`_ it is time consuming to
configure hundreds of repositories.

The `github-watchlist` script lets you configure your watched
repositories with patterns. It can easily be set up as a cronjob once
you have figured out a good configuration.

.. image:: https://travis-ci.org/jone/github-watchlist.png?branch=master
   :target: https://travis-ci.org/jone/github-watchlist

.. contents:: Table of Contents


Quick Start
===========

Install with `zc.buildout <http://pypi.python.org/pypi/zc.buildout>`_:

.. code:: bash

    $ git clone git://github.com/jone/github-watchlist
    $ cd github-watchlist
    $ python bootstrap.py
    $ bin/buildout

Use `bin/initialize` to automatically create and configure a `GitHub
OAuth <http://developer.github.com/v3/oauth/>`_ token:

.. code:: bash

    $ bin/initialize

`bin/initialize` creates a `config.ini` file, containing your login /
oAuth token and your watch configuration. Edit the `config.ini` to
configure which repositories to watch.

Example `config.ini`:

.. code:: ini

    [watchlist]
    github-login = jone
    github-oauth-token = 51dc30ddc473d43a6011e9ebba6ca770

    watchlist =
        watching:      collective/collective.dexteritytextindexer
        not-watching:  collective/.*
        watching:      jone/.*

Then run the `bin/update-watchlist` script.


Configuring the watchlist
=========================

The `watchlist` in the `config.ini` is processed from top-down. Each
line has subscription type (`watching` or `not-watching`),
followed by colon, followed by a regular expression matching one or
many repository names (`principal/repository-name`).


**Subscription types:**

`watching`
    You receive notifications for all discussions in this repository.

`not-watching`
    You only receive notifications for discussions in which you
    participate or are @mentioned.


**Matching repositories with regular expressions**

See the python `Regular expressions documentation
<http://docs.python.org/2/library/re.html>`_ for details about the
regular expression matching.


**Processing the watchlist**

The watchlist is processed top-down. Once a repository is matched it
will not be matched by a later expression. Therefore the specific
expressions (such as an explicit repository name) should be at the top
while more generic expressions (such as `collective/.*`) should be at
the bottom.


**Witch repositories are processed?**

All your repositories and all repositories of organisations you
participate in are manageable with this script.

Repositories where you do not participate are not manageable with this
script, the subscription for those repositories is not changed.


Watchlist updater
=================

The `bin/update-watchlist` script gives applies your configuration to
your repositories and your current watches and shows a summary of
changes you need to confirm:

.. code:: bash

    $ ./bin/update-watchlist --help
    usage: update-watchlist [-h] [-c CONFIGFILE] [-l LOGFILE] [-C]

    Setup github watchlist.

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIGFILE, --configfile CONFIGFILE
                            Path to the config file (Default:
                            /Users/jone/projects/packages/github-
                            watchlist/config.ini)
      -l LOGFILE, --log LOGFILE
                            Write changed subscriptions into a logfile.
      -C, --confirmed       Update the subscriptions without user confirmation.
                            This is useful when running as cronjob.


.. code:: bash

    $ ./bin/update-watchlist
    NO SUBSCRIPTION CHANGES:
     - keep not watching: collective/ArchGenXML
     - keep watching: jone/github-watchlist

    SUBSCRIPTION CHANGES:
     - add subscription: 4teamwork/ftw.lawgiver
     - remove subscription: collective/collective.dancing

    SUMMARY:
     - Keep watching: 1
     - Keep not watching: 1
     - Start watching: 1
     - Stop watching: 1

    Continue updating subscriptions? [Yes/No]: yes
    INFO create subscription: 4teamwork/ftw.lawgiver
    INFO delete subscription: plone/collective.dancing

Using the `--confirmed` option you can disable the confirmation prompt
so that it can be hooked up with a cronjob.


License
=======

"THE BEER-WARE LICENSE" (Revision 42):

`jone <https://github.com/jone>`_ wrote this script. As long as you
retain this notice you can do whatever you want with this stuff. If we
meet some day, and you think this stuff is worth it, you can buy me a
beer in return.


.. image:: https://cruel-carlota.pagodabox.com/d1d1c2459158d8c198c361c5b8ea74bd
   :alt: githalytics.com
   :target: http://githalytics.com/jone/github-watchlist
