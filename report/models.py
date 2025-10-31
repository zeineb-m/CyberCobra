from django.db import models

from auth_app.models import User

# Create your models here.
class Report(models.Model):

    subject = models.CharField(
        max_length=255,
        null=False,
        blank=False,  # ensures it's not empty in forms and admin
        help_text="The subject or title of the report."
    )

    body = models.TextField(
        help_text="The main content of the report. Must be at least 500 characters."
    )

    writer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports'
    )

        # --- Department as ENUM ---
    DEPARTMENT_CHOICES = [
        ('security', 'Security Department'),
        ('immigration', 'Immigration Department'),
        ('civil_protection', 'Civil Protection'),
        ('finance', 'Finance Department'),
        ('planning', 'Planning and Development'),
    ]
     
    department = models.CharField(
        max_length=50,
        choices=DEPARTMENT_CHOICES,
        help_text="Select the department associated with this report."
    )

    bibliographies = models.JSONField(
        default=list,
        help_text="List of information sources or reference links."
    )

    used_documents = models.JSONField(
        default=list,
        help_text="List of used or referenced document names or file paths."
    )

        # --- Categories (ENUM list / tags) ---
    CATEGORY_CHOICES = [
        ('security', 'Security'),
        ('policy', 'Policy'),
        ('logistics', 'Logistics'),
        ('research', 'Research'),
        ('communication', 'Communication'),
        ('emergency', 'Emergency'),
        ('administration', 'Administration'),
    ]
    categories = models.JSONField(
        default=list,
        help_text="List of tags or topics (must be from predefined categories)."
    )
    
    # --- System fields ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


