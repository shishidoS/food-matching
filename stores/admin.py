from django.contrib import admin
from django.utils.html import format_html
from .models import PostFood, PostTags, PostTagging

@admin.register(PostTags)
class PostTagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_display', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    list_filter = ('created_at',)
    
    def color_display(self, obj):
        """タグカラーを視覚的に表示"""
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'カラー'

@admin.register(PostFood)
class PostFoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity_display', 'use_date', 'store_account', 'is_active', 'created_at')
    list_filter = ('is_active', 'use_date', 'unit', 'created_at', 'tags', 'store_account')
    search_fields = ('name', 'description', 'store_account__username')
    filter_horizontal = ('tags',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    date_hierarchy = 'use_date'
    
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'description', 'image')
        }),
        ('数量・期限', {
            'fields': ('quantity', 'unit', 'use_date')
        }),
        ('タグ', {
            'fields': ('tags',),
            'classes': ('wide',)
        }),
        ('システム情報', {
            'fields': ('store_account', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def quantity_display(self, obj):
        """数量と単位を組み合わせて表示"""
        return f"{obj.quantity}{obj.unit}"
    quantity_display.short_description = '数量'
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新規作成の場合
            obj.store_account = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """管理者は全ての食材を、一般ユーザーは自分の食材のみを表示"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(store_account=request.user)

@admin.register(PostTagging)
class PostTaggingAdmin(admin.ModelAdmin):
    list_display = ('food', 'tag', 'created_at')
    list_filter = ('tag', 'created_at')
    search_fields = ('food__name', 'tag__name')
    ordering = ('-created_at',)