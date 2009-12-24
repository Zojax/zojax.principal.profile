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
import logging
import datetime

from zope import interface, component
from zope.component import queryUtility, getUtility, getUtilitiesFor
from zope.datetime import parseDatetimetz
from zope.app.component.hooks import getSite
from zope.app.intid.interfaces import IIntIds
from zope.traversing.browser import absoluteURL
from zope.cachedescriptors.property import Lazy
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from zc.copy import copy
from zojax.converter.api import convert
from zojax.converter.interfaces import ConverterException

from interfaces import IProfilesCategory
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
        fields = getUtility(IProfileFields).getFields()

        if self.profileData is None:
            self.profileData = {}

        profileData = self.profileData

        data = {}
        for field in fields:
            name = field.__name__
            id = intids.getId(field)

            data[name] = profileData.get(id, getattr(field, 'default', None))

        return data

    def setProfileData(self, data):
        intids = getUtility(IIntIds)
        fields = getUtility(IProfileFields).getFields()

        if self.profileData is None:
            self.profileData = {}

        profileData = self.profileData

        changes = []

        for field in fields:
            name = field.__name__
            id = intids.getId(field)
            value = data.get(name, field.default)

            if profileData.get(id) != value:
                changes.append(name)

            profileData[id] = value

        self.profileData = profileData

        return changes

    def photoUrl(self, request):
        url = '%s/@@profile.photo'%absoluteURL(getSite(), request)

        if self.profileImage:
            return '%s/%s/%s'%(
                url, self.__principal__.id, self.profileImage.hash)
        else:
            return '%s/%s'%(url, self.__principal__.id)

    def avatarUrl(self, request):
        url = '%s/@@profile.avatar'%absoluteURL(getSite(), request)

        intids = getUtility(IIntIds)
        configlet = getUtility(IAvatarConfiglet)

        if self.avatar is None or not getUtility(IProfilesCategory).enableAvatars:
            return '%s/%s'%(url, configlet.default or 0)
        else:
            intids = queryUtility(IIntIds)
            if intids is not None:
                avatar = intids.queryObject(self.avatar)
            else:
                avatar = None

            if avatar is None:
                if self.avatarImage:
                    return '%s/%s/%s'%(
                        url, self.__principal__.id, self.avatarImage.hash)
                else:
                    return '%s/%s'%(url, self.__principal__.id, )
            else:
                return '%s/%s/%s'%(url, self.avatar, avatar.data.hash)


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


@component.adapter(IPersonalProfile, IObjectModifiedEvent)
def principalProfileModified(profile, event):
    profile.modified = parseDatetimetz(str(datetime.datetime.now()))

    configlet = getUtility(IProfilesCategory)
    if configlet.photoAsAvatar and profile.profileImage:
        image = copy(profile.profileImage)
        configlet = getUtility(IAvatarConfiglet)
        if (image.width > configlet.maxWidth or
            image.height > configlet.maxHeight):
            try:
                image.data = convert(
                    image.data, 'image/jpeg',
                    sourceMimetype = image.mimeType,
                    width = configlet.maxWidth,
                    height = configlet.maxHeight, quality=88)
            except ConverterException, err:
                log = logging.getLogger('zojax.personal.profile')
                log.log(logging.WARNING, str(err))
                return
            else:
                profile.avatarImage = image
        else:
            profile.avatarImage = image

        profile.avatar = 0
