# Garden Brows Blog

Garden Brows Blog é um projeto de blog e portal em Django para publicar conteúdos editoriais, materiais complementares e artigos com foco em bem-estar, estilo de vida, inspiração e educação feminina.

## Visão geral

A aplicação foi construída para oferecer:

- publicação de posts com categoria e tags;
- suporte a conteúdo rico com CKEditor 5;
- gestão de autores e materiais extras;
- páginas institucionais como política de privacidade e termos de uso;
- suporte a PWA para experiência instalável;
- banco PostgreSQL e cache Redis em ambiente de desenvolvimento.

## Stack

- Python 3.11+
- Django 6.0
- PostgreSQL 16
- Redis 7
- Django CKEditor 5
- django-jazzmin
- django-pwa
- Docker Compose

## Estrutura do projeto

- `blog/`: app principal com modelos, views, URLs e templates do blog.
- `core/`: configuração do projeto Django e URLs globais.
- `templates/`: templates compartilhados da aplicação.
- `static/`: arquivos estáticos do front-end.
- `compose.yaml`: serviços de infraestrutura para PostgreSQL e Redis.
- `manage.py`: entry point do Django.
- `.env.example`: template de variáveis de ambiente.

## Requisitos

Antes de iniciar, certifique-se de ter instalado:

- Python 3.11 ou superior
- pip
- virtualenv
- Docker e Docker Compose
- Git

## Configuração inicial

1. Clone o repositório:

   ```bash
   git clone <url-do-repositorio>
   cd garden_brows
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Copie o arquivo de ambiente:

   ```bash
   cp .env.example .env
   ```

5. Ajuste os valores do arquivo `.env` conforme o ambiente local.

   Exemplo mínimo de configuração:

   ```env
   SECRET_KEY=sua-chave-secreta
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1

   POSTGRES_DB=postgres
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   ```

## Executando serviços externos

Para iniciar o PostgreSQL e o Redis com Docker Compose:

```bash
docker compose up -d db redis
```

## Rodando a aplicação

1. Aplique as migrações:

   ```bash
   python manage.py migrate
   ```

2. Crie um superusuário para acessar o painel administrativo:

   ```bash
   python manage.py createsuperuser
   ```

3. Inicie o servidor de desenvolvimento:

   ```bash
   python manage.py runserver
   ```

4. Acesse:

   - site: http://localhost:8000/
   - admin: http://localhost:8000/admin/

## Coletando arquivos estáticos

Em produção ou em ambiente com deploy mais próximo do real, rode:

```bash
python manage.py collectstatic --noinput
```

## Funcionalidades principais

- Publicação de posts com título, slug, imagem de capa e conteúdo rico;
- Organização por categoria e tags;
- Upload e gerenciamento de materiais, arquivos e links externos;
- Página de contato e páginas de termos/políticas;
- Suporte a caching com Redis;
- Healthcheck em `/health/`;
- PWA para instalação em dispositivos.

## Observações

- O projeto usa `AUTH_USER_MODEL = "blog.Author"`, então o modelo de usuário customizado é usado em vez do padrão do Django.
- O arquivo `compose.yaml` já prepara os serviços de banco e cache para uso local.
- Em produção, recomende-se ajustar `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` e demais configurações de segurança.

## Contribuição

Contribuições são bem-vindas. Para enviar alterações, siga o fluxo padrão de Git:

```bash
git checkout -b minha-feature
git add .
git commit -m "feat: minha funcionalidade"
git push origin minha-feature
```

## Licença

Este projeto não possui uma licença definida no repositório. Verifique com a equipe responsável antes de reutilizar ou distribuir o código em produção.

