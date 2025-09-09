from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, MenuItem, Order, OrderItem, KOT, WalletTransaction

# Unregister default User admin if needed
# admin.site.unregister(User)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'wallet_balance', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Canteen Info', {
            'fields': ('user_type', 'pin', 'wallet_balance', 'qr_code')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'user_type', 'pin', 'password1', 'password2'),
        }),
    )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)} if hasattr(Category, 'slug') else {}

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'available')
    list_filter = ('category', 'available')
    search_fields = ('name', 'description')
    list_editable = ('price', 'available')
    raw_id_fields = ('category',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('menu_item',)
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_date', 'total_amount', 'completed')
    list_filter = ('completed', 'order_date')
    search_fields = ('user__username', 'id')
    date_hierarchy = 'order_date'
    inlines = (OrderItemInline,)
    readonly_fields = ('order_date',)

class KOTAdmin(admin.ModelAdmin):
    list_display = ('kot_number', 'order', 'generated_at', 'served', 'served_at')
    list_filter = ('served', 'generated_at')
    search_fields = ('kot_number', 'order__id')
    date_hierarchy = 'generated_at'
    readonly_fields = ('generated_at',)

class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_type', 'transaction_date', 'reference')
    list_filter = ('transaction_type', 'transaction_date')
    search_fields = ('user__username', 'reference')
    date_hierarchy = 'transaction_date'
    readonly_fields = ('transaction_date',)

# Register models with custom admin classes
admin.site.register(User, CustomUserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(KOT, KOTAdmin)
admin.site.register(WalletTransaction, WalletTransactionAdmin)

# Optional admin site customization
admin.site.site_header = "Smart Canteen System Administration"
admin.site.site_title = "Smart Canteen Admin"
admin.site.index_title = "Welcome to Smart Canteen Admin"
