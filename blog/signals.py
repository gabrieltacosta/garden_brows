import os
import shutil
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Author, Post, Material


# Helper para remover um arquivo individual de forma segura
def safe_remove_file(file_field):
    if file_field and os.path.isfile(file_field.path):
        os.remove(file_field.path)


# Helper para remover o diretório correspondente ao objeto
def delete_object_directory(folder_path):
    if os.path.isdir(folder_path):
        try:
            shutil.rmtree(folder_path)
        except OSError:
            pass


# ==============================================================================
# --- SIGNALS PARA EXCLUSÃO AUTOMÁTICA DE IMAGENS (SISTEMA DE LIMPEZA) ---
# ==============================================================================

# 1. Deleta o arquivo físico quando o objeto é excluído do banco de dados
@receiver(post_delete, sender=Post)
def delete_post_folder_on_delete(sender, instance, **kwargs):
    if instance.image_cover:
        # Obtém o caminho do diretório onde o arquivo está armazenado (ex: media/posts/123/)
        folder_path = os.path.dirname(instance.image_cover.path)
        delete_object_directory(folder_path)

@receiver(post_delete, sender=Author)
def delete_author_folder_on_delete(sender, instance, **kwargs):
    if instance.image:
        folder_path = os.path.dirname(instance.image.path)
        delete_object_directory(folder_path)

@receiver(post_delete, sender=Material)
def delete_material_folder_on_delete(sender, instance, **kwargs):
    # Pega o diretório a partir de qualquer um dos arquivos presentes
    file_path = instance.file.path if instance.file else (instance.image.path if instance.image else None)
    if file_path:
        folder_path = os.path.dirname(file_path)
        delete_object_directory(folder_path)


# 2. Deleta o arquivo antigo quando o usuário altera a imagem por uma NOVA
@receiver(pre_save, sender=Post)
def delete_old_cover_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return 
    try:
        old_post = Post.objects.get(pk=instance.pk)
    except Post.DoesNotExist:
        return

    if old_post.image_cover and old_post.image_cover != instance.image_cover:
        safe_remove_file(old_post.image_cover)

@receiver(pre_save, sender=Author)
def delete_old_avatar_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return 
    try:
        old_user = Author.objects.get(pk=instance.pk)
    except Author.DoesNotExist:
        return 

    if old_user.image and old_user.image != instance.image:
        safe_remove_file(old_user.image)

@receiver(pre_save, sender=Material)
def delete_old_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return 
    try:
        old_material = Material.objects.get(pk=instance.pk)
    except Material.DoesNotExist:
        return 

    if old_material.file and old_material.file != instance.file:
        safe_remove_file(old_material.file)

    if old_material.image and old_material.image != instance.image:
        safe_remove_file(old_material.image)
