from django.urls import path
from .views import home, PostDetailView, post_archive, PrivacyPolicyView, TermsOfUseView, contact_view, category_detail, tag_detail, healthcheck

app_name = "blog"

urlpatterns = [
    path('', home, name="home"),
    path('health/', healthcheck, name='healthcheck'),
    path("posts/", post_archive, name="archive"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="detail"),
    path("politica-de-privacidade/", PrivacyPolicyView.as_view(), name="privacy"),
    path("termos-de-uso/", TermsOfUseView.as_view(), name="terms"),
    path("contato/", contact_view, name="contact"),
    path("categoria/<slug:slug>/", category_detail, name="category_detail"),
    path("tag/<slug:slug>/", tag_detail, name="tag_detail"),
]