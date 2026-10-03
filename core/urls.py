from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import PostSitemap, StaticSitemap, CategorySitemap,TagSitemap
from django.http import HttpResponse
from blog.views import ckeditor5_custom_upload
from django.contrib.staticfiles.views import serve


sitemaps = {
    "static": StaticSitemap,
    "posts": PostSitemap,
    "categories": CategorySitemap,
    "tags": TagSitemap
}

urlpatterns = [    
    path('admin/', admin.site.urls),
    path('ckeditor5/image_upload/', ckeditor5_custom_upload, name='ckeditor5_image_upload'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path("", include("blog.urls")),
    
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("sitemap.xml/", sitemap, {"sitemaps": sitemaps}),
    path("robots.txt", lambda r: HttpResponse("User-agent: *\nDisallow: /admin/\nDisallow: /ckeditor5/\n\nSitemap: https://todagarota.com.br/sitemap.xml", 
            content_type="text/plain")),
   re_path("", include('pwa.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'blog.views.not_found'