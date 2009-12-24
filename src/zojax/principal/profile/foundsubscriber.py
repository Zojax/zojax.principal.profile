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
from zope.app.security.interfaces import IAuthentication
from zope.app.authentication.interfaces import IPrincipalCreated
from zope.app.authentication.interfaces import IPluggableAuthentication

from interfaces import IPrincipalInformation

@component.adapter(IPrincipalCreated)
def foundPrincipalCreated(event):
    principal = event.principal
    info = IPrincipalInformation(principal)
    principal.firstname = info.firstname
    principal.lastname = info.lastname
    principal.title = '%s %s'%(info.firstname, info.lastname)
