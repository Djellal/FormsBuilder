from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.db.models import Count, Max
import csv
import json

from .models import Form, FormField, FormSubmission, FormAnswer, UploadedFile, FormStatus, FieldType, FormAccess
from .forms import StudentRegistrationForm, FormForm, FormUpdateForm
from academic.models import Faculte, Domaine, Specialite
from django.contrib.auth.models import Group
from django.contrib.auth import login


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.groups.filter(name='admin').exists()


def is_admin(user):
    return user.is_staff or user.groups.filter(name='admin').exists()


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    active_forms = Form.objects.filter(status=FormStatus.PUBLISHED)
    return render(request, 'forms_builder/home.html', {'forms': active_forms})


def about(request):
    return render(request, 'forms_builder/about.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            student_group, _ = Group.objects.get_or_create(name='student')
            user.groups.add(student_group)
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Ufas1Forms.')
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    if is_admin(request.user):
        forms = Form.objects.annotate(submission_count=Count('submissions'))
        recent_submissions = FormSubmission.objects.filter(form__created_by=request.user)[:10]
        return render(request, 'forms_builder/dashboard.html', {
            'forms': forms,
            'recent_submissions': recent_submissions,
            'is_admin': True,
        })
    else:
        my_submissions = FormSubmission.objects.filter(submitted_by=request.user).select_related('form')[:20]
        available_forms = Form.objects.filter(status=FormStatus.PUBLISHED)
        return render(request, 'forms_builder/student_dashboard.html', {
            'submissions': my_submissions,
            'available_forms': available_forms,
        })


class FormListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Form
    template_name = 'forms_builder/form_list.html'
    context_object_name = 'forms'

    def get_queryset(self):
        return Form.objects.filter(created_by=self.request.user).annotate(submission_count=Count('submissions'))


class FormCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    form_class = FormForm
    template_name = 'forms_builder/form_create.html'
    success_url = reverse_lazy('form_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Form created successfully!')
        return super().form_valid(form)


class FormUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Form
    template_name = 'forms_builder/form_edit.html'
    fields = ['title', 'description', 'form_type', 'status', 'access_level', 'single_submission', 'allow_update', 'image']
    success_url = reverse_lazy('form_list')

    def test_func(self):
        if not super().test_func():
            return False
        form = self.get_object()
        return form.created_by == self.request.user or self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Form updated successfully!')
        return super().form_valid(form)


class FormDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Form
    template_name = 'forms_builder/form_confirm_delete.html'
    success_url = reverse_lazy('form_list')

    def test_func(self):
        if not super().test_func():
            return False
        form = self.get_object()
        return form.created_by == self.request.user or self.request.user.is_staff


@login_required
def form_builder(request, pk):
    form = get_object_or_404(Form, pk=pk)
    if form.created_by != request.user and not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('form_list')
    
    fields = form.fields.all()
    field_types = FieldType.choices
    return render(request, 'forms_builder/form_builder.html', {
        'form': form,
        'fields': fields,
        'field_types': field_types,
    })


@login_required
def add_field(request, form_pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    form = get_object_or_404(Form, pk=form_pk)
    if form.created_by != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    data = json.loads(request.body)
    max_order = form.fields.aggregate(Max('order'))['order__max'] or 0
    
    field = FormField.objects.create(
        form=form,
        name=data.get('name', '').replace(' ', '_').lower(),
        label=data.get('label', ''),
        field_type=data.get('field_type', 'text'),
        is_required=data.get('is_required', False),
        order=max_order + 1,
        placeholder=data.get('placeholder', ''),
        default_value=data.get('default_value', ''),
        options_json=data.get('options_json', []),
        validation_json=data.get('validation_json', {}),
        visible_condition=data.get('visible_condition', {}),
        enabled_condition=data.get('enabled_condition', {}),
        admin_only=data.get('admin_only', False),
        icon=data.get('icon', ''),
        background_color=data.get('background_color', ''),
    )

    if data.get('parent_field_id'):
        field.parent_field_id = data['parent_field_id']
        field.save()
    
    return JsonResponse({'id': field.id, 'success': True})


@login_required
def update_field(request, field_pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    field = get_object_or_404(FormField, pk=field_pk)
    if field.form.created_by != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    data = json.loads(request.body)
    
    field.name = data.get('name', field.name).replace(' ', '_').lower()
    field.label = data.get('label', field.label)
    field.field_type = data.get('field_type', field.field_type)
    field.is_required = data.get('is_required', field.is_required)
    field.placeholder = data.get('placeholder', field.placeholder)
    field.default_value = data.get('default_value', field.default_value)
    field.options_json = data.get('options_json', field.options_json)
    field.validation_json = data.get('validation_json', field.validation_json)
    field.visible_condition = data.get('visible_condition', field.visible_condition)
    field.enabled_condition = data.get('enabled_condition', field.enabled_condition)
    field.admin_only = data.get('admin_only', field.admin_only)
    field.icon = data.get('icon', field.icon)
    field.background_color = data.get('background_color', field.background_color)

    if 'parent_field_id' in data:
        field.parent_field_id = data['parent_field_id'] or None

    field.save()
    return JsonResponse({'success': True})


@login_required
def delete_field(request, field_pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    field = get_object_or_404(FormField, pk=field_pk)
    if field.form.created_by != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    field.delete()
    return JsonResponse({'success': True})


@login_required
def reorder_fields(request, form_pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    form = get_object_or_404(Form, pk=form_pk)
    if form.created_by != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    data = json.loads(request.body)
    for i, field_id in enumerate(data.get('field_ids', [])):
        FormField.objects.filter(pk=field_id, form=form).update(order=i)

    return JsonResponse({'success': True})


@login_required
def get_field(request, field_pk):
    field = get_object_or_404(FormField, pk=field_pk)
    if field.form.created_by != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)

    # Determine if parent is a panel or a cascading select
    panel_id = None
    cascading_parent_id = None
    if field.parent_field:
        if field.parent_field.field_type == FieldType.PANEL:
            panel_id = field.parent_field.id
        else:
            cascading_parent_id = field.parent_field.id
    
    field_data = {
        'id': field.id,
        'name': field.name,
        'label': field.label,
        'field_type': field.field_type,
        'is_required': field.is_required,
        'placeholder': field.placeholder,
        'default_value': field.default_value,
        'options_json': field.options_json,
        'validation_json': field.validation_json,
        'visible_condition': field.visible_condition,
        'enabled_condition': field.enabled_condition,
        'parent_field_id': cascading_parent_id,
        'panel_id': panel_id,
        'admin_only': field.admin_only,
        'icon': field.icon,
        'background_color': field.background_color,
    }

    return JsonResponse(field_data)


def form_submit_view(request, slug):
    form = get_object_or_404(Form, slug=slug, status=FormStatus.PUBLISHED)
    fields = form.fields.all()
    
    if form.access_level == FormAccess.AUTHENTICATED and not request.user.is_authenticated:
        messages.warning(request, 'You must be logged in to submit this form.')
        return redirect(f'/login/?next=/f/{slug}/')
    
    existing_submission = None
    if request.user.is_authenticated:
        existing_submission = FormSubmission.objects.filter(
            form=form, submitted_by=request.user
        ).first()
        
        if form.single_submission and existing_submission and not form.allow_update:
            messages.info(request, 'You have already submitted this form.')
            return redirect('my_submission', slug=slug)
    
    is_update = existing_submission and form.allow_update
    
    if request.method == 'POST':
        if is_update:
            submission = existing_submission
            submission.answers.all().delete()
            submission.files.all().delete()
        else:
            submission = FormSubmission.objects.create(
                form=form,
                submitted_by=request.user if request.user.is_authenticated else None,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            )
        
        for field in fields:
            value = request.POST.get(f'field_{field.id}', '')
            
            if field.field_type == FieldType.CHECKBOX:
                values = request.POST.getlist(f'field_{field.id}')
                FormAnswer.objects.create(
                    submission=submission,
                    field=field,
                    value_text=','.join(values),
                    value_json={'values': values},
                )
            elif field.field_type == FieldType.FILE:
                uploaded_file = request.FILES.get(f'field_{field.id}')
                existing_file = request.POST.get(f'existing_file_{field.id}')
                if uploaded_file:
                    import uuid
                    stored_name = f"{uuid.uuid4().hex}_{uploaded_file.name}"
                    from django.conf import settings
                    import os
                    os.makedirs(settings.MEDIA_ROOT / 'uploads', exist_ok=True)
                    with open(settings.MEDIA_ROOT / 'uploads' / stored_name, 'wb+') as dest:
                        for chunk in uploaded_file.chunks():
                            dest.write(chunk)
                    
                    UploadedFile.objects.create(
                        submission=submission,
                        field=field,
                        original_filename=uploaded_file.name,
                        stored_filename=stored_name,
                        content_type=uploaded_file.content_type,
                        size_bytes=uploaded_file.size,
                    )
                    FormAnswer.objects.create(
                        submission=submission,
                        field=field,
                        value_text=stored_name,
                    )
                elif existing_file:
                    FormAnswer.objects.create(
                        submission=submission,
                        field=field,
                        value_text=existing_file,
                    )
            else:
                FormAnswer.objects.create(
                    submission=submission,
                    field=field,
                    value_text=value,
                )
        
        if is_update:
            messages.success(request, 'Your submission has been updated!')
        else:
            messages.success(request, 'Form submitted successfully!')
        return redirect('form_success', slug=slug)
    
    prefill_data = {}
    if is_update:
        for answer in existing_submission.answers.all():
            prefill_data[answer.field_id] = answer.value_text
    
    is_admin_user = request.user.is_authenticated and (
        request.user.is_staff or 
        request.user.groups.filter(name__in=['admin', 'facadmin']).exists()
    )
    
    # Organize fields: panels with their children, and standalone fields
    # First, prefetch all fields with their parent relationships
    fields = list(form.fields.select_related('parent_field').all())
    
    panels = []
    standalone_fields = []
    panel_children = {}  # panel_id -> list of child fields
    panel_ids = set()
    
    # First pass: identify all panels
    for field in fields:
        if field.field_type == FieldType.PANEL:
            panels.append(field)
            panel_ids.add(field.id)
            panel_children[field.id] = []
    
    # Second pass: categorize fields
    for field in fields:
        if field.field_type == FieldType.PANEL:
            continue  # Already handled
        elif field.parent_field_id and field.parent_field_id in panel_ids:
            panel_children[field.parent_field_id].append(field)
        else:
            standalone_fields.append(field)
    
    # Attach children to panels
    for panel in panels:
        panel.panel_fields = panel_children.get(panel.id, [])
    
    return render(request, 'forms_builder/form_submit.html', {
        'form': form,
        'fields': fields,
        'panels': panels,
        'standalone_fields': standalone_fields,
        'is_update': is_update,
        'prefill_data': prefill_data,
        'is_admin_user': is_admin_user,
    })


@login_required
def my_submission(request, slug):
    form = get_object_or_404(Form, slug=slug)
    submission = get_object_or_404(FormSubmission, form=form, submitted_by=request.user)
    answers = submission.answers.all().select_related('field')
    
    return render(request, 'forms_builder/my_submission.html', {
        'form': form,
        'submission': submission,
        'answers': answers,
    })


def form_success(request, slug):
    form = get_object_or_404(Form, slug=slug)
    return render(request, 'forms_builder/form_success.html', {'form': form})


@login_required
def submission_list(request, form_pk):
    form = get_object_or_404(Form, pk=form_pk)
    if form.created_by != request.user and not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('form_list')
    
    submissions = form.submissions.all().prefetch_related('answers', 'answers__field')
    return render(request, 'forms_builder/submission_list.html', {
        'form': form,
        'submissions': submissions,
    })


@login_required
def submission_detail(request, pk):
    submission = get_object_or_404(FormSubmission, pk=pk)
    if submission.form.created_by != request.user and not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('form_list')

    # Check if the current user is an admin
    is_admin = request.user.is_staff or request.user.groups.filter(name='admin').exists()

    # Get all fields and answers for the form
    fields = submission.form.fields.select_related('parent_field').all()
    answers = submission.answers.all().select_related('field')

    # Create a mapping of field_id to answer for easy lookup
    answer_map = {answer.field_id: answer for answer in answers}

    # Organize fields: panels with their children, and standalone fields
    panels = []
    standalone_answers = []
    panel_children = {}  # panel_id -> list of child answers
    panel_ids = set()

    # First pass: identify all panels
    for field in fields:
        if field.field_type == FieldType.PANEL:
            panels.append(field)
            panel_ids.add(field.id)
            panel_children[field.id] = []

    # Second pass: categorize answers
    for answer in answers:
        field = answer.field
        if field.field_type == FieldType.PANEL:
            continue  # Skip panel fields themselves
        elif field.parent_field_id and field.parent_field_id in panel_ids:
            # Create a tuple of (answer, field) to pass both objects
            panel_children[field.parent_field_id].append((answer, field))
        else:
            # Create a tuple of (answer, field) to pass both objects
            standalone_answers.append((answer, field))

    # Attach children to panels
    for panel in panels:
        panel.panel_answers = panel_children.get(panel.id, [])

    files = submission.files.all()
    return render(request, 'forms_builder/submission_detail.html', {
        'submission': submission,
        'panels': panels,
        'standalone_answers': standalone_answers,
        'files': files,
        'is_admin': is_admin,
    })


@login_required
def export_csv(request, form_pk):
    form = get_object_or_404(Form, pk=form_pk)
    if form.created_by != request.user and not request.user.is_staff:
        return HttpResponse('Access denied', status=403)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{form.slug}_submissions.csv"'
    
    writer = csv.writer(response)
    fields = form.fields.all()
    headers = ['Submission ID', 'Submitted At', 'Status'] + [f.label for f in fields]
    writer.writerow(headers)
    
    for submission in form.submissions.all():
        row = [submission.id, submission.submitted_at, submission.status]
        answer_dict = {a.field_id: a.value_text for a in submission.answers.all()}
        for field in fields:
            row.append(answer_dict.get(field.id, ''))
        writer.writerow(row)
    
    return response


def api_facultes(request):
    facultes = Faculte.objects.all().values('id', 'nom')
    return JsonResponse(list(facultes), safe=False)


def api_domaines(request):
    faculte_id = request.GET.get('faculte_id')
    domaines = Domaine.objects.all()
    if faculte_id:
        domaines = domaines.filter(faculte_id=faculte_id)
    return JsonResponse(list(domaines.values('id', 'nom', 'faculte_id')), safe=False)


def api_specialites(request):
    domaine_id = request.GET.get('domaine_id')
    specialites = Specialite.objects.all()
    if domaine_id:
        specialites = specialites.filter(domaine_id=domaine_id)
    return JsonResponse(list(specialites.values('id', 'nom', 'domaine_id')), safe=False)


def api_child_options(request, field_pk):
    parent_value = request.GET.get('parent_value', '')
    field = get_object_or_404(FormField, pk=field_pk)

    options = [opt for opt in field.options_json if opt.get('parentValue') == parent_value]
    return JsonResponse(options, safe=False)


@login_required
def update_answer(request, pk, answer_id):
    """Update an individual answer for admin-only fields"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    answer = get_object_or_404(FormAnswer, pk=answer_id)

    # Check if the user has permission to edit this answer
    if answer.submission.form.created_by != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)

    # Check if the field is admin_only
    if not answer.field.admin_only:
        return JsonResponse({'error': 'Only admin-only fields can be edited here'}, status=403)

    new_value = request.POST.get('value', '')

    # Handle checkbox specially
    if answer.field.field_type == 'checkbox':
        new_value = '1' if request.POST.get('value') else '0'

    answer.value_text = new_value
    answer.save()

    messages.success(request, f'Updated {answer.field.label} successfully!')
    return redirect('submission_detail', pk=pk)
