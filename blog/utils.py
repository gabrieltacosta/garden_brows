import os
from io import BytesIO
from django.core.files.base import ContentFile
import cuid2
from PIL import Image, ImageOps



def generate_cuid():
    return cuid2.cuid_wrapper()()

# --- FUNÇÃO PARA COMPRIMIR E CONVERTER PARA WEBP ---
def compress_and_convert_to_webp(image_field, max_width=1024, quality=80, is_avatar=False):

    if not image_field or not image_field.file:
        return

    # Abre a imagem original usando o Pillow
    img = Image.open(image_field)

    img = ImageOps.exif_transpose(img)

    # Converte para RGB (necessário se a imagem original for PNG com transparência ou RGBA)
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        # Cria um fundo branco para manter a visibilidade caso haja transparência
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.convert('RGBA').split()[3])
        img = background
    else:
        img = img.convert('RGB')

    if is_avatar:
        img = ImageOps.fit(img, (max_width, max_width), Image.Resampling.LANCZOS)
    else:
    # Redimensiona proporcionalmente se a largura for maior que o permitido (ex: 1024px)
        if img.width > max_width:
            output_size = (max_width, int((max_width / img.width) * img.height))
            img = img.resize(output_size, Image.Resampling.LANCZOS)

    # Cria o buffer na memória (BytesIO)
    image_io = BytesIO()

    # Salva a imagem no buffer formato WEBP com a qualidade desejada (0-100)
    img.save(image_io, format='WEBP', quality=quality, optimize=True)

    # Altera a extensão do nome do arquivo original para .webp
    current_filename = os.path.splitext(image_field.name)[0]
    new_filename = f"{current_filename}.webp"

    # Atribuímos o novo ContentFile diretamente ao arquivo do campo, evitando disparar o save() do Django.
    image_field.file = ContentFile(image_io.getvalue())
    image_field.name = new_filename


# --- CONFIGURAÇÃO DOS CAMINHOS ---
def get_image_upload_path(instance, filename):
    return os.path.join('users', instance.id, filename)

def get_cover_upload_path(instance, filename):
    return os.path.join('post', instance.id, filename)