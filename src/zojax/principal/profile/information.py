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
from rwproperty import getproperty, setproperty

from zope import interface, component
from zope.component import getUtility
from zope.security.interfaces import IPrincipal
from zope.security.proxy import removeSecurityProxy

from interfaces import IPersonalEmailsConfiglet
from interfaces import IPersonalProfile, IPrincipalInformation


class PrincipalInformation(object):
    component.adapts(IPrincipal)
    interface.implements(IPrincipalInformation)

    readonly = False

    def __init__(self, principal):
        self.principal = principal
        self.profile = IPersonalProfile(principal)

    @getproperty
    def title(self):
        title = u'%s %s'%(self.firstname, self.lastname)
        return title.strip() or self.principal.title

    @getproperty
    def firstname(self):
        return getattr(self.profile.data, 'firstname', self.principal.title)

    @getproperty
    def lastname(self):
        return getattr(self.profile.data, 'lastname', u'')

    @getproperty
    def email(self):
        return getattr(self.profile.data, 'email', u'')

    @setproperty
    def firstname(self, value):
        self.profile.data.firstname = value

    @setproperty
    def lastname(self, value):
        self.profile.data.lastname = value

    @setproperty
    def email(self, value):
        configlet = removeSecurityProxy(
            getUtility(IPersonalEmailsConfiglet))
        configlet.update(self.principal.id, value)

        self.profile.data.email = value
