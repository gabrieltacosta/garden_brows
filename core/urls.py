from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import PostSitemap, StaticSitemap, CategorySitemap,TagSitemap
from django.views.generic.base import TemplateView
from blog.views import ckeditor5_custom_upload, custom_admin_login_view



sitemaps = {
    "static": StaticSitemap,
    "posts": PostSitemap,
    "categories": CategorySitemap,
    "tags": TagSitemap
}

urlpatterns = [
    path('admin/login/', custom_admin_login_view, name='admin_login'),
    path('admin/', admin.site.urls),
    path('ckeditor5/image_upload/', ckeditor5_custom_upload, name='ckeditor5_image_upload'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path("", include("blog.urls")),
    
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("sitemap.xml/", sitemap, {"sitemaps": sitemaps}),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
   re_path("", include('pwa.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'blog.views.not_found'