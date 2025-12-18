from django.contrib import admin

from .models import Category, Manufacturer, Supplier, Product, UserProfile, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "manufacturer", "supplier", "price", "stock_quantity", "discount_percent")
    list_filter = ("category", "supplier", "manufacturer")
    search_fields = ("name", "description")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "role")
    list_filter = ("role",)
    search_fields = ("full_name", "user__username")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "created_at")
    list_filter = ("created_at",)
    search_fields = ("customer__username",)
    inlines = [OrderItemInline]


