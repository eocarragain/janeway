__copyright__ = "Copyright 2017 Birkbeck, University of London"
__author__ = "Martin Paul Eve & Andy Byers"
__license__ = "AGPL v3"
__maintainer__ = "Birkbeck Centre for Technology and Publishing"
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from hvad.admin import TranslatableAdmin

from core import models


class SettingAdmin(admin.ModelAdmin):
    """Displays Setting objects in the Django admin interface."""
    list_display = ('name', 'group', 'types')
    list_filter = ('group', 'types')


class AccountAdmin(UserAdmin):
    """Displays Account objects in the Django admin interface."""
    list_display = ('username', 'email', 'first_name', 'middle_name', 'last_name', 'institution', 'date_confirmed')
    search_fields = ('username', 'email', 'first_name', 'middle_name', 'last_name', 'orcid', 'institution', 'biography')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': (
            'middle_name', 'orcid', 'institution', 'department', 'twitter', 'linkedin', 'facebook', 'github',
            'biography',
            'signature', 'profile_image', 'interest')}),
    )


class RoleAdmin(admin.ModelAdmin):
    """Displays Role objects in the Django admin interface."""
    list_display = ('name',)
    search_fields = ('name',)


class PasswordResetAdmin(admin.ModelAdmin):
    """Displays Password Reset Data"""
    list_display = ('account', 'expiry', 'expired')
    search_fields = ('account',)
    list_filter = ('expired',)


class SettingValueAdmin(TranslatableAdmin):
    pass


class CountryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('name', 'code')


class HomepageElementAdmin(admin.ModelAdmin):
    """Displays Setting objects in the Django admin interface."""
    list_display = ('name', 'object', 'sequence')
    list_filter = ('name',)
    search_fields = ('name',)


admin_list = [
    (models.Account, AccountAdmin),
    (models.Role, RoleAdmin,),
    (models.Setting, SettingAdmin),
    (models.SettingGroup,),
    (models.SettingValue, SettingValueAdmin),
    (models.File,),
    (models.AccountRole,),
    (models.Interest,),
    (models.Task,),
    (models.TaskCompleteEvents,),
    (models.Galley,),
    (models.EditorialGroup,),
    (models.EditorialGroupMember,),
    (models.PasswordResetToken, PasswordResetAdmin),
    (models.OrcidToken,),
    (models.DomainAlias,),
    (models.Country, CountryAdmin),
    (models.WorkflowElement,),
    (models.HomepageElement, HomepageElementAdmin),
]

[admin.site.register(*t) for t in admin_list]
