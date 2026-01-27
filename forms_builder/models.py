from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid


class FormType(models.TextChoices):
    REGISTRATION = 'registration', 'Registration'
    SURVEY = 'survey', 'Survey'
    DATA_COLLECTION = 'data_collection', 'Data Collection'


class FormStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'
    ARCHIVED = 'archived', 'Archived'


class FormAccess(models.TextChoices):
    PUBLIC = 'public', 'Public (No authentication required)'
    AUTHENTICATED = 'authenticated', 'Authenticated users only'


class FieldType(models.TextChoices):
    TEXT = 'text', 'Text'
    EMAIL = 'email', 'Email'
    NUMBER = 'number', 'Number'
    TEXTAREA = 'textarea', 'Textarea'
    SELECT = 'select', 'Select'
    RADIO = 'radio', 'Radio'
    CHECKBOX = 'checkbox', 'Checkbox'
    DATE = 'date', 'Date'
    TIME = 'time', 'Time'
    PHONE = 'phone', 'Phone'
    URL = 'url', 'URL'
    PASSWORD = 'password', 'Password'
    HIDDEN = 'hidden', 'Hidden'
    FILE = 'file', 'File'
    SELECT_FACULTE = 'select_faculte', 'Select Faculte'
    SELECT_DOMAINE = 'select_domaine', 'Select Domaine'
    SELECT_SPECIALITE = 'select_specialite', 'Select Specialite'
    SELECT_ETABLISSEMENT = 'select_etablissement', 'Select Etablissement'
    PANEL = 'panel', 'Panel (Field Group)'


class SubmissionStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class Form(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    form_type = models.CharField(max_length=20, choices=FormType.choices, default=FormType.REGISTRATION)
    status = models.CharField(max_length=20, choices=FormStatus.choices, default=FormStatus.DRAFT)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    access_level = models.CharField(max_length=20, choices=FormAccess.choices, default=FormAccess.PUBLIC)
    allow_update = models.BooleanField(default=False, help_text='Allow authenticated users to update their submission')
    single_submission = models.BooleanField(default=False, help_text='Allow only one submission per user')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_forms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='form_images/', blank=True, null=True, help_text='Upload an image for this form')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


class FormField(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=255)
    field_type = models.CharField(max_length=20, choices=FieldType.choices, default=FieldType.TEXT)
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    placeholder = models.CharField(max_length=255, blank=True)
    default_value = models.TextField(blank=True)
    options_json = models.JSONField(default=list, blank=True)
    validation_json = models.JSONField(default=dict, blank=True)
    parent_field = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_fields'
    )
    visible_condition = models.JSONField(default=dict, blank=True, help_text='{"field_name": "value"} for conditional visibility')
    enabled_condition = models.JSONField(default=dict, blank=True, help_text='{"field_name": "value"} for conditional enabling')
    admin_only = models.BooleanField(default=False, help_text='Only admin or facadmin can edit this field')
    icon = models.CharField(max_length=50, blank=True, help_text='Bootstrap icon class (e.g., bi-person, bi-envelope)')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.form.title} - {self.label}"


class FormSubmission(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='submissions')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=SubmissionStatus.choices, default=SubmissionStatus.PENDING)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Submission {self.id} for {self.form.title}"


class FormAnswer(models.Model):
    submission = models.ForeignKey(FormSubmission, on_delete=models.CASCADE, related_name='answers')
    field = models.ForeignKey(FormField, on_delete=models.CASCADE, related_name='answers')
    value_text = models.TextField(blank=True)
    value_json = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Answer for {self.field.label}"


class UploadedFile(models.Model):
    submission = models.ForeignKey(FormSubmission, on_delete=models.CASCADE, related_name='files')
    field = models.ForeignKey(FormField, on_delete=models.CASCADE, related_name='uploaded_files')
    original_filename = models.CharField(max_length=255)
    stored_filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    size_bytes = models.PositiveIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_filename
