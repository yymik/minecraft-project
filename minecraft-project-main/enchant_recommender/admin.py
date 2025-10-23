# enchant_recommender/admin.py
from django.contrib import admin
from .models import EnchantmentRecommendation

@admin.register(EnchantmentRecommendation)
class EnchantmentRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_type', 'created_at')
    list_filter = ('item_type', 'user')
    search_fields = ('user__username', 'item_type', 'memo')