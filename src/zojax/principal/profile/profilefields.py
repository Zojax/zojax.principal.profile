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
from zojax.content.type.configlet import ContentContainerConfiglet
from zojax.persistent.fields.interfaces import IFieldType, IFieldSchema

from interfaces import _, IProfileField, IProfileFields


class ProfileFields(ContentContainerConfiglet):
    interface.implements(IProfileFields)

    title = _(u'User profile fields')


class ProfileFieldSchema(object):
    interface.implements(IFieldSchema)
    component.adapts(IProfileFields, IFieldType)

    title = u''
    weight = 1
    schema = IProfileField

    def __init__(self, container, contentType):
        pass
