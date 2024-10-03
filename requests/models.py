from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Requester(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name  # Display the Requester's name


class Buyer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name  # Display the Buyer's name


class Request(models.Model):
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Closed', 'Closed'),
        ('Canceled', 'Canceled'),
    ]

    REQUEST_TYPE_CHOICES = [
        ('Supplier creation', 'Supplier creation'),
        ('PO creation', 'PO creation'),
        ('NDA', 'NDA'),
        ('Supplier Assist', 'Supplier Assist'),
        ('Other request', 'Other request'),
        ('PO modification', 'PO modification'),
    ]

    requester = models.ForeignKey(Requester, on_delete=models.CASCADE)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    po_ref = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Started')
    subject = models.CharField(max_length=100)
    reference = models.CharField(max_length=50, unique=True, editable=False)  # Read-only, auto-generated
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    object = models.CharField(max_length=255, editable=False)
    attachments = models.FileField(upload_to='attachments/', null=True, blank=True)
    comments = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  # Set user (admin or creator)

    def save(self, *args, **kwargs):
        # Generate the reference if it's not set
        if not self.reference:
            self.reference = self.generate_reference()

        # Automatically generate the formatted object string before saving
        self.object = f"{self.request_type}_{self.subject}_{self.reference}_{self.requester.name}_{self.buyer.name}_{self.user.username if self.user else 'N/A'}_{self.status}"
        super().save(*args, **kwargs)

    def generate_reference(self):
        """Generate a unique and scalable reference based on the request type."""
        # Count the number of existing requests of this type
        count = Request.objects.filter(request_type=self.request_type).count() + 1

        # Set the correct prefix based on the request type
        prefix = {
            'Supplier creation': 'SUP',
            'PO creation': 'PO',
            'NDA': 'NDA',
            'Supplier Assist': 'SUPA',
        }.get(self.request_type, 'OTHER')  # Default to 'OTHER' for any unlisted types

        # Generate the reference with the prefix and incremented count
        return f"{prefix}{count:03}"

    def add_comment(self, comment_text, user):
        """Appends a comment with a timestamp and user to the comments field."""
        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        new_comment = f"<strong>{timestamp} - {user.username}:</strong> {comment_text}"
        if self.comments:
            self.comments += f"\n\n{new_comment}"  # Append new comment to existing comments
        else:
            self.comments = new_comment
        self.save()

    def __str__(self):
        return self.subject  # Display the subject of the request


