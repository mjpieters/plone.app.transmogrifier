from zope.interface import classProvides, implements

from collective.transmogrifier.interfaces import ISection, ISectionBlueprint
from collective.transmogrifier.utils import Matcher
from collective.transmogrifier.utils import Expression
from plone.i18n.normalizer import urlnormalizer as normalizer


class URLNormalizerSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.locale = Expression(options.get('locale', 'python:None'), 
                                transmogrifier, name, options)
        self.destinationkey = Expression(options.get('destination-key', 'string:_id'), 
                                        transmogrifier, name, options)
                
        self.sourcekey = Matcher(options.get('source-key', 'title'))

    def __iter__(self):
        for item in self.previous:
            sourcekey = self.sourcekey(*item.keys())[0]
            if not sourcekey:   # not enough info to return a sensible id key
                yield item; continue
            
            # Get the information we require for normalization
            keywords = dict(text=item[sourcekey], locale=self.locale(item))
            # Perform Normalization
            source_norm = normalizer.normalize(**keywords)
            item[self.destinationkey(item)] = source_norm
            
            yield item