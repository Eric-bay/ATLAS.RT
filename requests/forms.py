from django import forms
from .models import Request

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['requester', 'buyer', 'request_type', 'po_ref', 'status', 'subject', 'attachments', 'comments']
