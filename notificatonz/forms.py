from django import forms
from .models import MessageLog

class MessageForm(forms.ModelForm):
    class Meta:
        model = MessageLog
        fields = ['channel', 'recipient', 'subject', 'body']
        
        widgets = {
            'channel': forms.Select(attrs={'class': 'form-select'}),
            'recipient': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email or +123456789'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Only for Email'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }