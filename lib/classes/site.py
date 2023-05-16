from search import Base
from classes.collection import Collection
from sqlalchemy import Column, Integer, String, ForeignKey

VALID_SITE_EXTENSIONS = (".gov", ".edu", ".com", ".net", ".mil", ".org")

class Site(Base):

    __tablename__ = "sites"

    sid = Column("sid", Integer, primary_key = True)
    url = Column("url", String)
    cid = Column(Integer, ForeignKey("collections.cid"))
    collection = Column("collection", Collection)

    def __init__(self, url, cid, collection):
        self.url = url
        self.cid = cid
        self.collection = collection

        collection.url_list.append(self)

    @property
    def get_url(self):
        return self._url

    @get_url.setter
    def set_url(self, new_url):
        if type(new_url) is str and new_url[-4:] in VALID_SITE_EXTENSIONS and " " not in new_url:
            self._url = new_url
        else:
            raise Exception("URL must be a string that ends in a valid website extension.")
