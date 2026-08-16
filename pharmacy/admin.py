from django.contrib import admin
from .models import TransactionHeads, ItemManufacturers, ItemForms, ItemUnits, ItemCategories

@admin.register(TransactionHeads)
class TransactionHeadsAdmin(admin.ModelAdmin):
    list_display = ('id', 'tran_head_name', 'manufacturer', 'form', 'quantity', 'cp', 'mrp')
    search_fields = ('tran_head_name',)
    list_filter = ('manufacturer', 'form')

# Optional – only if you want to manage them in admin
admin.site.register(ItemManufacturers)
admin.site.register(ItemForms)
admin.site.register(ItemUnits)
admin.site.register(ItemCategories)
