from django import forms
from .models import Topic


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'What do you want people to rate?',
                'maxlength': 200,
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Add more context (optional)…',
            }),
        }
