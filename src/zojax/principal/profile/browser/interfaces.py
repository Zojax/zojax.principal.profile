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
from zojax.principal.profile.interfaces import _

from field import PersonalEmailField


class IPrincipalInformationForm(interface.Interface):
    """ principal information for IPrincipal """

    firstname = schema.TextLine(
        title=_('First Name'),
        description=_(u"e.g. John. This is how users "
                      u"on the site will identify you."),
        required = True)

    lastname = schema.TextLine(
        title=_('Last Name'),
        description=_(u"e.g. Smith. This is how users "
                      u"on the site will identify you."),
        required = True)

    email = PersonalEmailField(
        title = _(u'E-Mail'),
        description = _(u'Enter your e-mail address. It will be used as address for email notifications.'),
        required = False)
