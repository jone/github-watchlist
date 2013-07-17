import logging


def add_log_argument_to_argparse(argparser):
    argparser.add_argument('-l', '--log', dest='logfile', default=None,
                           help='Write changed subscriptions into a logfile.')


def setup_logging(args):
    disable_requests_logging()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

    if args.logfile:
        handler = logging.FileHandler(args.logfile, mode='a+')
        formatter = logging.Formatter('%(asctime)-15s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logging.root.addHandler(handler)


def disable_requests_logging():
    """Disables logging "INFO Starting new HTTPS connection (1): api.github.com"
    by requests' urllib3 package.
    """
    from requests.packages.urllib3 import connectionpool
    connectionpool.log.setLevel(logging.WARNING)
