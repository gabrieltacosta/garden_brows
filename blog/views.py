from django.core.mail import send_mail
from django.views.generic import TemplateView
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import os
from io import BytesIO
from urllib.parse import urlparse
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, EmptyPage
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.text import slugify
from PIL import Image
from django.views.decorators.cache import cache_page

from .models import Post, Category, Tag
from django.views.generic import DetailView


def healthcheck(request):
    return HttpResponse("OK", status=200)


@csrf_exempt
def ckeditor5_custom_upload(request):
    if request.method == 'POST' and request.FILES.get('upload'):
        uploaded_file = request.FILES['upload']
        
        # --- ESTRATÉGIA PARA DEFINIR A PASTA BASEADOS NO ID (SOLUÇÃO A) ---
        post_id = None
        
        # 1. Tenta pegar o ID enviado via cabeçalho customizado (X-Post-Id) ou POST comum
        if 'HTTP_X_POST_ID' in request.META:
            post_id = request.META['HTTP_X_POST_ID']
        else:
            post_id = request.POST.get('post_id')
        
        # 2. Fallback: Se não veio explicitamente, tenta extrair da URL de Referência (Edição)
        if not post_id and 'HTTP_REFERER' in request.META:
            referer_path = urlparse(request.META['HTTP_REFERER']).path
            path_parts = [p for p in referer_path.split('/') if p]
            
            # Padrão esperado do admin: ['admin', 'blog', 'post', 'ID_DO_POST', 'change']
            if len(path_parts) >= 4 and path_parts[0] == 'admin' and path_parts[2] == 'post':
                post_id = path_parts[3]

        # 3. Fallback Final: Se o post for NOVO e não capturamos o ID, usa o usuário logado
        if not post_id:
            if request.user.is_authenticated:
                folder_name = f"temporario-{slugify(request.user.username)}"
            else:
                folder_name = "temporario-anonimo"
        else:
            folder_name = post_id

        # --- PROCESSAMENTO E COMPRESSÃO DA IMAGEM COM PILLOW ---
        try:
            img = Image.open(uploaded_file)
            
            # Corrige a orientação da imagem com base nos metadados EXIF
            from PIL import ImageOps
            img = ImageOps.exif_transpose(img)
            
            # Trata transparências de PNGs/WMPhs convertendo para um fundo branco (RGB)
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.convert('RGBA').split()[3])
                img = background
            else:
                img = img.convert('RGB')
                
            # Redimensiona proporcionalmente se a largura for maior que 1200px
            if img.width > 1200:
                output_size = (1200, int((1200 / img.width) * img.height))
                img = img.resize(output_size, Image.Resampling.LANCZOS)
                
            # Cria o buffer na memória e salva o arquivo comprimido em WebP
            image_io = BytesIO()
            img.save(image_io, format='WEBP', quality=80, optimize=True)
            
            # Limpa o nome do arquivo original para evitar caracteres estranhos na URL
            filename_base = os.path.splitext(uploaded_file.name)[0]
            new_filename = f"{slugify(filename_base)}.webp"
            
            # Monta o caminho final: media/post/[ID_OU_TEMP]/imagens/[NOME_DO_ARQUIVO].webp
            custom_path = os.path.join('post', folder_name, 'imagens', new_filename)
            
            # Salva fisicamente no sistema de arquivos do Django
            saved_path = default_storage.save(custom_path, ContentFile(image_io.getvalue()))
            file_url = default_storage.url(saved_path)
            
            # O CKEditor necessita estritamente desse retorno JSON com a chave 'url'
            return JsonResponse({'url': file_url})
            
        except Exception as e:
            return JsonResponse({'error': {'message': f'Erro ao processar imagem: {str(e)}'}}, status=400)
            
    return JsonResponse({'error': {'message': 'Método não permitido ou arquivo não enviado.'}}, status=400)

# @cache_page(60 * 60)
def home(request):
    posts_published = list(Post.objects.filter(status='published').order_by('-created_at'))
    featured_post = posts_published[0] if posts_published else None
    recent_posts = posts_published[1:4] if len(posts_published) > 1 else []
    return render(request, "home.html", {'featured_post': featured_post, 'recent_posts': recent_posts})



class PostDetailView(DetailView):
    model = Post
    template_name = 'detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        # Garante que a busca inicial só traga posts publicados
        return super().get_queryset().filter(status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_atual = self.object
        tag_ids = post_atual.tags.values_list('id', flat=True)
        related_posts = Post.objects.filter(status='published', tags__in=tag_ids).exclude(id=post_atual.id)
        context['related_posts'] = related_posts.annotate(
            same_tags_count=Count('tags')
        ).order_by('-same_tags_count', '-created_at')[:3]

        if post_atual.category:
            context['category_posts'] = Post.objects.filter(
                status='published', 
                category=post_atual.category
            ).exclude(id=post_atual.id).order_by('-created_at')[:3]
        else:
            context['category_posts'] = None

        return context

# @cache_page(60 * 60)
def post_archive(request):
    # Pega todos os posts publicados
    posts_list = Post.objects.filter(status='published').order_by('-created_at')
    
    # Define o limite de 9 posts por página
    paginator = Paginator(posts_list, 9)
    page_number = request.GET.get('page', 1)

    # CORREÇÃO: Pega o cabeçalho convertendo para minúsculo para evitar divergências
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or \
               request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

    # Bloco exclusivo para requisições AJAX
    if is_ajax:
        try:
            page_obj = paginator.page(page_number)
            html = render_to_string('components/post_grid_items.html', {'page_obj': page_obj}, request=request)

            response = HttpResponse(html)
            if not page_obj.has_next():
                response['X-Last-Page'] = 'true'
            return response
            
        except EmptyPage:
            # Se a página passar do limite, retorna 404 para o AJAX sumir com o botão
            return HttpResponse('', status=404)

    # Bloco para ACESSO NORMAL (Primeiro carregamento da página inteira)
    page_obj = paginator.get_page(page_number)
    return render(request, "archive.html", {
        'page_obj': page_obj,
        'has_next': page_obj.has_next()
    })


class PrivacyPolicyView(TemplateView):
    template_name = "pages/privacy.html"


class TermsOfUseView(TemplateView):
    template_name = "pages/terms.html"


def contact_view(request):

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # TODO: Aqui você pode usar o send_mail do Django para enviar um e-mail real para você.
        # Por enquanto, vamos apenas simular o sucesso.
        send_mail(
            subject=f"Contato do Blog: {subject}",
            message=f"Nome: {name}\nEmail: {email}\n\nMensagem:\n{message}",
            from_email=None,
            recipient_list=['gabriel.tuka@gmail.com'],
            fail_silently=False,
        )
        
        messages.success(request, f"Obrigada, {name}! Sua mensagem foi enviada com sucesso. Responderemos em breve.")
        return redirect("blog:contact")

    return render(request, "pages/contact.html")



def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    # Busca apenas posts publicados dessa categoria
    posts_list = Post.objects.filter(status='published', category=category).order_by('-created_at')
    
    paginator = Paginator(posts_list, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, "pages/category_detail.html", {
        "category": category,
        "page_obj": page_obj
    })



def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    # Busca apenas posts publicados com essa tag
    posts_list = Post.objects.filter(status='published', tags=tag).order_by('-created_at')
    
    paginator = Paginator(posts_list, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, "pages/tag_detail.html", {
        "tag": tag,
        "page_obj": page_obj
    })

def not_found(request, exception):
    return render(request, 'not_found.html')