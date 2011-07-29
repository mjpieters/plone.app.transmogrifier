from zope.interface import classProvides, implements
from zope.annotation.interfaces import IAnnotations

from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.utils import Matcher
from collective.transmogrifier.utils import defaultKeys

from Products.CMFCore.utils import getToolByName

VERSIONABLE_KEY = 'plone.app.transmogrifier.versioning:versionable'


class BaseVersioningSection(object):
    implements(ISection)
    
    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.repository = getToolByName(transmogrifier.context,
                                        'portal_repository')
        self.anno = IAnnotations(transmogrifier)
        self.save()

    def save(self):
        versionable = self.repository._versionable_content_types
        self.anno[VERSIONABLE_KEY] = tuple(versionable)

    def restore(self):
        versionable = self.repository._versionable_content_types
        versionable[:] = ()
        versionable.extend(self.anno[VERSIONABLE_KEY])

    def clear(self):
        versionable = self.repository._versionable_content_types
        versionable[:] = ()


class DisableVersioningSection(BaseVersioningSection):
    classProvides(ISectionBlueprint)
    
    def __iter__(self):
        for item in self.previous:
            # http://stackoverflow.com/questions/2339358/workaround-for-python-2-4s-yield-not-allowed-in-try-block-with-finally-clause
            #try:
            #    self.save()
            #    self.clear()
            #    yield item
            #finally:
            #    self.restore()

            # XXX I'm not entirely sure if the code below does the same thing as the code above. [aclark]
            try:
                self.save()
                self.clear()
                yield item
            except:
                self.restore()
            self.restore()

class EnableVersioningSection(BaseVersioningSection):
    classProvides(ISectionBlueprint)
    
    def __iter__(self):
        for item in self.previous:
            self.restore()
            yield item
