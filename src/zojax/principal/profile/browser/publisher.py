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
from zope.component import getUtility
from zope.location import LocationProxy
from zope.app.intid.interfaces import IIntIds
from zope.app.component.hooks import getSite
from zope.app.component.interfaces import ISite
from zope.traversing.namespace import getResource
from zope.publisher.interfaces import NotFound, IPublishTraverse
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError
from zojax.principal.profile.interfaces import \
    IAvatar, IAvatarConfiglet, IPersonalProfile


class Avatar(object):
    interface.implements(IPublishTraverse)
    component.adapts(ISite, interface.Interface)

    __name__ = 'profile.avatar'

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context

    def publishTraverse(self, request, name):
        content = None

        try:
            id = int(name)
            content = getUtility(IIntIds).queryObject(id)
        except:
            pass

        if IAvatar.providedBy(content):
            return LocationProxy(content, self, name)

        auth = getUtility(IAuthentication)
        try:
            principal = auth.getPrincipal(name)
            prefs = IPersonalProfile(principal)
            if prefs.avatarImage:
                return LocationProxy(prefs.avatarImage, self, name)
        except PrincipalLookupError:
            if name != '0':
                raise NotFound(self, request, name)

        return getResource(getSite(), 'avatarEmptyImage.png', request)
