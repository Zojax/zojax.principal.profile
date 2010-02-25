##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""

from zope import interface, component
from zope.app.intid.interfaces import IIntIds
from zope.security import checkPermission

from interfaces import IPersonalProfileCompleteChecker, IPersonalProfile, \
                       IProfileFields


class BasicChecker(object):
    
    component.adapts(IPersonalProfile)
    interface.implements(IPersonalProfileCompleteChecker)

    def __init__(self, context):
        self.context = context

    def check(self):
        intids = component.getUtility(IIntIds)
        profileData = self.context.profileData
        
        for field in component.getUtility(IProfileFields).getFields():
            id = intids.getId(field)
            if field.required and \
                profileData.get(id, getattr(field, 'default', None)) == \
                getattr(field, 'missing_value', None):
                return False
            
        return bool(self.context.firstname) \
               and bool(self.context.lastname) \
               and bool(self.context.email)
               
