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
from zope.i18nmessageid import MessageFactory
from zojax.controlpanel.interfaces import ICategory
from zojax.content.type.interfaces import IContentType
from zojax.preferences.interfaces import IPreferenceCategory
from zojax.filefield.field import ImageField
from zojax.widget.list.field import SimpleList
from zojax.widget.radio.field import RadioChoice

_ = MessageFactory('zojax.principal.profile')


class IProfilesCategory(ICategory):
    """ user profiles configlet category """

    profileImageWidth = schema.Int(
        title = u'Profile image width',
        default = 250,
        required = True)

    profileImageHeight = schema.Int(
        title = u'Profile image height',
        default = 500,
        required = True)

    fieldCategories = SimpleList(
        title = u'Field categories',
        default = [],
        value_type = schema.TextLine(),
        required = False)

    quickInfoFields = schema.List(
        title = u'Quick info',
        description = u'Show this fields in quick info portlet.',
        value_type = schema.Choice(vocabulary='profile.fields'),
        default = [],
        required = False)


class IProfileFields(interface.Interface):
    """ user profiles configuration """


class IProfileField(interface.Interface):
    """ field schema """

    searchable = schema.Bool(
        title = _(u'Searchable'),
        description = _(u'The value of this field will show up in search results.'),
        default = False,
        required = False)

    visible = schema.Bool(
        title = _(u'Visible'),
        description = _(u'Whether or not the field is visible to the public.'),
        default = True,
        required = False)

    editable = schema.Bool(
        title = _(u'Editable'),
        description = _(u'Whether or not the field can be changed by the user.'),
        default = True,
        required = False)

    category = schema.Choice(
        title = _(u'Category'),
        vocabulary = 'profile.fieldCategories',
        required = False)


class IProfileFilterableField(interface.Interface):
    """ field schema """

    filterable = schema.Bool(
        title = _(u'Filterable'),
        description = _(u'Users can filter based on this field.'),
        default = False,
        required = False)


class IPersonalProfile(IPreferenceCategory):
    """ personal profile """

    title = interface.Attribute('Principal full name')
    firstname = interface.Attribute('Principal first name')
    lastname = interface.Attribute('Principal last name')
    email = interface.Attribute('Principal email')
    space = interface.Attribute('Personal space')

    profileImage = ImageField(
        title = _(u'Profile image'),
        description = _(u'You can upload a JPG, GIF or PNG.'),
        required = False)

    avatar = schema.Choice(
        title = _(u'Avatar'),
        vocabulary = 'profile.avatars',
        required = False)

    avatarImage = ImageField(
        title = _(u'Avatar is a small image of you that will be displayed next to your blog posts or comments.'),
        description = _(u'You can upload the same image you used for your profile or choose a different one.'),
        required = False)

    timezone = schema.Choice(
        title = _(u'Timezone'),
        vocabulary = u'Timezones',
        required = False)

    profileData = schema.Dict(
        title = _(u'Profile data'),
        required = False)

    registered = schema.Datetime(
        title = _(u'Registered'),
        description = _(u'Date of registration.'),
        required = False)

    lastLoginTime = schema.Datetime(
        title = _(u'Last login time'),
        description = _('Date when principal last logged in.'),
        required = False)

    def avatarUrl(request):
        """Return url to avatar."""

    def getProfileData():
        """Return dict with profile data."""

    def setProfileData(data):
        """Save profile data."""


class IPersonalSpaceService(interface.Interface):
    """ personal space service """

    def queryPersonalSpace(principal):
        """ return personal space (traversable object) """


class IPrincipalInformation(interface.Interface):
    """ principal information for IPrincipal """

    title = interface.Attribute('Title')
    firstname = interface.Attribute('First name')
    lastname = interface.Attribute('Last name')
    email = interface.Attribute('Email')
    readonly = interface.Attribute('Readonly information')


class IAvatar(interface.Interface):
    """ Avatar """

    title = schema.TextLine(
        title = _(u'Title'),
        description = _(u'Avatar title.'),
        required = False)

    data = ImageField(
        title = u'File',
        description = _(u'Avatar image data.'),
        required = True)


class IAvatarConfiglet(interface.Interface):
    """ avatar settings configlet """

    enabled = schema.Bool(
        title = _('Enable Avatars'),
        description = _('When Avatars are enabled, users may choose from preselected profile photos, or upload their own. If Disabled, users may only upload thier own profile photo.'),
        default = True)

    maxWidth = schema.Int(
        title = _('Maximum Image Width'),
        default = 64)

    maxHeight = schema.Int(
        title = _('Maximum Image Height'),
        default = 64)

    default = schema.Choice(
        title = _(u'Default avatar'),
        vocabulary = 'global.avatars',
        required = False)


class IPersonalEmailsConfiglet(interface.Interface):
    """ personal emails configlet """

    emails = interface.Attribute('Email to principal id mapping')

    principals = interface.Attribute('Principal id to email mapping')

    def update(principalId, email):
        """ update principal to email mapping """

    def remove(principalId):
        """ remvoe principal to email mapping """

    def getPrincipalEmail(principalId):
        """ return email for principal """

    def getPrincipalByEmail(email):
        """ return principal by email """


class IRegistrationFields(interface.Interface):
    """ registration fields configlet """

    fields = schema.List(
        title = _(u'Registration fields'),
        description = _(u'List of fields user should fill during registration.'),
        value_type = schema.Choice(vocabulary='profile.fields'),
        default = [],
        required = False)

    def getFields():
        """Rerturn list of profile fields."""

    def registerPrincipal(principal, data):
        """Save newly registered principal profile data."""
