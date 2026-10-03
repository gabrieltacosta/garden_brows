from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Post, Category, Tag

class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Post.objects.filter(status='published').order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at
    

class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        # Só gera sitemap para categorias que possuem pelo menos um post publicado
        return Category.objects.filter(posts__status='published').distinct()

    def location(self, obj):
        from django.urls import reverse
        return reverse('blog:category_detail', kwargs={'slug': obj.slug})
    


class TagSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Tag.objects.filter(posts__status='published').distinct()
    
    def location(self, obj):
        from django.urls import reverse
        return reverse('blog:tag_detail', kwargs={'slug': obj.slug})
    

class StaticSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return ['blog:home']
    
    def location(self, item):
        return reverse(item)