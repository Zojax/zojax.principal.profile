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
from zojax.layoutform import button, Fields, PageletEditSubForm
from zojax.principal.profile.interfaces import IRegistrationFields
from zojax.principal.registration.interfaces import IMemberRegisterAction


class RegistrationProfileFields(PageletEditSubForm):

    prefix = 'profile'
    ignoreContext = True

    @property
    def fields(self):
        return Fields(*getUtility(IRegistrationFields).getFields())

    @button.handler(IMemberRegisterAction)
    def handleRegister(self, action):
        data, errors = self.extractData()
        if not errors and self.parentForm.registeredPrincipal is not None:
            getUtility(IRegistrationFields).registerPrincipal(
                self.parentForm.registeredPrincipal, data)

    def isAvailable(self):
        return bool(getUtility(IRegistrationFields).getFields())
