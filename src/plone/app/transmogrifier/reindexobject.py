from zope.interface import classProvides, implements

try:
    from Products.CMFCore.CMFCatalogAware import CatalogAware # Plone 4
except ImportError:
    from Products.CMFCore.CMFCatalogAware import CMFCatalogAware as CatalogAware

from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.utils import defaultMatcher

import logging
logger = logging.getLogger('plone.app.transmogrifier.reindexobject')

class ReindexObjectSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.portal_catalog = transmogrifier.context.portal_catalog
        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.verbose = options.get('verbose', '0').lower()  in (
                            '1', 'true', 'yes', 'on')
        self.counter = 0

    def __iter__(self):

        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            if not pathkey: # not enough info
                yield item; continue
            path = item[pathkey]

            ob = self.context.unrestrictedTraverse(str(path).lstrip('/'), None)
            if ob is None:
                yield item; continue # object not found

            if not isinstance(ob, CatalogAware):
                yield item; continue # can't notify portal_catalog

            if self.verbose: # add a log to display reindexation progess
                self.counter += 1
                logger.info("Reindex object %s (%s)", path, self.counter)

            self.portal_catalog.reindexObject(ob) # update catalog

            yield item

