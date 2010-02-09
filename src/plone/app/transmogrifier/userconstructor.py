from zope.interface import classProvides, implements

from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.utils import defaultMatcher
from collective.transmogrifier.utils import Condition

class UserConstructorSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context

        self.portal_membership = transmogrifier.context.portal_membership
        self.createMemberArea = Condition(options.get('create-member-area',
                                                      'python:False'),
                                          transmogrifier, name, options)

        self.usernamekey = defaultMatcher(options, 'username-key',
                                          name, key='username')
        self.passwordkey = defaultMatcher(options, 'password-key',
                                          name, key='password')
        self.emailkey = defaultMatcher(options, 'email-key',
                                       name, key='email')
        self.fullnamekey = defaultMatcher(options, 'fullname-key',
                                          name, key='fullname')
        self.roleskey = defaultMatcher(options, 'roles-key',
                                       name, key='roles')

    def __iter__(self):

        pm = self.portal_membership

        for item in self.previous:

            usernamekey = self.usernamekey(*item.keys())[0]
            passwordkey = self.passwordkey(*item.keys())[0]
            emailkey = self.emailkey(*item.keys())[0]
            fullnamekey = self.fullnamekey(*item.keys())[0]
            roleskey = self.roleskey(*item.keys())[0]

            if (usernamekey and passwordkey and emailkey and fullnamekey \
                and roleskey) is None:
                yield item; continue # not enough infos

            username = item[usernamekey]
            if pm.getMemberById(username) is not None:
                yield item; continue # existing user

            password = item[passwordkey]
            email = item[emailkey]
            fullname = item[fullnamekey]
            roles = item[roleskey]
            if isinstance(roles, basestring):
                roles = (roles,)

            # add the user
            pm.addMember(username, password, roles, [],
                         properties={"email": email, "fullname": fullname})

            # add his member area
            if self.createMemberArea(item):
                pm.createMemberArea(member_id=username)

            yield item

