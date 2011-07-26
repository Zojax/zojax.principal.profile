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
from zope import interface
from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds
from zope.app.component.hooks import getSite, setSite
from zope.app.component.interfaces import ISite
from zope.security.management import getInteraction
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.traversing.api import getParents, getPath

from zojax.preferences.interfaces import IPreferenceGroup

from interfaces import IAvatarConfiglet
from interfaces import IProfileFields, IProfilesCategory, IPersonalProfile


class Vocabulary(SimpleVocabulary):

    def getTerm(self, value):
        try:
            return super(Vocabulary, self).getTerm(value)
        except LookupError:
            return super(Vocabulary, self).getTerm(self.by_value.keys()[0])


class ProfileFieldsVocabulary(object):
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        ids = getUtility(IIntIds)
        site = getSite()
        try:
            for i in [site] + getParents(site):
                if not ISite.providedBy(i):
                    continue
                setSite(i)
                fields = getUtility(IProfileFields)
                for name, field in fields.items():
                    id  = ids.getId(field)
                    path = getPath(i)[1:]
                    if path:
                        path += '/'
                    terms.append((path+field.title, id))

            terms.sort()
            return Vocabulary(
                [SimpleTerm(name, name, title) for title, name in terms])
        finally:
            setSite(site)


class CategoriesVocabulary(object):
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        configlet = getUtility(IProfilesCategory)

        for category in configlet.fieldCategories:
            terms.append(category)

        terms.sort()
        return SimpleVocabulary(
            [SimpleTerm(name, name, name) for name in terms])


class AvatarsVocabulary(object):
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        configlet = getUtility(IAvatarConfiglet)

        request = None
        for part in getInteraction().participations:
            if part is not None:
                request = part
                break

        if context is not None:
            profile = context
            if profile.avatarImage:
                terms.append(SimpleTerm(0, '0', '0'))
        elif request is not None:
            profile = profile = IPersonalProfile(request.principal)
            if profile.avatarImage:
                terms.append(SimpleTerm(0, '0', '0'))

        if configlet.enabled:
            ids = getUtility(IIntIds)

            for name, avatar in configlet.items():
                id = ids.queryId(avatar)
                terms.append(SimpleTerm(id, str(id), str(id)))
        return Vocabulary(terms)


class PrefsAvatarsVocabulary(object):
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        if isinstance(context, dict):
            context = context.get('context')

        while not IPreferenceGroup.providedBy(context):
            context = context.__parent__
            if context is None:
                return Vocabulary(())

        terms = []
        configlet = getUtility(IAvatarConfiglet)

        principal = context.__principal__
        profile = IPersonalProfile(principal)
        if profile.avatarImage:
            terms.append(SimpleTerm(0, '0', '0'))

        if configlet.enabled:
            ids = getUtility(IIntIds)

            for name, avatar in configlet.items():
                id = ids.queryId(avatar)
                terms.append(SimpleTerm(id, str(id), str(id)))

        return Vocabulary(terms)


class GlobalAvatarsVocabulary(object):
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        terms = []
        ids = getUtility(IIntIds)
        configlet = getUtility(IAvatarConfiglet)

        for name, avatar in configlet.items():
            id = ids.queryId(avatar)
            terms.append(SimpleTerm(id, str(id), str(id)))

        return Vocabulary(terms)
