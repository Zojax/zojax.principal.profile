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
import logging

from zope import interface, component
from zope.component import getUtility, getMultiAdapter
from zope.cachedescriptors.property import Lazy
from zope.traversing.browser import absoluteURL
from zope.app.component.hooks import getSite
from zope.app.intid.interfaces import IIntIds
from zope.publisher.interfaces import IPublishTraverse

from zojax.filefield.data import Image
from zojax.converter.api import convert
from zojax.converter.interfaces import ConverterException
from zojax.content.forms.form import AddForm
from zojax.content.type.interfaces import IContentType
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.layoutform import button, Fields, PageletForm, PageletEditForm
from zojax.widget.radio.field import RadioChoice
from zojax.principal.profile.interfaces import _, IAvatar


class Configlet(PageletEditForm):
    """ configlet view """

    @property
    def label(self):
        return self.context.__title__

    @property
    def description(self):
        return self.context.__description__

    @Lazy
    def fields(self):
        return Fields(self.context.__schema__).omit('default')


class Avatar(object):

    def __call__(self):
        return self.context.data.show(self.request)


class AvatarTraverser(object):
    interface.implements(IPublishTraverse)
    component.adapts(IAvatar, interface.Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        if name != 'index.html':
            request.response.setHeader(
                'Cache-Control', 'public, max-age=31536000')
            request.response.setHeader(
                'Expires', u"Fri, 01 Jan, 2100 01:01:01 GMT")
            request.response.setHeader(
                'Last-Modified', u"Sat, 01 Jan, 2000 01:01:01 GMT")

        return getMultiAdapter((self.context, request), name='index.html')


class Avatars(AddForm):

    fields = Fields(IAvatar)
    label = _(u'Upload avatar')
    prefix = 'upload'

    def __init__(self, context, view, request):
        self.container = context
        self.view = view
        self.request = request
        self.context = getUtility(
            IContentType, 'profile.avatar').__bind__(context)

    @property
    def description(self):
        context = self.container
        return _(
            u'Create new avatar. Maximum size: ${width} x ${height} pixels.',
            mapping={'width': context.maxWidth, 'height': context.maxHeight})

    @button.buttonAndHandler(_('Upload'))
    def handleUpload(self, action):
        data, errors = self.extractData()
        if errors:
            pass
        else:
            file = data['data']

            image = Image()
            image.data = file.data
            image.mimeType = file.mimeType

            if (image.width > self.container.maxWidth or
                image.height > self.container.maxHeight):
                try:
                    image.data = convert(
                        image.data, 'image/jpeg',
                        sourceMimetype = image.mimeType,
                        width = self.container.maxWidth,
                        height = self.container.maxHeight, quality=88)
                except ConverterException, err:
                    log = logging.getLogger('zojax.profile.avatar')
                    log.log(logging.WARNING, str(err))
                    IStatusMessage(self.request).add(err, 'error')
                    return

            if not data['title']:
                data['title'] = file.filename

            avatar = self.context.create(title=data['title'], data=image)
            self.context.add(avatar)
            IStatusMessage(self.request).add(_(u'Avatar sccessully uploaded.'))
            self.redirect('.')


class IAvatarGallery(interface.Interface):

    avatar = RadioChoice(
        title = _('Select avatar'),
        vocabulary = 'global.avatars',
        horizontal = True,
        required = False)


class AvatarGallery(PageletForm):

    label = _('Avatar Gallery')
    fields = Fields(IAvatarGallery)
    ignoreContext = True
    prefix = 'gallery'

    def update(self):
        self.url = absoluteURL(getSite(), self.request)
        self.default = self.context.default

        super(AvatarGallery, self).update()

    def isAvailable(self):
        return len(self.context) > 0

    @button.buttonAndHandler(_('Set as default'))
    def handleSetDefault(self, action):
        data, errors = self.extractData()

        avatar = data['avatar']
        if not avatar:
            IStatusMessage(self.request).add(
                _('Please select avatar.'), 'warning')
        else:
            self.context.default = int(avatar)
            self.default = self.context.default
            IStatusMessage(self.request).add(
                _('Default avatar has been selected.'))

    @button.buttonAndHandler(_('Remove avatar'))
    def handleRemove(self, action):
        data, errors = self.extractData()

        avatar = data['avatar']
        if not avatar:
            IStatusMessage(self.request).add(
                _('Please select avatar.'), 'warning')
        else:
            ids = getUtility(IIntIds)
            ob = ids.queryObject(int(avatar))

            if ob is not None:
                del self.context[ob.__name__]
                IStatusMessage(self.request).add(_('Avatar has been removed.'))
                self.redirect('.')
