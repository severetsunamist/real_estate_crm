from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Company, Contact, Object, Offer, ObjectImage, Agent

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    fieldsets = [
        (_('Основная информация'), {
            'fields': ['name', 'description', 'logo', 'website']
        }),
        (_('Дополнительная информация'), {
            'fields': ['created_at'],
            'classes': ['collapse']
        }),
    ]
    list_display = ['name', 'logo_preview', 'website']
    readonly_fields = ['created_at', 'logo_preview']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    fieldsets = [
        (_('Основная информация'), {
            'fields': ['first_name', 'last_name', 'email', 'phone']
        }),
        (_('Работа и связь'), {
            'fields': ['company', 'user', 'is_primary', 'telegram_chat_id']
        }),
    ]
    list_display = ['first_name', 'last_name', 'email', 'company', 'is_primary']
    list_filter = ['company', 'is_primary']

@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    fieldsets = [
        (_('Основная информация'), {
            'fields': ['name', 'description', 'object_type', 'status', 'default_vacancy_type']
        }),
        (_('Местоположение'), {
            'fields': ['address', 'city', 'latitude', 'longitude']
        }),
        (_('Характеристики объекта'), {
            'fields': ['owner', 'total_area', 'floors', 'build_year']
        }),
        (_('Даты'), {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    list_display = ['name', 'object_type', 'status', 'city', 'owner', 'total_area', 'active_offers_count']
    list_filter = ['object_type', 'status', 'city', 'owner']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    fieldsets = [
        (_('Основная информация'), {
            'fields': ['object', 'parent_offer', 'vacancy_type', 'offer_type','available_from', 'is_available','owner_company', 'contact_person']
        }),
        (_('Площади помещений'), {
            'fields': [
                'total_area_display',  # ← Add calculated field here
                'whs_area', 
                'mez_area', 
                'office_area', 
                'tech_area'
            ]
        }),
        (_('Ставки аренды (руб/м²/год)'), {
            'fields': ['whs_lease_price', 'mez_lease_price', 'office_lease_price', 'tech_lease_price']
        }),
        (_('Цена продажи'), {
            'fields': ['sale_price']
        }),
        (_('Технические характеристики'), {
            'fields': [
                'height', 
                'column_grid', 
                'floor_load', 
                'docks_amount', 
                'ramp', 
                'racks', 
                'multitemp'
            ]
        }),
        (_('Для агрегаторов'), {
            'fields':['title', 'description'],
            'classes': ['collapse']
        }),
        (_('Даты'), {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]

    list_display = ['total_area_display', 'object', 'offer_type', 'is_available', 'whs_area','mez_area','office_area', 'whs_lease_price', 'mez_lease_price', 'office_lease_price', 'sale_price']
    list_filter = ['offer_type', 'vacancy_type', 'is_available', 'object']
    readonly_fields = ['created_at', 'updated_at', 'total_area_display']  # ← Add to readonly fields

    # Add this method to display the calculated total area
    def total_area_display(self, obj):
        if obj.pk:  # Only if object exists in database
            return f"{obj.total_area} м²"
        return "Общая площадь: (сохраните для расчета)"
    total_area_display.short_description = "Общая площадь"

@admin.register(ObjectImage)
class ObjectImageAdmin(admin.ModelAdmin):
    fieldsets = [
        (_('Основная информация'), {
            'fields': ['object', 'image', 'caption', 'order']
        }),
        (_('Предпросмотр'), {
            'fields': ['image_preview'],
            'classes': ['collapse']
        }),
        (_('Даты'), {
            'fields': ['uploaded_at'],
            'classes': ['collapse']
        }),
    ]
    list_display = ['object', 'image_preview', 'caption', 'order']
    list_filter = ['object']
    readonly_fields = ['uploaded_at', 'image_preview']

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    fieldsets = [
        (_('Основная информация'), {
            'fields': ['user', 'company', 'is_active']
        }),
        (_('Telegram интеграция'), {
            'fields': ['telegram_id'],
            'classes': ['collapse']
        }),
    ]
    list_display = ['user', 'company', 'is_active']
    list_filter = ['company', 'is_active']

# Admin site headers
admin.site.site_header = _("Администрирование CRM Недвижимости")
admin.site.site_title = _("CRM Недвижимости")
admin.site.index_title = _("Панель управления")