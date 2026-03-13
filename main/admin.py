from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created']
    prepopulated_fields = {'slug': ('name',)}  
    search_fields = ['name']
    ordering = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'category', 
        'price', 
        'quantity', 
        'available', 
        'created'
    ]
    list_filter = ['category', 'available', 'created'] 
    search_fields = ['name', 'description'] 
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created'  
    list_editable = ['available', 'quantity']  
    readonly_fields = ['created', 'updated']  
    
    fieldsets = (
        ('Основное', {
            'fields': ('category', 'name', 'slug', 'symbol')
        }),
        ('Описание', {
            'fields': ('short_description', 'description'),
            'classes': ('collapse',) 
        }),
        ('Цена и наличие', {
            'fields': ('price', 'quantity', 'available')
        }),
        ('Медиа', {
            'fields': ('image',),
        }),
        ('Мета', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category')  