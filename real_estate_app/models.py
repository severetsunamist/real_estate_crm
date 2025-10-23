from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
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
        verbose_name_plural = "Companies"
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
        ('warehouse', '🏭 Warehouse'),
        ('office', '🏢 Office'),
        ('retail', '🛍️ Retail'),
        ('industrial', '🏗️ Industrial'),
        ('mixed', '🔀 Mixed Use'),
    ]
    
    STATUS_CHOICES = [
        ('active', '✅ Active'),
        ('inactive', '❌ Inactive'),
        ('draft', '📝 Draft'),
        ('sold', '💰 Sold'),
        ('leased', '📄 Leased'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    address = models.TextField()
    city = models.CharField(max_length=100)
    
    # Location fields (latitude/longitude instead of PostGIS)
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    
    owner = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='owned_objects')
    total_area = models.DecimalField(max_digits=10, decimal_places=2)
    floors = models.IntegerField(validators=[MinValueValidator(1)], default=1)
    build_year = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Property Object"
    
    def __str__(self):
        return f"{self.get_object_type_display()} - {self.name}"
    
    @property
    def active_vacancies_count(self):
        return self.vacancies.filter(is_available=True).count()
    
    @property
    def coordinates(self):
        if self.latitude and self.longitude:
            return f"{self.latitude}, {self.longitude}"
        return "Not set"

class Vacancy(models.Model):
    VACANCY_TYPES = [
        ('entire_object', '🏢 Entire Object'),
        ('unit', '📦 Unit'),
        ('floor', '🏢 Floor'),
    ]
    
    OFFER_TYPES = [
        ('sale', '💰 Sale'),
        ('lease', '📄 Lease'),
        ('both', '💼 Sale & Lease'),
    ]
    
    object = models.ForeignKey(Object, on_delete=models.CASCADE, related_name='vacancies')
    vacancy_type = models.CharField(max_length=20, choices=VACANCY_TYPES)
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPES, default='lease')
    parent_vacancy = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_vacancies')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Area specifications
    whs_area = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mez_area = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    office_area = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tech_area = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Technical specifications
    height = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    floor_load = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    docks_amount = models.IntegerField(default=0)
    
    # Pricing
    sale_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    lease_price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='RUB')
    
    # Availability
    available_from = models.DateField(default=timezone.now)
    is_available = models.BooleanField(default=True)
    contact_person = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Vacancies"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.object.name}"
    
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object = models.ForeignKey(Object, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='object_images/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
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
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username