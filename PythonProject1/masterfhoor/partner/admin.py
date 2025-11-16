from django.contrib import admin
from .models import *


@admin.register(PartnerType)
class PartnerTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'partner_type', 'rating', 'phone', 'email']
    list_filter = ['partner_type', 'rating']
    search_fields = ['name', 'inn', 'director_name']
    readonly_fields = ['calculate_discount_display']

    def calculate_discount_display(self, obj):
        return f"{obj.calculate_discount()}%"

    calculate_discount_display.short_description = "Текущая скидка"


@admin.register(SalesHistory)
class SalesHistoryAdmin(admin.ModelAdmin):
    list_display = ['partner', 'product', 'quantity', 'sale_date']
    list_filter = ['sale_date', 'partner']
    date_hierarchy = 'sale_date'


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'coefficient']


@admin.register(MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'defect_percentage']


admin.site.register(Product)
admin.site.register(Material)
admin.site.register(Recipe)