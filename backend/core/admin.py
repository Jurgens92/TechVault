from django.contrib import admin
from .models import (
    Organization, Location, Contact, Documentation,
    PasswordEntry, Configuration,
    DocumentationVersion, PasswordEntryVersion, ConfigurationVersion
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'country']
    search_fields = ['name', 'email', 'description']
    readonly_fields = ['id', 'created_by', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'name', 'description', 'is_active')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state_province', 'postal_code', 'country')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'city', 'is_active', 'created_at']
    list_filter = ['organization', 'is_active', 'country', 'created_at']
    search_fields = ['name', 'city', 'address']
    readonly_fields = ['id', 'created_by', 'created_at', 'updated_at']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'organization', 'email', 'is_active', 'created_at']
    list_filter = ['organization', 'is_active', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']
    readonly_fields = ['id', 'created_by', 'created_at', 'updated_at', 'full_name']


@admin.register(Documentation)
class DocumentationAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization', 'category', 'is_published', 'created_at']
    list_filter = ['organization', 'category', 'is_published', 'created_at']
    search_fields = ['title', 'content', 'tags']
    readonly_fields = ['id', 'created_by', 'created_at', 'updated_at']


@admin.register(PasswordEntry)
class PasswordEntryAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'category', 'username', 'created_at']
    list_filter = ['organization', 'category', 'created_at']
    search_fields = ['name', 'username', 'url']
    readonly_fields = ['id', 'created_by', 'created_at', 'updated_at']


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'config_type', 'is_active', 'created_at']
    list_filter = ['organization', 'config_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_by', 'created_at', 'updated_at']


# Version History Admin
@admin.register(DocumentationVersion)
class DocumentationVersionAdmin(admin.ModelAdmin):
    list_display = ['documentation', 'version_number', 'title', 'created_at', 'created_by']
    list_filter = ['created_at', 'is_published']
    search_fields = ['title', 'content', 'change_note']
    readonly_fields = ['id', 'created_at', 'created_by']
    ordering = ['-created_at']


@admin.register(PasswordEntryVersion)
class PasswordEntryVersionAdmin(admin.ModelAdmin):
    list_display = ['password_entry', 'version_number', 'name', 'created_at', 'created_by']
    list_filter = ['created_at', 'category']
    search_fields = ['name', 'username', 'change_note']
    readonly_fields = ['id', 'created_at', 'created_by']
    ordering = ['-created_at']


@admin.register(ConfigurationVersion)
class ConfigurationVersionAdmin(admin.ModelAdmin):
    list_display = ['configuration', 'version_number', 'name', 'config_type', 'created_at', 'created_by']
    list_filter = ['created_at', 'config_type', 'is_active']
    search_fields = ['name', 'content', 'change_note']
    readonly_fields = ['id', 'created_at', 'created_by']
    ordering = ['-created_at']
