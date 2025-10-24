from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.html import format_html
import uuid

class Company(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True, verbose_name="Логотип")
    website = models.URLField(blank=True, verbose_name="Веб-сайт")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
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
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contacts', verbose_name="Компания")
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    is_primary = models.BooleanField(default=False, verbose_name="Основной контакт")
    telegram_chat_id = models.CharField(max_length=50, blank=True, verbose_name="Telegram Chat ID")
    
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
        ('industrial', '🏭 Промышленный'),
        ('office', '🏢 Офис'),
        ('retail', '🛍️ Торговый'),
    ]
    
    STATUS_CHOICES = [
        ('active', '✅ Активный'),
        ('inactive', '❌ Неактивный'),
        ('exclusive', '❤️ Эксклюзив'),
        ('secret', '⭐ Секретно'),
        ('draft', '📝 Черновик'),
        ('sold', '💰 Продан'),
        ('leased', '📄 Сдан в аренду'),
    ]
    
    REGION_CHOICES = [
        ('Москва', 'Москва'),
        ('Санкт-Петербург', 'Санкт-Петербург'),
        ('Казань', 'Казань'),
        ('Екатеринбург', 'Екатеринбург'),
        ('Новосибирск', 'Новосибирск'),
        ('Ростов-на-Дону', 'Ростов-на-Дону'),
        ('Самара', 'Самара'),
        ('Пермь', 'Пермь'),
        ('Уфа', 'Уфа'),
        ('Красноярск', 'Красноярск'),
        ('Нижний Новгород', 'Нижний Новгород'),
        ('Тюмень', 'Тюмень'),
        ('Хабаровск', 'Хабаровск'),
        ('Владивосток', 'Владивосток'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES, verbose_name="Тип объекта")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    address = models.CharField(max_length=200, verbose_name="Адрес")
    city = models.CharField(max_length=100, choices=REGION_CHOICES, default='Москва', verbose_name="Город")
    
    # Location fields
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        verbose_name="Широта"
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        verbose_name="Долгота"
    )
    
    owner = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='owned_objects', verbose_name="Владелец")
    total_area = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая площадь")
    floors = models.IntegerField(validators=[MinValueValidator(1)], default=1, verbose_name="Этажи")
    build_year = models.IntegerField(null=True, blank=True, verbose_name="Год постройки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    # Default vacancy type for this object
    default_vacancy_type = models.CharField(
        max_length=20, 
        choices=[
            ('entire_object', '🏢 Весь объект'),
            ('unit', '📦 Помещение'),
            ('floor', '🏢 Этаж'),
        ],
        default='unit',
        verbose_name="Тип предложения по умолчанию"
    )
    
    class Meta:
        verbose_name = "Объект"
        verbose_name_plural = "Объекты"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_object_type_display()} - {self.name}"
    
    @property
    def active_offers_count(self):
        return self.offers.filter(is_available=True).count()
    
    @property
    def coordinates(self):
        if self.latitude and self.longitude:
            return f"{self.latitude}, {self.longitude}"
        return "Not set"

class Offer(models.Model):
    VACANCY_TYPES = [
        ('entire_object', '🏢 Весь объект'),
        ('unit', '📦 Помещение'),
        ('floor', '🏢 Этаж'),
    ]
    
    OFFER_TYPES = [
        ('sale', '💰 Продажа'),
        ('lease', '📄 Аренда'),
        ('both', '💼 Продажа и Аренда'),
    ]

    CG_TYPES = [
        ('12x24', '12x24'),
        ('12x18', '12x18'),
        ('18x24', '18x24'),
        ('9x9', '9x9'),
        ('6x6', '6x6'),
        ('6x9', '6x9'),
        ('9x18', '9x18'),
        ('9x12', '9x12'),
        ('another', 'другой'),
    ]
    
    object = models.ForeignKey(Object, on_delete=models.CASCADE, related_name='offers', verbose_name="Объект")
    parent_offer = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_offers', verbose_name="Родительское предложение")
    vacancy_type = models.CharField(max_length=20, choices=VACANCY_TYPES, default='unit', verbose_name="Тип предложения")
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPES, default='lease', verbose_name="Тип предложения")
    
    # Availability
    available_from = models.DateField(default=timezone.now, verbose_name="Доступно с")
    is_available = models.BooleanField(default=True, verbose_name="Доступно")
    owner_company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Собственник")
    contact_person = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Контактное лицо")
    
    # Area specifications
    whs_area = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Складская площадь")
    mez_area = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Мезонин площадь")
    office_area = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Офисная площадь")
    tech_area = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Техническая площадь")
    
    # Lease prices
    whs_lease_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Ставка аренды Склад, руб/м²/год")
    mez_lease_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Ставка аренды Мезонин, руб/м²/год")
    office_lease_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Ставка аренды Офис, руб/м²/год")
    tech_lease_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Ставка аренды Тех, руб/м²/год")
    
    # Sale price
    sale_price = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Цена продажи, руб")
   

    # Technical specifications (not required)
    height = models.DecimalField(max_digits=4, decimal_places=2, default=12, blank=True, verbose_name="Высота, м")
    column_grid = models.CharField(max_length=7, choices=CG_TYPES, default='12x24', blank=True, verbose_name="Шаг колонн, м")
    floor_load = models.DecimalField(max_digits=3, decimal_places=1, default=6, blank=True, verbose_name="Нагрузка на пол, т/м²")
    docks_amount = models.IntegerField(default=0, blank=True, verbose_name="Количество доков")
    ramp = models.BooleanField(default=False, blank=True, verbose_name="Есть рампа")
    racks = models.BooleanField(default=False, blank=True, verbose_name="Установлены стеллажи")
    multitemp = models.BooleanField(default=False, blank=True, verbose_name="Мультитемпературный склад")
    
    title = models.CharField(max_length=50, blank=True, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Предложение"
        verbose_name_plural = "Предложения"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.total_area}"
    
    @property
    def total_area(self):
        return self.whs_area + self.mez_area + self.office_area + self.tech_area
    
    @property
    def price_display(self):
        if self.offer_type == 'sale' and self.sale_price:
            return f"${self.sale_price:,.2f}"
        elif self.offer_type == 'lease' and self.lease_price_per_sqm:
            return f"${self.lease_price_per_sqm}/m²"
        elif self.offer_type == 'both':
            prices = []
            if self.sale_price:
                prices.append(f"Sale: ${self.sale_price:,.2f}")
            if self.lease_price_per_sqm:
                prices.append(f"Lease: ${self.lease_price_per_sqm}/m²")
            return " | ".join(prices)
        return "Price not set"

class ObjectImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID")
    object = models.ForeignKey(Object, on_delete=models.CASCADE, related_name='images', verbose_name="Объект")
    image = models.ImageField(upload_to='object_images/', verbose_name="Фото")
    caption = models.CharField(max_length=200, blank=True, verbose_name="Подпись")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Компания")
    telegram_id = models.CharField(max_length=50, blank=True, verbose_name="Telegram ID")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    
    class Meta:
        verbose_name = "Агент"
        verbose_name_plural = "Агенты"
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username