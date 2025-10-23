from django.contrib import admin
from django.utils.html import format_html
from .models import Company, Contact, Object, Vacancy, ObjectImage, Agent

class ObjectImageInline(admin.TabularInline):
    model = ObjectImage
    extra = 1
    fields = ['image_preview', 'image', 'caption', 'order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        return obj.image_preview()
    image_preview.short_description = 'Preview'

class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1
    fields = ['first_name', 'last_name', 'email', 'phone', 'is_primary']

class VacancyInline(admin.StackedInline):
    model = Vacancy
    extra = 0
    fields = ['title', 'vacancy_type', 'offer_type', 'is_available']

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['logo_preview', 'name', 'contacts_count', 'objects_count', 'created_at']
    list_display_links = ['name']
    search_fields = ['name', 'description']
    inlines = [ContactInline]
    
    def logo_preview(self, obj):
        return obj.logo_preview
    logo_preview.short_description = 'Logo'
    
    def contacts_count(self, obj):
        return obj.contacts.count()
    contacts_count.short_description = 'Contacts'
    
    def objects_count(self, obj):
        return obj.owned_objects.count()
    objects_count.short_description = 'Objects'

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'company', 'email', 'phone', 'is_primary']
    list_filter = ['company', 'is_primary']
    search_fields = ['first_name', 'last_name', 'email']

@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'object_type', 'city', 'total_area', 'status', 'created_at']
    list_filter = ['object_type', 'city', 'status']
    search_fields = ['name', 'address', 'city']
    inlines = [ObjectImageInline, VacancyInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'object_type', 'status')
        }),
        ('Location', {
            'fields': ('address', 'city', 'latitude', 'longitude')
        }),
        ('Specifications', {
            'fields': ('owner', 'total_area', 'floors', 'build_year')
        }),
    )

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'object', 'vacancy_type', 'offer_type', 'is_available', 'created_at']
    list_filter = ['vacancy_type', 'offer_type', 'is_available']
    search_fields = ['title', 'object__name']

@admin.register(ObjectImage)
class ObjectImageAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'object', 'caption', 'order']
    list_editable = ['caption', 'order']
    list_filter = ['object']
    
    def image_preview(self, obj):
        return obj.image_preview()
    image_preview.short_description = 'Preview'

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'is_active']
    list_filter = ['company', 'is_active']