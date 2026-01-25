from django.contrib import admin
from .models import Form, FormField, FormSubmission, FormAnswer, UploadedFile


class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 0
    ordering = ['order']


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ['title', 'form_type', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'form_type', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [FormFieldInline]


@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ['label', 'form', 'field_type', 'is_required', 'order']
    list_filter = ['field_type', 'is_required']
    search_fields = ['label', 'name']


class FormAnswerInline(admin.TabularInline):
    model = FormAnswer
    extra = 0
    readonly_fields = ['field', 'value_text']


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'form', 'submitted_by', 'submitted_at', 'status']
    list_filter = ['status', 'submitted_at', 'form']
    search_fields = ['form__title']
    inlines = [FormAnswerInline]


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'submission', 'content_type', 'size_bytes', 'uploaded_at']
    list_filter = ['content_type', 'uploaded_at']
