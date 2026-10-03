from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Author
from .models import Post, Category, Tag

# Register your models here.
class CustomUserAdmin(UserAdmin):
    # Adiciona o campo de foto na tela de edição do usuário no Admin
    # fieldsets controla a divisão das seções dentro da página do usuário
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Extras', {'fields': ('image',)}),
    )
    
    # Adiciona a foto na lista de usuários para você ver a miniatura de quem é quem
    list_display = ('exibir_avatar', 'username', 'email', 'first_name', 'last_name', 'is_staff')
    list_display_links = ("username",)
    
    def exibir_avatar(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return format_html('<img src="{}" style="height: 40px; width: 40px; border-radius: 50%; object-cover: cover;" />', obj.image.url)
        return "Sem foto"
    
    exibir_avatar.short_description = 'Avatar'

# Registra o Usuario usando a classe customizada que criamos acima
admin.site.register(Author, CustomUserAdmin)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("image_thumbnail",'title', 'author','category', 'status', 'created_at')
    list_editable = ("status",)
    list_display_links = ("title",)
    list_filter = ('status', 'author', 'category', 'tags')
    search_fields = ('title', 'content')
    ordering = ("-created_at",)
    prepopulated_fields = {'slug': ('title',)}

    @admin.display(description="Capa")
    def image_thumbnail(self, obj):
        if obj.image_cover and hasattr(obj.image_cover, 'url'):
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" style="height: 50px; width: 50px; object-fit: cover; border-radius: 5px;" />'
                '</a>',
                obj.image_cover.url
            )
        return "Sem imagem"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)
    
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            fields = [f for f in fields if f != 'author']
        return fields
    
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            if not change or not obj.author_id:
                obj.author = request.user
        return super().save_model(request, obj, form, change)
    


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}



@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}