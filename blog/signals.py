import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Author, Post



# ==============================================================================
# --- SIGNALS PARA EXCLUSÃO AUTOMÁTICA DE IMAGENS (SISTEMA DE LIMPEZA) ---
# ==============================================================================

# 1. Deleta o arquivo físico quando o objeto é excluído do banco de dados
@receiver(post_delete, sender=Post)
def delete_cover_on_post_delete(sender, instance, **kwargs):
    if instance.image_cover:
        if os.path.isfile(instance.image_cover.path):
            os.remove(instance.image_cover.path)

@receiver(post_delete, sender=Author)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

# 2. Deleta o arquivo antigo quando o usuário altera a imagem por uma NOVA
@receiver(pre_save, sender=Post)
def delete_old_cover_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False
    try:
        old_post = Post.objects.get(pk=instance.pk)
    except Post.DoesNotExist:
        return False

    old_cover = old_post.image_cover
    new_cover = instance.image_cover
    if old_cover and old_cover != new_cover:
        if os.path.isfile(old_cover.path):
            os.remove(old_cover.path)

@receiver(pre_save, sender=Author)
def delete_old_avatar_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False
    try:
        old_user = Author.objects.get(pk=instance.pk)
    except Author.DoesNotExist:
        return False

    old_img = old_user.image
    new_img = instance.image
    if old_img and old_img != new_img:
        if os.path.isfile(old_img.path):
            os.remove(old_img.path)