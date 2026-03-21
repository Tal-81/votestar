"""votes/forms.py"""
from django import forms
from .models import Vote


class VoteForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1, max_value=5,
        widget=forms.HiddenInput(),  # The star UI in the template sets this
    )

    class Meta:
        model = Vote
        fields = ['rating']
