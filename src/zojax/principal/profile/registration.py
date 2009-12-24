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
from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds

from zojax.principal.profile.interfaces import IProfileFields, IPersonalProfile


class RegistrationFields(object):

    def getFields(self):
        fields = []
        configletFields = getUtility(IProfileFields).getFields()
        ids  = getUtility(IIntIds)

        seen = set()
        for field in self.fields:
            fieldObject = ids.getObject(field)
            if fieldObject in configletFields and field not in seen:
                seen.add(field)
                fields.append(fieldObject)
        return fields

    def registerPrincipal(self, principal, data):
        profile = IPersonalProfile(principal, None)
        fields = [field.__name__ for field in self.getFields()]
        if profile is not None:
            data = dict([(key, value)
                         for key, value in data.items() if key in fields])
            profile.setProfileData(data)
