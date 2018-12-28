import logging
import os

from . import spyder
from . import db
from . import util
from urllib.parse import urlparse
from multiprocessing import Pool, Queue, Lock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

##TODO: url blacklist
    # FACEBOOK >:(

logger = logging.getLogger(__name__)


class SpyderManager:

    def __init__(self, db, unlocked=False):
        self._db = db
        self._unlocked = unlocked
        self.queue = Queue()
        self._links = []
        self._links_lock = Lock()

    def run(self, root_site=None, crawlers=5):
        engine = create_engine(self._db)
        db.BASETABLE.metadata.create_all(engine)

        if not root_site:
            root_site = input('Address: ').strip()
        self.queue.put(root_site)
        self._links.append(root_site)

        pool = Pool(crawlers, self._spawn_crawlers)
        while True:
            pass

    ##TODO: how to stop?
    def _spawn_crawlers(self):
        util.config_root_logger()
        logger = logging.getLogger(__name__)
        logger.info('Spawned process: %s' % os.getpid())
        engine = create_engine(self._db)
        SpyderSession = sessionmaker()
        SpyderSession.configure(bind=engine)

        while True:
            session = SpyderSession()
            url = self.queue.get()
            try:
                s = spyder.Spyder(url, session, locked=not self._unlocked)
                page = s.crawl()
                if page:
                    session.commit()
                    logger.info('Saved page: %s' % page)
                    with self._links_lock:
                        links = [link for link in page.links if link not in self._links]
                        # if not self._unlocked:
                        #     links = list(filter(lambda x: urlparse(x).netloc == urlparse(page.url).netloc, links))
                        self._links = self._links + links
                        for link in links:
                            self.queue.put(link)
            except Exception as e:
                logger.exception(e)
                session.rollback()
            finally:
                session.close()


def main():
    args = util.init_args()
    SpyderManager(args.db, unlocked=args.unlock).run(root_site=args.s, crawlers=args.crawlers)

if __name__ == '__main__':
    main()