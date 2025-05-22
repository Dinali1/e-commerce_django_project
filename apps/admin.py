from django.contrib import admin
from django.contrib.auth.models import User, Group

from apps.models import *

# Register your models here.


admin.site.unregister(Group)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    exclude = ('slug',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'description',  'category', 'reviews')
    exclude = ('slug',)

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('name', 'username_telegram')


    
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    
@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    pass

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_established', 'product')
    

    
    
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('balance', 'review', 'status', 'created_at', 'payment_id')


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('username', )

@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = ('description', 'stream', 'created_at')



    
    


    
    
    









