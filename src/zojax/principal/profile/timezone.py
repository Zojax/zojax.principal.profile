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
""" ITZInfo for principal

$Id$
"""
from pytz import timezone
from zope import component, interface
from zope.security.interfaces import IPrincipal
from zope.interface.common.idatetime import ITZInfo
from zope.publisher.interfaces.browser import IBrowserRequest

from interfaces import IPersonalProfile


@component.adapter(IPrincipal)
@interface.implementer(ITZInfo)
def getPrincipalTimezone(principal):
    prefs = IPersonalProfile(principal, None)
    if prefs is not None:
        try:
            return timezone(prefs.timezone)
        except:
            pass


@component.adapter(IBrowserRequest)
@interface.implementer(ITZInfo)
def getRequestTimezone(request):
    return ITZInfo(request.principal, None)
