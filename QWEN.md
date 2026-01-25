# Ufas1Forms - Dynamic Form Builder Project Context

## Project Overview

Ufas1Forms is a Django-based web application designed for creating dynamic forms for registration, surveys, and data collection. It provides a comprehensive solution for managing different types of forms with advanced features like cascading dropdowns, conditional logic, and academic field types.

### Key Technologies
- **Framework**: Django (Python)
- **Database**: SQLite (default, configurable)
- **Frontend**: HTML templates with Bootstrap 5
- **Authentication**: Django's built-in auth system with custom groups

### Architecture
The project follows a modular Django application structure with two main apps:
- `forms_builder`: Core functionality for form creation, submission, and management
- `academic`: Academic structure models (Etablissement, Faculte, Domaine)

## Project Structure

```
FormsBuilder/
├── ufas1forms/          # Django project settings and configuration
├── forms_builder/       # Main forms application
│   ├── models.py        # Form, FormField, FormSubmission, FormAnswer, UploadedFile
│   ├── views.py         # All views and API endpoints
│   ├── urls.py          # URL routing for forms
│   └── apps.py          # App configuration
├── academic/            # Academic structure app
│   ├── models.py        # Etablissement, Faculte, Domaine models
│   └── apps.py          # App configuration
├── templates/           # HTML templates
├── static/              # CSS and JavaScript files
├── media/               # Uploaded files storage
├── manage.py            # Django management script
├── README.md            # Project documentation
└── venv/                # Virtual environment
```

## Core Models

### Form Models
- `Form`: Represents a form with title, description, type, status, and access level
- `FormField`: Individual form fields with type, validation, and conditional logic
- `FormSubmission`: Records of form submissions
- `FormAnswer`: Individual field answers within submissions
- `UploadedFile`: File uploads associated with form submissions

### Academic Models
- `Etablissement`: Educational institution
- `Faculte`: Faculty within an institution
- `Domaine`: Academic domain within a faculty

## Features

### Form Types
- Registration forms
- Survey forms
- Data collection forms

### Field Types (16 total)
- Basic: text, email, number, textarea, password, hidden
- Selection: select, radio, checkbox
- Specialized: date, time, phone, url, file
- Academic: select_faculte, select_domaine (with cascading functionality)

### Advanced Features
- **Cascading Dropdowns**: Parent-child relationships between select fields
- **Conditional Logic**: Fields visible/enabled based on other field values
- **Visual Form Builder**: Drag-and-drop interface for form creation
- **Multiple Access Levels**: Public and authenticated-only forms
- **Submission Management**: Track, view, and export responses
- **File Upload Support**: Handle file attachments in forms
- **CSV Export**: Export form responses for analysis

## User Roles
- `admin`: System administrators with full access
- `facadmin`: Faculty administrators (mentioned in docs)
- `student`: Regular users for form submission

## Building and Running

### Prerequisites
- Python 3.x
- Django (version inferred from codebase)
- Virtual environment recommended

### Setup Instructions
```bash
# Navigate to project directory
cd /home/djellal/workspace/FormsBuilder

# Activate virtual environment
source venv/bin/activate

# Run migrations (if needed)
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Default Credentials
- **Username**: admin
- **Password**: admin123

### Access Points
- Application: http://127.0.0.1:8000
- Admin panel: http://127.0.0.1:8000/admin

## Development Conventions

### Coding Standards
- Follow Django best practices
- Use class-based views for CRUD operations
- Implement proper authentication decorators/mixins
- Use JSON fields for flexible data storage

### Model Design
- Use Django's built-in User model for authentication
- Leverage Django's choice fields for standardized options
- Use UUIDs for unique identifiers when needed
- Implement proper foreign key relationships

### Views and URLs
- Use Django's generic views where appropriate
- Implement proper permission checking with mixins
- Use RESTful URL patterns
- Return JSON responses for AJAX endpoints

### Security Considerations
- Validate user permissions before allowing access to forms/submissions
- Sanitize user inputs
- Implement CSRF protection (Django default)
- Secure file uploads with proper validation

## API Endpoints

### Form Management
- `/forms/` - List forms
- `/forms/create/` - Create new form
- `/forms/<int:pk>/edit/` - Update form
- `/forms/<int:pk>/delete/` - Delete form
- `/forms/<int:pk>/builder/` - Visual form builder

### Field Management
- `/forms/<int:form_pk>/add-field/` - Add field to form
- `/fields/<int:field_pk>/update/` - Update field
- `/fields/<int:field_pk>/delete/` - Delete field
- `/forms/<int:form_pk>/reorder-fields/` - Reorder fields

### Submissions
- `/forms/<int:form_pk>/submissions/` - View form submissions
- `/submissions/<int:pk>/` - View specific submission
- `/forms/<int:form_pk>/export/` - Export submissions as CSV

### Public Form Access
- `/f/<slug:slug>/` - Submit form publicly
- `/f/<slug:slug>/success/` - Success page after submission
- `/f/<slug:slug>/my-submission/` - View user's submission

### Academic API
- `/api/facultes/` - Get list of faculties
- `/api/domaines/` - Get list of domains (filterable by faculty)
- `/api/fields/<int:field_pk>/options/` - Get child options for cascading dropdowns

## Key Implementation Details

### Conditional Logic
Fields can be conditionally visible or enabled based on other field values using JSON conditions:
```json
{"field_name": "expected_value"}
```

### Cascading Dropdowns
Child select fields can be linked to parent fields with parent-child relationships defined in options:
```json
[
  {"value": "dept1", "text": "Department 1", "parentValue": "faculty1"},
  {"value": "dept2", "text": "Department 2", "parentValue": "faculty1"}
]
```

### Form Access Control
- Forms can be set to public or authenticated-only access
- Permissions are enforced through Django's authentication system
- Form creators can only access their own forms (except admins)

This project provides a robust foundation for creating and managing dynamic forms with advanced features tailored for academic institutions.