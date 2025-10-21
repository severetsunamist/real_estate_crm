from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.html import format_html
import uuid

class Company(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def logo_preview(self):
        if self.logo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', self.logo.url)
        return "No Logo"

class Contact(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contacts')
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    is_primary = models.BooleanField(default=False)
    telegram_chat_id = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'is_primary'],
                condition=models.Q(is_primary=True),
                name='unique_primary_contact'
            )
        ]
        ordering = ['company', 'is_primary', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Object(models.Model):
    OBJECT_TYPES = [
        ('warehouse', '🏭 Склад'),
        ('other', '🔀 Другое'),
    ]
    
    STATUS_CHOICES = [
        ('active', '✅ Активно'),
        ('inactive', '❌ На стопе'),
        ('draft', '📝 Черновик'),
    ]
    
    CITY_CHOICES = [
        ('msk', 'Москва'),
        ('spb', 'Санкт-Петербург'),
    ]

    name = models.CharField(max_length=200)
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES, default='warehouse')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    city = models.CharField(max_length=15, choices=CITY_CHOICES, default='spb')
    address = models.CharField(max_length=100)
    owner = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='owned_objects')
    total_area = models.DecimalField(max_digits=10, decimal_places=2)
    floors = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    build_year = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Объект"
        verbose_name_plural = "Объекты"
    
    def __str__(self):
        return f"{self.get_object_type_display()} - {self.name}"
    
    @property
    def active_vacancies_count(self):
        return self.vacancies.filter(is_available=True).count()

class Vacancy(models.Model):
    VACANCY_TYPES = [
        ('entire_object', '🏢 Целиком'),
        ('unit', '📦 Блок'),
    ]
    
    OFFER_TYPES = [
        ('sale', '💰 Продажа'),
        ('lease', '📄 Аренда'),
        ('both', '💼 Аренда или Продажа'),
    ]
    
    FLOOR_TYPES = [
        ('concrete', 'Бетон'),
        ('tile', 'Плитка'),
        ('asphalt', 'Асфальт'),
        ('dustfree', 'Бетон-Антипыль'),
    ]
    
    UTILITY_TYPES = [
        ('municipal', 'Центральное'),
        ('private', 'Частное'),
        ('none', 'Нет'),
    ]
    
    object = models.ForeignKey(Object, on_delete=models.CASCADE, related_name='vacancies')
    vacancy_type = models.CharField(max_length=20, choices=VACANCY_TYPES)
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPES, default='lease')
    parent_vacancy = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_vacancies')
    title = models.CharField(max_length=200)
    contact_person = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Контакт")
    
    # Area specifications
    whs_area = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Площадь Склада (м²)")
    mez_area = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Площадь Мезонина (м²)")
    office_area = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Площадь Офиса (м²)")
    tech_area = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Тех. Площадь (м²)")
    
    # Pricing
    sale_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Цена продажи")
    lease_price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Ставка аренды")
    currency = models.CharField(max_length=3, default='RUB', verbose_name="Валюта")
    
    # Availability
    is_available = models.BooleanField(default=True, verbose_name="Готов к въезду")
    available_from = models.DateField(default=timezone.now, verbose_name="Готов к въезду с")
    

    # Technical specifications
    height = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="Высота потолка (м)")
    column_grid = models.CharField(max_length=50, blank=True, verbose_name="Шаг колонн (м)")
    floor_load = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name="Нагрузка на пол (т/м²)")
    floor_type = models.CharField(max_length=20, choices=FLOOR_TYPES, blank=True, verbose_name="Тип полов")
    docks_amount = models.IntegerField(default=0, verbose_name="Кол-во доков")
    
    # Fire safety
    fire_alarm = models.BooleanField(default=True, verbose_name="Пожарная сигнализация")
    sprinkler_system = models.BooleanField(default=True, verbose_name="Спринкленая сиатема пожаротушения")
    smoke_remove = models.BooleanField(default=True, verbose_name="Система дымоудаления")
    hydrants = models.BooleanField(default=False, verbose_name="Гидранты")
    special_fire_system = models.BooleanField(default=False, verbose_name="Особая система пожаротушения")
    
    # Utilities
    ventilation = models.BooleanField(default=False, verbose_name="Вентиляция")
    electricity = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Электрические мощности (кВт)")
    water = models.CharField(max_length=20, choices=UTILITY_TYPES, default='municipal', verbose_name="Водоснабжение")
    heating = models.CharField(max_length=20, choices=UTILITY_TYPES, default='municipal', verbose_name="Отопление")
    sew = models.CharField(max_length=20, choices=UTILITY_TYPES, default='municipal', verbose_name="Канализация")
    
    # Media
    floorplan_image = models.ImageField(upload_to='floorplans/', blank=True, null=True,  verbose_name="Планировка")
    
    
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")
    
    class Meta:
        verbose_name = "Предложение"
        verbose_name_plural = "Предложения"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.object.name}"
    
    @property
    def total_area(self):
        return self.whs_area + self.mez_area + self.office_area + self.tech_area

class ObjectImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object = models.ForeignKey(Object, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='object_images/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фото"
        ordering = ['order', 'uploaded_at']
    
    def image_preview(self):
        if self.image:
            return format_html(
                '<img src="{}" width="100" height="75" style="object-fit: cover; border-radius: 4px;" />', 
                self.image.url
            )
        return "No Image"
    
    def __str__(self):
        return f"Image for {self.object.name}"

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    telegram_chat_id = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Брокер"
        verbose_name_plural = "Брокеры"
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username