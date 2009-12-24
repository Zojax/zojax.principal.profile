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
from BTrees.OOBTree import OOBTree

from zope import interface, component
from zope.component import getUtility
from zope.security.interfaces import IPrincipal
from zope.security.proxy import removeSecurityProxy
from zope.app.security.interfaces import IAuthentication
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zojax.mail.interfaces import IMailAddress, IPrincipalByEMail

from interfaces import IPersonalEmailsConfiglet


class PersonalEmails(object):
    interface.implements(IPersonalEmailsConfiglet)

    @property
    def emails(self):
        data = self.data
        emails = data.get('emails')
        if emails is None:
            emails = OOBTree()
            data['emails'] = emails
        return emails

    @property
    def principals(self):
        data = self.data
        principals = data.get('principals')
        if principals is None:
            principals = OOBTree()
            data['principals'] = principals
        return principals

    def update(self, principalId, email):
        self.remove(principalId)

        if email:
            self.emails[email] = principalId
            self.principals[principalId] = email

    def remove(self, principalId):
        principals = self.principals

        if principalId in principals:
            email = principals.get(principalId)
            if email in self.emails:
                del self.emails[email]
            del principals[principalId]

    def getPrincipalEmail(self, principalId):
        return self.principals.get(principalId)

    def getPrincipalByEmail(self, email):
        return self.emails.get(email)

    def isAvailable(self):
        return False


class PrincipalByEMail(object):
    interface.implements(IPrincipalByEMail)

    def getPrincipal(self, email):
        configlet = getUtility(IPersonalEmailsConfiglet)

        pId = configlet.getPrincipalByEmail(email)
        if pId is not None:
            return getUtility(IAuthentication).getPrincipal(pId)


@component.adapter(IPrincipal)
@interface.implementer(IMailAddress)
def getPrincipalEMail(principal):
    configlet = removeSecurityProxy(
        getUtility(IPersonalEmailsConfiglet))

    email = configlet.getPrincipalEmail(principal.id)
    if email:
        return PrincipalEMail(email)


class PrincipalEMail(object):
    @interface.implementer(IMailAddress)

    def __init__(self, email):
        self.address = email
