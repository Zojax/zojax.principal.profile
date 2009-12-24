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
from zope import interface, schema
from zope.app.security.interfaces import PrincipalLookupError
from z3c.schema.email import RFC822MailAddress
from zojax.mail.utils import getPrincipalByEMail
from zojax.principal.profile.interfaces import IPrincipalInformation

from interfaces import _


class IPersonalEmailField(interface.Interface):
    """ personal email field """


class EmailAlreadyInUseError(schema.ValidationError):
    __doc__ = _('E-Mail address already in use.')


class PersonalEmailField(RFC822MailAddress):
    interface.implements(IPersonalEmailField)

    def validate(self, value):
        super(PersonalEmailField, self).validate(value)

        if self.context is None:
            return

        if value is None:
            return

        principal = self.context['__principal__']

        value = value.lower()
        oldvalue = self.query(principal)

        try:
            principalId = getPrincipalByEMail(value).id
        except PrincipalLookupError:
            return

        if value != oldvalue and principalId != principal.id:
            raise EmailAlreadyInUseError()

    def query(self, object, default=None):
        return IPrincipalInformation(object).email
