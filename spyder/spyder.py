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

    def __init__(self, addr, db_session, locked=True):
        self._addr = addr
        self._session = db_session
        self._locked = locked

    def crawl(self):
        try:
            self._resp = requests.get(self._addr, headers=self._request_headers, stream=True)
            ip, port = self._resp.raw._connection.sock.getpeername()
            logger.info('(%s:%s) %s: %s' % (ip, port, self._addr, self._resp.status_code))
            if self._resp.status_code < 200 or self._resp.status_code > 299:
                logger.warning('Ignoring HTTP %s response: %s' % (self._resp.status_code, self._addr))
                return None
            ##TODO: check if non-HTML

            self._soup = BeautifulSoup(self._resp.content, 'html.parser')
            links = list(set(map(lambda x: self._try_parse_link(x, self._addr), self._soup.find_all('a'))))
            links = self._filter_links(links)

            # TODO: track multiples of the same link?
            page = db.Page(url=self._addr, content=self._resp.text, links=links, updated=datetime.datetime.utcnow())
            page = self._session.merge(page)
            return page

        except requests.exceptions.MissingSchema as e:
            logger.warning('Ignoring invalid URL: %s' % self._addr)
            return None
        except requests.exceptions.ConnectionError as e:
            if '[Errno 11004] getaddrinfo failed' in str(e):
                logger.warning('Ignoring failed DNS query: %s' % self._addr)
                return None
            raise

    ##TODO: filter non-HTML
    def _filter_links(self, links):
        if None in links:
            links.remove(None)
        if self._locked:
            addr_netloc = urlparse(self._addr).netloc
            links = filter(lambda x: urlparse(x).netloc == addr_netloc, links)
        return list(links)

    @staticmethod
    def _try_parse_link(a_tag, parent_addr):
        try:
            addr = a_tag.attrs['href']
            parsed = urlparse(addr)
            if not parsed.scheme or not parsed.netloc:
                parsed_parent = urlparse(parent_addr)
                addr = urlunparse([parsed_parent.scheme, parsed_parent.netloc] + list(parsed[2:]))
            addr = addr.replace('../', '/')
            addr = addr.replace('./', '/') ##TODO: replace these with regex
            addr = addr.replace('//', '/')
            addr = addr.replace(':/', '://')
            return addr
        except KeyError as e:
            logger.debug('Ignoring <a> tag with no href: %s' % a_tag)
            return None
