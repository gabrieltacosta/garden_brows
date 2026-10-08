from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name','content']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Seu nome'}),
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escreva seu comentário...'}),
        }