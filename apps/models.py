from enum import EnumType

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models
from django.db.models import Model, ImageField, CharField, DecimalField, SmallIntegerField, TextField, ForeignKey, \
    DateTimeField, CASCADE, BooleanField, EmailField, TextChoices, FileField, IntegerField, SlugField, \
    PositiveIntegerField
from django.utils.text import slugify


# Create your models here.

class BaseSlug(Model):
    class Meta:
        abstract = True

    name = CharField(max_length=255)
    slug = SlugField(unique=True)

    def save(self, *args, **kwargs):
        slug = slugify(self.name)
        if self.__class__.objects.filter(slug=slug).exists():
            slug_count = self.__class__.objects.filter(slug__startswith=slug).count()
            self.slug = slug + f"-{int(slug_count) + 1}"
        else:
            self.slug = slug
        super().save(*args, **kwargs)


class Category(BaseSlug):
    class Meta:
        verbose_name_plural = 'categories'
    image = ImageField(upload_to='categories', null=True, blank=True)
    name = CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(BaseSlug):
    main_image = ImageField(upload_to='products', null=True, blank=True)
    name = CharField(max_length=255)
    price = DecimalField(max_digits=10, decimal_places=2)
    quantity = SmallIntegerField(default=0)
    description = TextField()
    reviews = TextField()
    seller_price = DecimalField(max_digits=10, decimal_places=2)
    order_count = PositiveIntegerField(default=0)
    video = FileField(upload_to='products', null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    discount_price = DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    attribute_id = ForeignKey('apps.Attribute', on_delete=CASCADE, related_name='products')
    seller_id = ForeignKey('apps.Seller', on_delete=CASCADE, related_name='products')
    category = ForeignKey('apps.Category', on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name


class Attribute(Model):
    name = CharField(max_length=255)

    def __str__(self):
        return self.name

class Seller(Model):
    name = CharField(max_length=255)
    username_telegram = CharField(max_length=255)


class Tag(Model):
    name = CharField(max_length=255)

class ProductTag(Model):
    tag = ForeignKey('apps.Tag', on_delete=CASCADE, related_name='product_tgs')
    product = ForeignKey('apps.Product', on_delete=CASCADE, related_name='product_tags')

class Option(Model):
    name = CharField(max_length=255)
    attribute = ForeignKey('apps.Attribute', on_delete=CASCADE, related_name='options')

class ProductImage(Model):
    image = ImageField(upload_to='product_images', null=True, blank=True)
    product = ForeignKey('apps.Product', on_delete=CASCADE, related_name='images')



class Region(Model):
    name = CharField(max_length=255)
    order_count = PositiveIntegerField(default=0)

class District(Model):
    name = CharField(max_length=255)
    region = ForeignKey('apps.Region', on_delete=CASCADE, related_name='districts')


class CustomerUser(UserManager):
    def _create_user_object(self,email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        return user

    def create_user(self,email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user( email, password, **extra_fields)

    def create_superuser(self,email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def _create_user(self, email, password, **extra_fields):
        user = self._create_user_object(email, password, **extra_fields)
        user.save(using=self._db)
        return user

class User(AbstractUser):
    email = EmailField(max_length=255, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomerUser()
    username = None
    phone_number = CharField(max_length=20, null=True, blank=True)
    district = ForeignKey('apps.District', on_delete=CASCADE, related_name='users', null=True, blank=True)
    image = ImageField(upload_to='users', null=True, blank=True)
    balance = DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

class Stream(Model):
    name = CharField(max_length=255)
    is_established = BooleanField(default=False)
    visit_count = PositiveIntegerField(default=0)
    product = ForeignKey('apps.Product', on_delete=CASCADE, related_name='streams')
    user = ForeignKey('apps.User', on_delete=CASCADE, related_name='streams')
    created_at = DateTimeField(auto_now_add=True)




class Transaction(Model):
    class StatusType(TextChoices):
        PENDING = 'pending', 'Pending',
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
    balance = DecimalField(max_digits=10, decimal_places=2)
    review = TextField()
    status = CharField(max_length=255, choices=StatusType, default=StatusType.PENDING)
    created_at = DateTimeField(auto_now_add=True)
    payment_id = ForeignKey('apps.Payment', on_delete=CASCADE, related_name='transactions')

class Account(Model):
    image = ImageField(upload_to='accounts', null=True, blank=True)
    username = CharField(max_length=255)
    user = ForeignKey('apps.User', on_delete=CASCADE, related_name='accounts')
    district = ForeignKey('apps.District', on_delete=CASCADE, related_name='accounts')
    first_name = CharField(max_length=255, default="Name")
    last_name = CharField(max_length=255, default="Surname")

class Query(Model):
    class StatusType(TextChoices):
        POSITIVE = 'positive', 'Positive',
        NEGATIVE = 'negative', 'Negative',
    description = TextField()
    status = CharField(max_length=255, choices=StatusType, default=StatusType.POSITIVE)
    created_at = DateTimeField(auto_now_add=True)
    stream = ForeignKey('apps.Stream', on_delete=CASCADE, related_name='queries')


class Order(Model):
    class StatusType(TextChoices):
        NEW = 'new', 'New'
        ACCEPTED = 'accepted', 'Accepted'
        DELIVERING = 'delivering', 'Delivering'
        DELIVERED = 'delivered', 'Delivered'
        RETURNED = 'returned', 'Returned'
        HOLD = 'hold', 'Hold'
        ARCHIVED = 'archived', 'Archived'
    name = CharField(max_length=255)
    phone_number = CharField(max_length=255)
    status = CharField(max_length=255, choices=StatusType, default=StatusType.NEW)
    created_at = DateTimeField(auto_now_add=True)
    stream = ForeignKey('apps.Stream', on_delete=CASCADE, related_name='orders', null=True, blank=True)
    product = ForeignKey('apps.Product', on_delete=CASCADE, related_name='orders')
    user = ForeignKey('apps.User', on_delete=CASCADE, related_name='orders')
    region = ForeignKey('apps.Region', on_delete=CASCADE, related_name='orders')
    total = DecimalField(max_digits=10, decimal_places=2)
    quantity = IntegerField(default=1)

class Payment(Model):
    class StatusType(TextChoices):
        CANCELED = 'canceled', 'Canceled'
        UNDER_VIEW = 'under view', 'Under View'
        COMPLETED = 'completed', 'Completed'
    card_number = CharField(max_length=255)
    payment_status = CharField(choices=StatusType, default=StatusType.UNDER_VIEW)
    message = TextField(null=True, blank=True)
    receipt = ImageField(upload_to='payments', null=True, blank=True)
    user = ForeignKey('apps.User', on_delete=CASCADE, related_name='payments')
    amount = DecimalField(max_digits=10, decimal_places=2)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.card_number

class Charity(Model):
    description = TextField()
    seller = ForeignKey('apps.Seller', on_delete=CASCADE, related_name='charities')
    amount = DecimalField(max_digits=10, decimal_places=2)

class Delivery(Model):
    name = CharField(max_length=255)
    price = DecimalField(max_digits=10, decimal_places=2)
    description = TextField()
    delivery_time = DateTimeField()
    phone_number = CharField(max_length=255)

class Post(Model):
    name = CharField(max_length=255)
    description = TextField()
    image = ImageField(upload_to='posts', null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)

class Settings(Model):
    phone_number = CharField(max_length=255)
    telegram_link = CharField(max_length=255)
    delivery_price = DecimalField(max_digits=10, decimal_places=2)

class Penalty(Model):
    name = CharField(max_length=255)
    amount = DecimalField(max_digits=10, decimal_places=2)
    description = TextField()
    response = TextField()
    user = ForeignKey('apps.User', on_delete=CASCADE, related_name='penalties')













