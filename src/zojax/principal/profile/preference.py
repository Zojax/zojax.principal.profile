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
import datetime
from zope import interface
from zope.component import getUtility, getUtilitiesFor
from zope.datetime import parseDatetimetz
from zope.app.component.hooks import getSite
from zope.app.intid.interfaces import IIntIds
from zope.traversing.browser import absoluteURL
from zope.cachedescriptors.property import Lazy

from interfaces import IPrincipalInformation, IPersonalSpaceService
from interfaces import IPersonalProfile, IProfileFields, IAvatarConfiglet


class PersonalProfile(object):
    interface.implements(IPersonalProfile)

    @Lazy
    def _principalinfo(self):
        return IPrincipalInformation(self.__principal__)

    @property
    def title(self):
        return self._principalinfo.title

    @property
    def firstname(self):
        return self._principalinfo.firstname

    @property
    def lastname(self):
        return self._principalinfo.lastname

    @property
    def email(self):
        return self._principalinfo.email

    @Lazy
    def space(self):
        principal = self.__principal__
        for name, service in getUtilitiesFor(IPersonalSpaceService):
            space = service.queryPersonalSpace(principal)
            if space is not None:
                return space

    def getProfileData(self):
        intids = getUtility(IIntIds)
        fields = getUtility(IProfileFields)

        if self.profileData is None:
            self.profileData = {}

        profileData = self.profileData

        data = {}
        for name, field in fields.items():
            id = intids.getId(field)

            data[name] = profileData.get(id, getattr(field, 'default', None))

        return data

    def setProfileData(self, data):
        intids = getUtility(IIntIds)
        fields = getUtility(IProfileFields)

        if self.profileData is None:
            self.profileData = {}

        profileData = self.profileData

        changes = []

        for name, field in fields.items():
            id = intids.getId(field)
            value = data.get(name, field.default)

            if profileData.get(id) != value:
                changes.append(name)

            profileData[id] = value

        self.profileData = profileData

        return changes

    def avatarUrl(self, request):
        url = '%s/@@profile.avatar'%absoluteURL(getSite(), request)

        if self.avatar == 0:
            return '%s/%s'%(url, self.__principal__.id)
        elif self.avatar is None:
            return '%s/%s'%(url, getUtility(IAvatarConfiglet).default or 0)
        else:
            return '%s/%s'%(url, self.avatar)


def principalRegisteredHandler(event):
    prefs = IPersonalProfile(event.principal, None)
    if prefs is not None:
        prefs.registered = parseDatetimetz(str(datetime.datetime.now()))


def principalLoggedinHandler(event):
    prefs = IPersonalProfile(event.principal, None)
    if prefs is not None:
        lastLoginTime = prefs.lastLoginTime

        if lastLoginTime is not None:
            dt = parseDatetimetz(str(datetime.datetime.now()))
            td = dt - prefs.lastLoginTime
            if td.days or td.seconds > 60:
                prefs.lastLoginTime = dt
        else:
            prefs.lastLoginTime = parseDatetimetz(str(datetime.datetime.now()))
