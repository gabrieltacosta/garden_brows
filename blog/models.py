import os
import re
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from .utils import get_materials_upload_path, get_image_upload_path, get_cover_upload_path, compress_and_convert_to_webp, generate_cuid





class Author(AbstractUser):
    id = models.CharField(primary_key=True, default=generate_cuid, editable=False, max_length=50)
    image = models.ImageField(upload_to=get_image_upload_path, blank=True, null=True, verbose_name="Foto")

    def __str__(self):
        return self.get_full_name() or self.username

    def save(self, *args, **kwargs):
        # Se uma nova imagem foi enviada, comprime antes de salvar
        if self.image and hasattr(self.image, 'name') and self.image.name:
            if not self.image.name.endswith('.webp'):
                compress_and_convert_to_webp(self.image, max_width=400, quality=85, is_avatar=True)
        super().save(*args, **kwargs)

    @property
    def avatar_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return 'Sem imagem'

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Nome")
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Post(models.Model):
    id = models.CharField(primary_key=True, default=generate_cuid, editable=False, max_length=50)
    STATUS_CHOICES = (('draft', 'Rascunho'), ('published', 'Publicado'))

    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="slug")
    description = models.CharField(max_length=200, verbose_name="Descrição")
    image_cover = models.ImageField(upload_to=get_cover_upload_path, blank=True, null=True, verbose_name="Capa")
    content = CKEditor5Field('Conteúdo', config_name='default')
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="posts",
        verbose_name="Categoria"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts", verbose_name="Tags")
    author = models.ForeignKey(Author, on_delete=models.PROTECT, verbose_name="Autor")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="Status")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        # 1. Gera o slug se não existir
        if not self.slug:
            self.slug = slugify(self.title)

        # 2. Se uma nova capa foi enviada, comprime e converte para .webp
        if self.image_cover and not self.image_cover.name.endswith('.webp'):
            compress_and_convert_to_webp(self.image_cover, max_width=1200, quality=80, is_avatar=False)

        # 3. --- SISTEMA DE LIMPEZA DE IMAGENS DO CKEDITOR ---
        if self.pk:  # Só faz isso se o post já existir (ou seja, se for uma EDIÇÃO)
            try:
                # Busca a versão atual do post diretamente do banco de dados antes de salvar o novo texto
                post_antigo = Post.objects.get(pk=self.pk)

                # Expressão regular para encontrar o caminho de todas as imagens (<img src="...">)
                # Ela captura o que estiver dentro de /media/...webp
                pattern = r'src="/media/([^"]+)"'

                imagens_antigas = set(re.findall(pattern, post_antigo.content))
                imagens_novas = set(re.findall(pattern, self.content))

                # Descobre quais imagens foram deletadas pelo usuário no editor
                imagens_removidas = imagens_antigas - imagens_novas

                # Apaga os arquivos físicos das imagens removidas
                from django.conf import settings
                for img_path_relativo in imagens_removidas:
                    # Converte o caminho relativo da URL para o caminho absoluto no seu computador
                    caminho_absoluto = os.path.join(settings.MEDIA_ROOT, img_path_relativo)
                    if os.path.isfile(caminho_absoluto):
                        os.remove(caminho_absoluto)

            except Post.DoesNotExist:
                pass
        # -----------------------------------------------------

        # Salva o post de fato com o novo conteúdo
        super().save(*args, **kwargs)

    @property
    def tempo_leitura(self):
    # Remove tags HTML se o seu conteúdo usar rich text / markdown
        texto_limpo = re.sub(r'<[^>]+>', '', self.content)
        palavras = len(texto_limpo.split())

    # Média padrão de leitura: 200 palavras por minuto
        velocidade = 200
        minutos = palavras / velocidade

    # Retorna pelo menos 1 minuto se houver texto
        tempo = round(minutos)
        return max(tempo, 1)


class Material(models.Model):
    id = models.CharField(primary_key=True, default=generate_cuid, editable=False, max_length=50)
    title = models.CharField(max_length=100, verbose_name="Título")
    slug = models.SlugField(max_length=100, unique=True, blank=True, help_text="Gerado automaticamente se deixado em branco.")
    description = models.TextField(help_text="Breve explicação do material para aparecer no card.", verbose_name="Descrição")
    file = models.FileField(upload_to=get_materials_upload_path, blank=True,
        null=True, verbose_name="Arquivo (PDF, Planilha, etc.)", help_text="Faça o upload caso seja um arquivo direto.")
    external_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="Link Externo",
        help_text="Use caso o material esteja no Google Drive, Notion, Canva, etc."
    )
    image = models.ImageField(upload_to=get_materials_upload_path, blank=True, null=True, verbose_name="Imagem de Capa / Ilustração")
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Marque para exibir este material na homepage e na página de materiais."
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem de exibição",
        help_text="Materiais com menor número aparecem primeiro (0, 1, 2...)."
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiais"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
            if not self.slug:
                self.slug = slugify(self.title)

            if self.image and not self.image.name.endswith('.webp'):
                        compress_and_convert_to_webp(self.image, max_width=1200, quality=80, is_avatar=False)

            super().save(*args, **kwargs)

    @property
    def access_url(self):
        """Retorna a URL do arquivo de download ou o link externo."""
        if self.file:
            return self.file.url
        return self.external_link or "#"

    @property
    def is_external(self):
        """Indica se é um link externo (para saber se abre em nova aba)."""
        return bool(self.external_link and not self.file)