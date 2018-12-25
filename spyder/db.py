from sqlalchemy import Column, String, JSON, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

BASETABLE = declarative_base()

class Page(BASETABLE):
    __tablename__ = 'pages'

    url = Column(String, primary_key=True)
    content = Column(String)
    links = Column(JSON)
    updated = Column(TIMESTAMP)

    def __repr__(self):
        return '<Page(url=%s)>' % self.url