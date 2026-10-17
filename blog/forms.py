from django import forms
from .models import Comment
from turnstile.fields import TurnstileField

class CommentForm(forms.ModelForm):
    turnstile = TurnstileField()

    class Meta:
        model = Comment
        fields = ['name','content']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Escreva seu nome'}),
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escreva seu comentário...'}),
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('remote_ip', None)
        super().__init__(*args, **kwargs)



class ContactForm(forms.Form):
    name = forms.CharField(label='Seu Nome', max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'w-full bg-brand-light/50 text-sm text-brand-dark px-4 py-3 rounded-xl border border-brand-blush/40 focus:outline-none focus:border-brand-terracotta transition',
        'aria-label': 'Input de Nome',
        'placeholder': 'Escreva seu nome'}))
    email = forms.EmailField(label='Seu E-mail', required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full bg-brand-light/50 text-sm text-brand-dark px-4 py-3 rounded-xl border border-brand-blush/40 focus:outline-none focus:border-brand-terracotta transition',
        'aria-label': 'Input de Email',
        'placeholder': 'Escreva seu email'}))
    subject = forms.CharField(label='Assunto', max_length=200, required=True, widget=forms.TextInput(attrs={
        'class': 'w-full bg-brand-light/50 text-sm text-brand-dark px-4 py-3 rounded-xl border border-brand-blush/40 focus:outline-none focus:border-brand-terracotta transition',
        'aria-label': 'Input de Assunto',
        'placeholder': 'Escreva o assunto'}))
    message = forms.CharField(label='Sua Mensagem', required=True, widget=forms.Textarea(attrs={
        'rows': 5,
        'class': 'w-full bg-brand-light/50 text-sm text-brand-dark px-4 py-3 rounded-xl border border-brand-blush/40 focus:outline-none focus:border-brand-terracotta transition resize-y',
        'aria-label': 'Input de Mensagem',
        'placeholder': 'Escreva sua mensagem...'}))
    turnstile = TurnstileField()