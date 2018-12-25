import requests
import logging
import datetime

from . import db
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse


logger = logging.getLogger(__name__)

class Spyder:

    _request_headers = {
        'User-Agent': 'python3-spyder'
    }

    def __init__(self, addr, db_session):
        self._addr = addr
        self._session = db_session

    def crawl(self):
        try:
            self._resp = requests.get(self._addr, headers=self._request_headers, stream=True)
            ip, port = self._resp.raw._connection.sock.getpeername()
            logger.info('(%s:%s) %s: %s' % (ip, port, self._addr, self._resp.status_code))
            if self._resp.status_code < 200 or self._resp.status_code > 299:
                logger.warning('Ignoring HTTP %s response.' % self._resp.status_code)
                return None

            self._soup = BeautifulSoup(self._resp.content, 'html.parser')
            links = list(set(map(lambda x: self._try_parse_link(x, self._addr), self._soup.find_all('a'))))
            if None in links:
                links.remove(None)

            # TODO: record links in db
                # track multiples of the same link?
            page = db.Page(url=self._addr, content=self._resp.text, links=links, updated=datetime.datetime.utcnow())
            page = self._session.merge(page)
            return page

        except requests.exceptions.MissingSchema as e:
            logger.warning('Ignoring invalid URL: %s' % self._addr)
            return None

    @staticmethod
    def _try_parse_link(a_tag, parent_addr):
        try:
            addr = a_tag.attrs['href']
            parsed = urlparse(addr)
            if not parsed.scheme or not parsed.netloc:
                parsed_parent = urlparse(parent_addr)
                return urlunparse([parsed_parent.scheme, parsed_parent.netloc] + list(parsed[2:]))
            return addr
        except KeyError as e:
            logger.warning('Ignoring <a> tag with no href: %s' % a_tag)
            return None
