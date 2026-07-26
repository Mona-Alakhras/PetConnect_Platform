from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
 
from .models import AdoptionRequest, Pet, PetImage, User
 
 
class PetImageInline(admin.TabularInline):
    model = PetImage
    extra = 1
    readonly_fields = ('preview', 'uploaded_at')
 
    @admin.display(description='Preview')
    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:6px;">',
                obj.image.url,
            )
        return '—'
 
 
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
 
    fieldsets = BaseUserAdmin.fieldsets + (
        ('PetConnect', {'fields': ('phone', 'role')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('PetConnect', {'fields': ('email', 'phone', 'role')}),
    )
 
 
@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'breed', 'location', 'status', 'owner', 'created_at')
    list_filter = ('status', 'species', 'created_at')
    search_fields = ('name', 'breed', 'location', 'owner__username')
    autocomplete_fields = ('owner',)
    date_hierarchy = 'created_at'
    inlines = [PetImageInline]
    list_select_related = ('owner',)
 
 
@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ('pet', 'adopter', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('pet__name', 'adopter__username', 'adopter__email')
    autocomplete_fields = ('pet', 'adopter')
    list_select_related = ('pet', 'adopter')
    readonly_fields = ('created_at', 'updated_at')
 
 
@admin.register(PetImage)
class PetImageAdmin(admin.ModelAdmin):
    list_display = ('pet', 'image', 'uploaded_at')
    search_fields = ('pet__name',)
    list_select_related = ('pet',)
 
 
