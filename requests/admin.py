from django.contrib import admin
from .models import Requester, Buyer, Request
from django.utils.safestring import mark_safe
from django import forms
from django.http import HttpResponse
from openpyxl import Workbook

# Registering the Requester and Buyer models
admin.site.register(Requester)
admin.site.register(Buyer)

# Custom form for RequestAdmin
class RequestAdminForm(forms.ModelForm):
    # Adding a separate form field for the new comment
    new_comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter new comment here...'}),
        required=False
    )

    class Meta:
        model = Request
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.user:  # Set user if it's not already set
            instance.user = self.current_user
        new_comment = self.cleaned_data.get('new_comment')
        if new_comment:
            instance.add_comment(new_comment, self.current_user)
        if commit:
            instance.save()
        return instance

# Custom export to Excel action
def export_to_excel(modeladmin, request, queryset):
    """ Export selected requests to an Excel file """
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Requests.xlsx'
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Requests"

    # Adding header row
    headers = ['Requester', 'Buyer', 'Request Type', 'PO Ref', 'Status', 'Subject', 'Reference', 'Created By', 'Created At', 'Updated At']
    ws.append(headers)

    # Adding data rows
    for obj in queryset:
        created_by_username = obj.user.username if obj.user else 'N/A'
        ws.append([
            obj.requester.name,
            obj.buyer.name,
            obj.request_type,
            obj.po_ref,
            obj.status,
            obj.subject,
            obj.reference,
            created_by_username,
            obj.created_at.strftime('%Y-%m-%d %H:%M'),
            obj.updated_at.strftime('%Y-%m-%d %H:%M'),
        ])

    wb.save(response)
    return response

export_to_excel.short_description = 'Export to Excel'

# Admin class for Request model
class RequestAdmin(admin.ModelAdmin):
    form = RequestAdminForm
    # Make `reference`, `object`, `created_at`, `updated_at`, and `comments_display` readonly
    readonly_fields = ('reference', 'object', 'created_at', 'updated_at', 'comments_display')

    actions = [export_to_excel]  # Add the export action to the admin page

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user  # Pass the current user to the form
        return form

    def comments_display(self, obj):
        """Display the comments in a readable format with line breaks."""
        return mark_safe('<br>'.join(obj.comments.split('\n'))) if obj.comments else 'No comments yet'
    comments_display.short_description = 'Comments'

    # Customize the field layout in the form
    fieldsets = (
        (None, {
            'fields': (
                'requester', 'buyer', 'request_type', 'po_ref', 'status', 
                'subject', 'attachments', 
                'comments_display', 'new_comment'
            )
        }),
        ('Timestamps', {
            'fields': ('reference', 'object', 'created_at', 'updated_at')
        }),
    )

# Register the Request model with the RequestAdmin class
admin.site.register(Request, RequestAdmin)





