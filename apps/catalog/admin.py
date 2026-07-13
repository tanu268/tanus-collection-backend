from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name",)
    ordering = ("name",)
    fields = ("name", "slug", "image", "blurb")
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image_preview", "image", "is_primary")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" style="height: 60px;" />', obj.image.url)
        return "(no image yet)"
    image_preview.short_description = "Preview"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_code", "name", "category_list",
        "price", "quantity", "status", "is_featured",
    )
    list_filter = ("status", "categories", "fabric", "color", "is_featured")
    search_fields = ("product_code", "name")
    ordering = ("-created_at",)
    filter_horizontal = ("categories",)
    inlines = [ProductImageInline]
    actions = ["mark_as_hidden", "mark_as_published"]

    @admin.display(description="Categories")
    def category_list(self, obj):
        return ", ".join(c.name for c in obj.categories.all())

    @admin.action(description="Mark selected products as Hidden")
    def mark_as_hidden(self, request, queryset):
        count = 0
        for product in queryset:
            product.status = Product.Status.HIDDEN
            product.save()
            count += 1
        self.message_user(request, f"{count} product(s) marked as Hidden.")


    @admin.action(description="Mark selected products as Published")
    def mark_as_published(self, request, queryset):
        count = 0
        for product in queryset:
            product.status = Product.Status.PUBLISHED
            product.save()
            count += 1
        self.message_user(request, f"{count} product(s) marked as Published.")