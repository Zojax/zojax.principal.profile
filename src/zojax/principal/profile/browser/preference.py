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
import logging, sys

from zope import interface, schema, event
from zope.lifecycleevent import Attributes, ObjectModifiedEvent
from zope.component import getUtility
from zope.proxy import removeAllProxies
from zope.security import checkPermission
from zope.app.component.hooks import getSite
from zope.app.intid.interfaces import IIntIds
from zope.traversing.browser import absoluteURL

from z3c.form.group import Group

from zojax.layoutform.interfaces import ISaveAction
from zojax.layoutform import button, Fields
from zojax.layoutform import PageletEditForm, PageletEditSubForm
from zojax.filefield.data import Image
from zojax.filefield.field import ImageField
from zojax.filefield.interfaces import IFileDataNoValue, IFileDataClear
from zojax.widget.radio.field import RadioChoice
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.converter.api import convert
from zojax.converter.interfaces import ConverterException
from zojax.content.type.interfaces import IOrder
from zojax.principal.profile.interfaces import _
from zojax.principal.profile.interfaces import IPrincipalInformation
from zojax.principal.profile.interfaces import IProfileFields, IPersonalProfile
from zojax.principal.profile.interfaces import IProfilesCategory, IAvatarConfiglet

from interfaces import IPrincipalInformationForm


class PersonalProfile(PageletEditForm):

    label = _('Information')

    @property
    def fields(self):
        fields = Fields(IPersonalProfile).omit(
            'profileData', 'registered', 'modified',
            'lastLoginTime', 'avatar', 'avatarImage')

        info = IPrincipalInformation(self.context.__principal__)
        if not info.readonly:
            fields = Fields(IPrincipalInformationForm) + fields

        return fields

    def getContent(self):
        data = dict(self.context.getProfileData())
        data['timezone'] = self.context.timezone
        data['__principal__'] = self.context.__principal__

        info = IPrincipalInformation(self.context.__principal__)
        if not info.readonly:
            data['firstname'] = info.firstname
            data['lastname'] = info.lastname
            data['email'] = info.email

        return data

    def updateForms(self):
        super(PersonalProfile, self).updateForms()

        manager = checkPermission('zojax.ManagerProfileFields', self)

        fields = getUtility(IProfileFields).getFields()
        ids = getUtility(IIntIds)
        fieldCategories = getUtility(IProfilesCategory).fieldCategories
        self.groups = list(self.groups)

        default = []
        categories = {}
        for field in fields:
            if not (field.editable or manager):
                continue

            if field.category not in fieldCategories:
                default.append(field)
            else:
                categories.setdefault(field.category, []).append(field)

        if default:
            group = Category(self.context, self.request, self, u'', default)
            group.update()
            self.groups.append(group)

        for key in fieldCategories:
            if key not in categories:
                continue
            fields = categories[key]
            if fields:
                group = Category(self.context, self.request, self, key, fields)
                group.update()
                self.groups.append(group)

    def applyChanges(self, data):
        changes = list(self.context.setProfileData(data))
        self.context.timezone = data['timezone']

        if 'profileImage' in data and \
                not IFileDataNoValue.providedBy(data['profileImage']):
            image = Image()
            image.data = data['profileImage'].data
            image.mimeType = data['profileImage'].mimeType

            configlet = getUtility(IProfilesCategory)
            if (image.width > configlet.profileImageWidth or
                image.height > configlet.profileImageHeight):
                try:
                    image.data = convert(
                        image.data, 'image/jpeg',
                        sourceMimetype = image.mimeType,
                        width = configlet.profileImageWidth,
                        height = configlet.profileImageHeight, quality=88)

                except ConverterException, err:
                    log = logging.getLogger('zojax.profile')
                    log.log(logging.WARNING, str(err))
                    IStatusMessage(self.request).add(err, 'error')
                else:
                    self.context.profileImage = image
            else:
                self.context.profileImage = image
            changes.append('profileImage')

        if changes:
            changes = {IPersonalProfile: changes}
        else:
            changes = {}

        # set principal information
        info = IPrincipalInformation(self.context.__principal__)
        if not info.readonly:
            changed = []
            for attr in ('firstname', 'lastname', 'email'):
                val = getattr(info, attr, None)
                if val != data[attr]:
                    setattr(info, attr, data[attr])
                    changed.append(attr)

            if changed:
                changes[IPrincipalInformation] = changed

        if not changes:
            changes = {IPersonalProfile: ('avatarImage',)}
        else:
            descriptions = []
            for interface, names in changes.items():
                descriptions.append(
                    Attributes(interface, *names))
            event.notify(
                ObjectModifiedEvent(self.context))
        return changes

    def nextURL(self):
        return '../../'


class Category(Group):

    prefix = 'category'

    def __init__(self, context, request, form, label, fields):
        super(Category, self).__init__(context, request, form)

        self.label = label
        self.fields = Fields(*fields)

    def getContent(self):
        return self.parentForm.getContent()

    def postUpdate(self):
        pass


class IAvatar(interface.Interface):

    avatar = RadioChoice(
        title = _('Avatar'),
        vocabulary = 'profile.prefs.avatars',
        horizontal = True,
        required = False)

    avatarImage = ImageField(
        title = _(u'Avatar is a small image of you that will be '
                  u'displayed next to your blog posts or comments.'),
        description = _(u'You can upload the same image you used for '
                        u'your profile or choose a different one.'),
        required = False)


class Avatar(PageletEditSubForm):

    fields = Fields(IAvatar)

    def update(self):
        self.url = absoluteURL(getSite(), self.request)

        super(Avatar, self).update()

    def getContent(self):
        return {'avatar': self.context.avatar,
                'context': self.context}

    def isAvailable(self):
        return not getUtility(IProfilesCategory).photoAsAvatar

    @button.handler(ISaveAction)
    def handleApply(self, action):
        data, errors = self.extractData()
        if not errors:
            self.context.avatar = data['avatar']

            if 'avatarImage' in data and \
                    not IFileDataNoValue.providedBy(data['avatarImage']):
                image = Image()
                image.data = data['avatarImage'].data
                image.mimeType = data['avatarImage'].mimeType

                configlet = getUtility(IAvatarConfiglet)
                if (image.width > configlet.maxWidth or
                    image.height > configlet.maxHeight):
                    try:
                        image.data = convert(
                            image.data, 'image/jpeg',
                            sourceMimetype = image.mimeType,
                            width = configlet.maxWidth,
                            height = configlet.maxHeight, quality=88)
                    except ConverterException, err:
                        log = logging.getLogger('zojax.profile')
                        log.log(logging.WARNING, str(err))
                        IStatusMessage(self.request).add(err, 'error')
                        return
                    else:
                        self.context.avatarImage = image
                else:
                    self.context.avatarImage = image

                self.context.avatar = 0
