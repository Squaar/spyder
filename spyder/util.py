import logging
import argparse

def config_root_logger():
    logger = logging.getLogger('spyder')
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter('%(asctime)s (%(process)s) %(levelname)s %(name)s %(message)s'))
    logger.addHandler(sh)
    return logger

def init_args():
    parser = argparse.ArgumentParser(description='Basic python webcrawler')
    parser.add_argument('-db', type=str, help='Database connection string. "dialect[+driver]://user:password@host/dbname[?key=value..]"')
    parser.add_argument('--echo', action='store_true', help='Enable to echo DB queries.')
    parser.add_argument('-s', type=str, help='Crawl and record a single site.')
    parser.add_argument('--unlock', action='store_true', help='Enable to allow the crawler to scan sites outside of the current site\'s domain.')
    parser.add_argument('--crawlers', type=int, default=5, help='Number of crawler processes to use.')
    return parser.parse_args()