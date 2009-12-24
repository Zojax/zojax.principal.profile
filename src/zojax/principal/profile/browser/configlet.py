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
from zope.cachedescriptors.property import Lazy

from zojax.layoutform import Fields
from zojax.controlpanel.browser.configlet import Configlet
from zojax.principal.profile.interfaces import IProfilesCategory


class UserProfilesConfiglet(Configlet):

    @Lazy
    def fields(self):
        return Fields(IProfilesCategory).omit('fieldCategories')
