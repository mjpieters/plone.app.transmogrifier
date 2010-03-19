import unittest
from zope.component import provideUtility
from zope.interface import classProvides, implements
from zope.testing import doctest
from collective.transmogrifier.interfaces import ISectionBlueprint, ISection
from collective.transmogrifier.tests import tearDown
from collective.transmogrifier.sections.tests import sectionsSetUp
from collective.transmogrifier.sections.tests import SampleSource
from Products.Five import zcml

# Doctest support

ctSectionsSetup = sectionsSetUp
def sectionsSetUp(test):
    ctSectionsSetup(test)
    import plone.app.transmogrifier
    zcml.load_config('configure.zcml', plone.app.transmogrifier)

def portalTransformsSetUp(test):
    sectionsSetUp(test)

    class MockPortalTransforms(object):
        def __call__(self, transform, data):
            return 'Transformed %r using the %s transform' % (data, transform)
        def convertToData(self, target, data, mimetype=None):
            if mimetype is not None:
                return 'Transformed %r from %s to %s' % (
                    data, mimetype, target)
            else:
                return 'Transformed %r to %s' % (data, target)
    test.globs['plone'].portal_transforms = MockPortalTransforms()

def aTSchemaUpdaterSetUp(test):
    sectionsSetUp(test)

    from Products.Archetypes.interfaces import IBaseObject
    class MockPortal(object):
        implements(IBaseObject)

        _last_path = None
        def unrestrictedTraverse(self, path, default):
            if path[0] == '/':
                return default # path is absolute
            if isinstance(path, unicode):
                return default
            if path == 'not/existing/bar':
                return default
            if path.endswith('/notatcontent'):
                return object()
            self._last_path = path
            return self

        _last_field = None
        def getField(self, name):
            if name.startswith('field'):
                self._last_field = name
                return self

        def get(self, ob):
            if self._last_field.endswith('notchanged'):
                return 'nochange'
            if self._last_field.endswith('unicode'):
                return u'\xe5'.encode('utf8')

        updated = ()
        def set(self, ob, val):
            self.updated += ((self._last_path, self._last_field, val),)

        def checkCreationFlag(self):
            return len(self.updated) % 2

        def unmarkCreationFlag(self):
            pass

        def at_post_create_script(self):
            pass

        def at_post_edit_script(self):
            pass

    test.globs['plone'] = MockPortal()
    test.globs['transmogrifier'].context = test.globs['plone']

    class SchemaSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(SchemaSource, self).__init__(*args, **kw)
            self.sample = (
                dict(_path='/spam/eggs/foo', fieldone='one value',
                     fieldtwo=2, nosuchfield='ignored',
                     fieldnotchanged='nochange', fieldunicode=u'\xe5',),
                dict(_path='not/existing/bar', fieldone='one value',
                     title='Should not be updated, not an existing path'),
                dict(fieldone='one value',
                     title='Should not be updated, no path'),
                dict(_path='/spam/eggs/notatcontent', fieldtwo=2,
                     title='Should not be updated, not an AT base object'),
            )
    provideUtility(SchemaSource,
        name=u'plone.app.transmogrifier.tests.schemasource')

def workflowUpdaterSetUp(test):
    sectionsSetUp(test)

    from Products.CMFCore.WorkflowCore import WorkflowException

    class MockPortal(object):
        _last_path = None
        def unrestrictedTraverse(self, path, default):
            if path[0] == '/':
                return default # path is absolute
            if isinstance(path, unicode):
                return default
            if path == 'not/existing/bar':
                return default
            self._last_path = path
            return self

        @property
        def portal_workflow(self):
            return self

        updated = ()
        def doActionFor(self, ob, action):
            assert ob == self
            if action == 'nonsuch':
                raise WorkflowException('Test exception')
            self.updated += ((self._last_path, action),)

    test.globs['plone'] = MockPortal()
    test.globs['transmogrifier'].context = test.globs['plone']

    class WorkflowSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(WorkflowSource, self).__init__(*args, **kw)
            self.sample = (
                dict(_path='/spam/eggs/foo', _transitions='spam'),
                dict(_path='/spam/eggs/baz', _transitions=('spam', 'eggs')),
                dict(_path='not/existing/bar', _transitions=('spam', 'eggs'),
                     title='Should not be updated, not an existing path'),
                dict(_path='spam/eggs/incomplete',
                     title='Should not be updated, no transitions'),
                dict(_path='/spam/eggs/nosuchtransition',
                     _transitions=('nonsuch',),
                     title='Should not be updated, no such transition'),
            )
    provideUtility(WorkflowSource,
        name=u'plone.app.transmogrifier.tests.workflowsource')


def browserDefaultSetUp(test):
    sectionsSetUp(test)

    from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault
    class MockPortal(object):
        implements(ISelectableBrowserDefault)

        _last_path = None
        def unrestrictedTraverse(self, path, default):
            if path[0] == '/':
                return default # path is absolute
            if isinstance(path, unicode):
                return default
            if path == 'not/existing/bar':
                return default
            self._last_path = path
            return self

        updated = ()
        def setLayout(self, layout):
            self.updated += ((self._last_path, 'layout', layout),)

        def setDefaultPage(self, defaultpage):
            self.updated += ((self._last_path, 'defaultpage', defaultpage),)

    test.globs['plone'] = MockPortal()
    test.globs['transmogrifier'].context = test.globs['plone']

    class BrowserDefaultSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(BrowserDefaultSource, self).__init__(*args, **kw)
            self.sample = (
                dict(_path='/spam/eggs/foo', _layout='spam'),
                dict(_path='/spam/eggs/bar', _defaultpage='eggs'),
                dict(_path='/spam/eggs/baz', _layout='spam', _defaultpage='eggs'),
                dict(_path='not/existing/bar', _layout='spam',
                     title='Should not be updated, not an existing path'),
                dict(_path='spam/eggs/incomplete',
                     title='Should not be updated, no layout or defaultpage'),
                dict(_path='spam/eggs/emptylayout', _layout='',
                     title='Should not be updated, no layout or defaultpage'),
                dict(_path='spam/eggs/emptydefaultpage', _defaultpage='',
                     title='Should not be updated, no layout or defaultpage'),
            )
    provideUtility(BrowserDefaultSource,
        name=u'plone.app.transmogrifier.tests.browserdefaultsource')

def urlNormalizerSetUp(test):
    sectionsSetUp(test)

    from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault
    class MockPortal(object):
        implements(ISelectableBrowserDefault)

        _last_path = None
        def unrestrictedTraverse(self, path, default):
            if path[0] == '/':
                return default # path is absolute
            if isinstance(path, unicode):
                return default
            if path == 'not/existing/bar':
                return default
            self._last_path = path
            return self

        updated = ()

    test.globs['plone'] = MockPortal()
    test.globs['transmogrifier'].context = test.globs['plone']

    class URLNormalizerSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(URLNormalizerSource, self).__init__(*args, **kw)
            self.sample = (
                dict(title='mytitle'),
                dict(title='Is this a title of any sort?'),
                dict(title='Put some <br /> $1llY V4LUES -- here&there'),
                dict(title='What about \r\n line breaks (system)'),
                dict(title='Try one of these --------- oh'),
                dict(language='My language is de'),
                dict(language='my language is en')
            )
    provideUtility(URLNormalizerSource,
        name=u'plone.app.transmogrifier.tests.urlnormalizersource')

def criteriaSetUp(test):
    sectionsSetUp(test)

    from Products.ATContentTypes.interface import IATTopic
    class MockPortal(object):
        implements(IATTopic)

        _last_path = None
        def unrestrictedTraverse(self, path, default):
            if path[0] == '/':
                return default # path is absolute
            if isinstance(path, unicode):
                return default
            if path == 'not/existing/bar':
                return default
            self._last_path = path
            return self

        criteria = ()
        def addCriterion(self, field, criterion):
            self.criteria += ((self._last_path, field, criterion),)

    test.globs['plone'] = MockPortal()
    test.globs['transmogrifier'].context = test.globs['plone']

    class CriteriaSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(CriteriaSource, self).__init__(*args, **kw)
            self.sample = (
                dict(_path='/spam/eggs/foo', _criterion='bar', _field='baz'),
                dict(_path='not/existing/bar', _criterion='bar', _field='baz',
                     title='Should not be updated, not an existing path'),
                dict(_path='spam/eggs/incomplete',
                     title='Should not be updated, no criterion or field'),
            )
    provideUtility(CriteriaSource,
        name=u'plone.app.transmogrifier.tests.criteriasource')

def mimeencapsulatorSetUp(test):
    sectionsSetUp(test)

    class EncapsulatorSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(EncapsulatorSource, self).__init__(*args, **kw)
            self.sample = (
                dict(_data='foobarbaz', _mimetype='application/x-test-data'),
                dict(_mimetype='skip/nodata'),
                dict(portrait='skip, no mimetypeset'),
                dict(portrait='someportraitdata',
                     _portrait_mimetype='image/jpeg'),
            )
    provideUtility(EncapsulatorSource,
        name=u'plone.app.transmogrifier.tests.encapsulatorsource')

    from OFS.Image import File
    class OFSFilePrinter(object):
        """Prints out data on any OFS.Image.File object in the item"""
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, transmogrifier, name, options, previous):
            self.previous = previous

        def __iter__(self):
            for item in self.previous:
                for key, value in item.iteritems():
                    if isinstance(value, File):
                        print '%s: (%s) %s' % (
                            key, value.content_type, str(value))
                yield item
    provideUtility(OFSFilePrinter,
        name=u'plone.app.transmogrifier.tests.ofsfileprinter')

def uidSetUp(test):
    sectionsSetUp(test)

    from Products.Archetypes.interfaces import IReferenceable

    class MockReferenceableObject(object):
        implements(IReferenceable)

        def __init__(self, path, portal):
            self.path = path
            self.portal = portal

        _at_uid = 'xyz'
        def UID(self):
            return self._at_uid

        def _setUID(self, uid):
            self.portal.uids_set.append((self.path, uid))
            self._at_uid = uid

    class MockPortal(object):
        implements(IReferenceable)

        _last_path = None
        def unrestrictedTraverse(self, path, default):
            if path[0] == '/':
                return default # path is absolute
            if isinstance(path, unicode):
                return default
            if path == 'not/existing/bar':
                return default
            if path.endswith('/notatcontent'):
                return object()
            return MockReferenceableObject(path, self)

        uids_set = []

    test.globs['plone'] = MockPortal()
    test.globs['transmogrifier'].context = test.globs['plone']

    class UIDSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(UIDSource, self).__init__(*args, **kw)
            self.sample = (
                dict(_path='/spam/eggs/foo',     _uid='abc',), # will be set
                dict(_path='/spam/eggs/bar',     _uid='xyz',), # same as default
                dict(_path='not/existing/bar',   _uid='def',), # not found
                dict(                            _uid='geh',), # no path
                dict(_path='/spam/eggs/baz',                ), # no uid
                dict(_path='/spam/notatcontent', _uid='ijk',), # not referenceable
            )
    provideUtility(UIDSource,
        name=u'plone.app.transmogrifier.tests.uidsource')


def reindexObjectSetup(test):
    sectionsSetUp(test)

    from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
    from Products.Archetypes.interfaces import IBaseObject

    class MockCatalogAwareObject(CMFCatalogAware): pass

    class MockPortal(object):
        implements(IBaseObject)

        _last_path = None
        def unrestrictedTraverse(self, path, default):
            if path[0] == '/':
                return default # path is absolute
            if isinstance(path, unicode):
                return default
            if path == 'not/existing/bar':
                return default
            if path == 'not/a/catalog/aware/content':
                return default
            self._last_path = path
            return MockCatalogAwareObject(self)

        @property
        def portal_catalog(self):
            return self

        reindexed = ()
        def reindexObject(self, ob):
            self.reindexed += ((self._last_path, 'reindexed'),)

    test.globs['plone'] = MockPortal()
    test.globs['transmogrifier'].context = test.globs['plone']

    class ReindexObjectSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(ReindexObjectSource, self).__init__(*args, **kw)
            self.sample = (
                dict(_path='/spam/eggs/foo'), # will be set
                dict(_path='/spam/eggs/bar'), # will be set
                dict(_path='/spam/eggs/baz'), # will be set
                dict(_path='not/a/catalog/aware/content',
                     title='Should not be reindexed, not a CMFCatalogAware content'),
                dict(_path='not/existing/bar',
                     title='Should not be reindexed, not an existing path'),
            )
    provideUtility(ReindexObjectSource,
        name=u'plone.app.transmogrifier.tests.reindexobjectsource')

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'portaltransforms.txt',
            setUp=portalTransformsSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'atschemaupdater.txt',
            setUp=aTSchemaUpdaterSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'uidupdater.txt',
            setUp=uidSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'workflowupdater.txt',
            setUp=workflowUpdaterSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'browserdefault.txt',
            setUp=browserDefaultSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'urlnormalizer.txt',
            setUp=urlNormalizerSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'criteria.txt', setUp=criteriaSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'mimeencapsulator.txt',
            setUp=mimeencapsulatorSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'reindexobject.txt',
            setUp=reindexObjectSetup, tearDown=tearDown),
    ))
