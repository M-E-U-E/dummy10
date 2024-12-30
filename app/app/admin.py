from django.contrib import admin
from .models import Property, Summary

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('property_name', 'city_name', 'price', 'rating')
    search_fields = ('property_name', 'city_name')

@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ('property', 'description')
    search_fields = ('property__property_name',)
