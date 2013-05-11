==================
 github-watchlist
==================

**Manage your watched GitHub repositories per script**


When participanting in large organisations on GitHub and watching all
repositories it's getting noisy. Although the watched repositories are
`configureable <https://GitHub.com/watching>`_ it is time consuming to
configure hundreds of repositories.

The `github-watchlist` script lets you configure your watched
repositories with patterns. It can easily be set up as a cronjob once
you have figured out a good configuration.


.. contents:: Table of Contents


Quick Start
===========

Install with `zc.buildout <http://pypi.python.org/pypi/zc.buildout>`_:

.. code:: bash

    $ git clone git://GitHub.com/jone/github-watchlist
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

Run the `bin/update-watchlist` script:

.. code:: bash

    $ bin/update-watchlist
    XXXXXXXXXXXXXXXXXXXXXXX


Configuring the watchlist
=========================

The `watchlist` in the `config.ini` is processed from top-down. Each
line has subscription type (`watching`, `not-watching` or `ignoring`),
followed by colon, followed by a regular expression matching one or
many repository names (`principal/repository-name`).


**Subscription types:**

`watching`
    You receive notifications for all discussions in this repository.

`not-watching`
    You only receive notifications for discussions in which you
    participate or are @mentioned.

`ignoring`
    You do not receive any notifications for discussions in this
    repository.


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

- All repositories watched by you
- All your repositories
- All repositories of organisations you participate in


Command line options
====================

The `bin/update-watchlist` script can be run in interactive-mode as
well as in batch-mode, useful for running it with a cronjob.



License
=======

"THE BEER-WARE LICENSE" (Revision 42):

`jone <https://github.com/jone>`_ wrote this script. As long as you
retain this notice you can do whatever you want with this stuff. If we
meet some day, and you think this stuff is worth it, you can buy me a
beer in return.
