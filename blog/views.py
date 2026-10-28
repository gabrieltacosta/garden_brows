from django.core.mail import send_mail
from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
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
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.urls import reverse
from blog.forms import CommentForm, ContactForm, CustomAdminForm
from django.conf import settings
from .models import Post, Category, Tag, Material, PostView
from django.views.generic import DetailView
from datetime import timedelta
from django.utils import timezone
from django.db import models


def healthcheck(request):
    return HttpResponse("OK", status=200)

def custom_admin_login_view(request):
    # Se o usuário já estiver logado, redireciona para o admin
    if request.user.is_authenticated:
        return redirect('/admin/')

    if request.method == 'POST':
        # 1. Validação do Honeypot (Bloqueio de bots)
        if request.POST.get("website_honeypot"):
            messages.error(request, "Acesso bloqueado por segurança.")
            return redirect(request.path)

        # 2. Instancia o formulário passando o request e os dados POST
        form = CustomAdminForm(request, data=request.POST)

        if form.is_valid():
            # Realiza o login do usuário autenticado
            user = form.get_user()
            login(request, user)
            
            # Redireciona para a página 'next' ou para o painel admin padrão
            next_url = request.GET.get('next') or request.POST.get('next') or '/admin/'
            return redirect(next_url)
    else:
        form = CustomAdminForm(request)

    context = {
        'form': form,
        'title': 'Entrar - GardenBrows Admin',
        'next': request.GET.get('next') or request.POST.get('next', '')
    }
    return render(request, 'admin/login.html', context)

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

#@cache_page(60 * 60)  # Cache de 1 hora
def home(request):
    posts_published = list(Post.objects.filter(status='published').order_by('-created_at'))
    featured_post = posts_published[0] if posts_published else None
    recent_posts = posts_published[1:4] if len(posts_published) > 1 else []
    materials = Material.objects.filter(is_active=True)
    return render(request, "home.html", {'featured_post': featured_post, 'recent_posts': recent_posts, 'materials': materials})



class PostDetailView(FormMixin, DetailView):
    model = Post
    template_name = 'detail.html'
    context_object_name = 'post'
    form_class = CommentForm

    def get_queryset(self):
        # Garante que a busca inicial só traga posts publicados
        return super().get_queryset().filter(status='published')

    def get_success_url(self):
        # Redireciona de volta para a própria página do post após comentar
        return reverse('blog:detail', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_atual = self.object

        if 'form' not in context:
            context['form'] = self.get_form()

        context['comments'] = post_atual.comments.filter(is_active=True).order_by('-created_at')

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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if request.POST.get("website_honeypot"):
            messages.success(request, "Agradecemos sua contribuição. Ele será exibido assim que for aprovado por um moderador.")
            return redirect('blog:detail', slug=self.object.slug)

        remote_ip = request.META.get("REMOTE_ADDR")

        form = self.get_form_class()(request.POST, remote_ip=remote_ip)

        if form.is_valid():
            return self.form_valid(form)
        
        return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = self.object
        comment.save()

        messages.success(self.request, "Agradecemos sua contribuição. Ele será exibido assim que for aprovado por um moderador.")

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Por favor, confirme que você não é um robô para enviar o comentário.")
        return super().form_invalid(form)


    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        if request.user_agent.is_bot:
            return response

        # Captura o IP do visitante
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key

        # Registra apenas se não existir visualização desse IP ou Sessão nas últimas 24 horas
        time_threshold = timezone.now() - timedelta(hours=24)
        
        has_viewed = PostView.objects.filter(
            post=self.object,
            created_at__gte=time_threshold
        ).filter(
            models.Q(ip_address=ip) | models.Q(session_key=session_key)
        ).exists()

        if not has_viewed:
            PostView.objects.create(
                post=self.object,
                ip_address=ip,
                session_key=session_key
            )

        return response



def post_archive(request):
    query = request.GET.get('q', '').strip()
    # Pega todos os posts publicados
    posts_list = Post.objects.filter(status='published').order_by('-created_at')

    if query:
        posts_list = posts_list.filter(
            models.Q(title__icontains=query) | 
            models.Q(description__icontains=query) |
            models.Q(content__icontains=query)
        ).distinct()
    
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
        'has_next': page_obj.has_next(),
        'search_query': query,
    })


class PrivacyPolicyView(TemplateView):
    template_name = "pages/privacy.html"


class TermsOfUseView(TemplateView):
    template_name = "pages/terms.html"


def contact_view(request):

    if request.method == "POST":
        if request.POST.get("website_honeypot"):
            messages.success(request, "Sua mensagem foi enviada com sucesso.")
            return redirect("blog:contact")
        
        remote_ip = request.META.get("REMOTE_ADDR")
        form = ContactForm(request.POST, remote_ip=remote_ip)
        if form.is_valid():
            name = request.POST.get("name")
            email = request.POST.get("email")
            subject = request.POST.get("subject")
            message = request.POST.get("message")

            try:    

                send_mail(
                    subject=f"Contato do Blog: {subject}",
                    message=f"Nome: {name}\nEmail: {email}\n\nMensagem:\n{message}",
                    from_email=None,
                    recipient_list=settings.ADMIN_EMAILS,
                    fail_silently=False,
                )
                messages.success(request, f"Obrigada, {name}! Sua mensagem foi enviada com sucesso. Responderemos em breve.")
            except Exception as e:
                messages.error(request, f"Desculpe, {name}. Ocorreu um erro ao enviar sua mensagem. Por favor, tente novamente mais tarde.")
            return redirect("blog:contact")
        else:
            messages.error(request, "Por favor, confirme que você não é um robô.")
    else:
        form = ContactForm()

    return render(request, "pages/contact.html", {"form": form})


@cache_page(60 * 60)  # Cache de 1 hora
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


@cache_page(60 * 60)  # Cache de 1 hora
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


def material_page(request):
    if request.method == 'GET':
        materials = Material.objects.filter(is_active=True)
        return render(request, 'pages/material_page.html', {'materials': materials})


@staff_member_required
def manually_clear_cache(request):
    cache.clear()
    messages.success(
        request,
        "Cache limpo com sucesso! Todas as páginas foram atualizadas.",
        extra_tags="cache-admin"
    )
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER')
    if not next_url or '/admin/login/' in next_url:
        next_url = '/'
    return redirect(next_url)