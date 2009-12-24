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
from zojax.wizard.step import WizardStep
from zojax.table.interfaces import ITableConfiguration
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.content.type.interfaces import IContainerContentsTable
from zojax.principal.profile.interfaces import \
    _, IProfileFields, IProfilesCategory


class TableConfiguration(object):
    interface.implements(ITableConfiguration)
    component.adapts(IProfileFields,interface.Interface,IContainerContentsTable)

    pageSize = 0
    enabledColumns = ('id', 'icon', 'name', 'title', 'type')
    disabledColumns = ()

    def __init__(self, context, request, table):
        pass


class FieldCategories(WizardStep):

    title = _('Field categories')

    def update(self):
        configlet = getUtility(IProfilesCategory)

        request = self.request

        if 'form.button.add' in request:
            categories = list(configlet.fieldCategories)
            cat = request.get('form.widget.category', '')

            if not cat:
                IStatusMessage(request).add(
                    _('Please enter category title.'), 'warning')
            elif cat in categories:
                IStatusMessage(request).add(
                    _('Category already exists.'), 'warning')
            else:
                categories.append(cat)
                configlet.fieldCategories = categories
                IStatusMessage(request).add(_('Category has been added.'))
                self.redirect('.')

        elif 'form.button.remove' in request:
            cats = request.get('form.widget.categories', ())
            if not cats:
                IStatusMessage(request).add(
                    _('Please select categories.'), 'warning')
            else:
                categories = list(configlet.fieldCategories)
                for cat in cats:
                    if cat in categories:
                        categories.remove(cat)

                configlet.fieldCategories = categories
                IStatusMessage(request).add(_('Category has been removed.'))
                self.redirect('.')

        elif 'form.button.moveup' in request or \
                'form.button.movedown' in request:
            cats = request.get('form.widget.categories', ())
            if not cats:
                IStatusMessage(request).add(
                    _('Please select categories.'), 'warning')
            else:
                sign = 'form.button.moveup' in request and -1 or 1
                categories = list(configlet.fieldCategories)
                for cat in cats:
                    if cat in categories:
                        ind = categories.index(cat)
                        categories.remove(cat)
                        categories.insert(ind + sign, cat)

                configlet.fieldCategories = categories
                IStatusMessage(request).add(_('Category has been moved.'))
                self.redirect('.')

        elif 'form.button.sort' in request:
            categories = list(configlet.fieldCategories)
            categories.sort()
            configlet.fieldCategories = categories
            IStatusMessage(request).add(_('Categories has been sorted.'))
            self.redirect('.')

        self.categories = configlet.fieldCategories
        super(FieldCategories, self).update()
