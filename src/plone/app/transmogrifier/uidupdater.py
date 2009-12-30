from zope.interface import classProvides, implements

from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.utils import Matcher
from collective.transmogrifier.utils import defaultKeys

from Products.Archetypes.interfaces import IReferenceable
from Products.Archetypes.config import UUID_ATTR

class UIDUpdaterSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)
    
    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        
        if 'path-key' in options:
            pathkeys = options['path-key'].splitlines()
        else:
            pathkeys = defaultKeys(options['blueprint'], name, 'path')
        self.pathkey = Matcher(*pathkeys)
        
        if 'uid-key' in options:
            uidkeys = options['uid-key'].splitlines()
        else:
            uidkeys = defaultKeys(options['blueprint'], name, 'uid')
        self.uidkey = Matcher(*uidkeys)
            
        
    def __iter__(self):
        
        for item in self.previous:
            
            pathkey = self.pathkey(*item.keys())[0]
            uidkey = self.uidkey(*item.keys())[0]
            
            if not pathkey or not uidkey: # not enough info
                yield item; continue
            
            path = item[pathkey]
            uid = item[uidkey]
            
            obj = self.context.unrestrictedTraverse(path.lstrip('/'), None)
            if obj is None: # path doesn't exist
                yield item; continue
            
            if IReferenceable.providedBy(obj):
                oldUID = obj.UID()
                if oldUID != uid:                    
                    if not oldUID:
                        setattr(obj, UUID_ATTR, uid)
                    else:
                        obj._setUID(uid)
                
            yield item
