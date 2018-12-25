import argparse
import logging

from . import spyder
from . import db
from urllib.parse import urlparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


logger = logging.getLogger(__name__)

##TODO: arg to lock to same domain
##TODO: url blacklist
    # FACEBOOK


def main():
    parser = argparse.ArgumentParser(description='Basic python webcrawler')
    parser.add_argument('-db', type=str, help='Database connection string. "dialect[+driver]://user:password@host/dbname[?key=value..]"')
    parser.add_argument('--echo', action='store_true', help='Enable to echo DB queries.')
    parser.add_argument('-s', type=str, help='Crawl and record a single site.')
    parser.add_argument('--unlock', action='store_true', help='Enable to allow the crawler to scan sites outside of the current site\'s domain.')
    args = parser.parse_args()

    engine = create_engine(args.db, echo=args.echo)
    SpyderSession = sessionmaker()
    SpyderSession.configure(bind=engine)
    db.BASETABLE.metadata.create_all(engine)

    if not args.s:
        args.s = input('Address: ').strip()

    queue = [args.s]
    crawled = []

    while queue:
        session = SpyderSession()
        url = queue.pop()
        try:
            s = spyder.Spyder(url, session)
            page = s.crawl()
            if page:
                session.commit()
                links = [link for link in page.links if link not in crawled+queue+[url]]
                if not args.unlock:
                    links = filter(lambda x: urlparse(x).netloc == urlparse(page.url).netloc, links)
                queue += links
        except Exception as e:
            logging.exception(e)
            session.rollback()
        finally:
            crawled.append(url)
            session.close()


if __name__ == '__main__':
    main()