from django import forms
from .models import Post, Comment
from django.utils.translation import gettext_lazy as _


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {'text': _('Текст поста'),
                  'group': _('Группа')}
        help_texts = {
            'text': _('Что хотите написать?'),
            'group': _('Относится к группе ?')}

    def clean_text(self):
        text = self.cleaned_data['text']
        return text


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

    def clean_text(self):
        text = self.cleaned_data['text']
        return text
