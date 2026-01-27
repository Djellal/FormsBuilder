# Ufas1Forms - Dynamic Form Builder Project Context

## Project Overview

Ufas1Forms is a Django-based web application designed for creating dynamic forms for registration, surveys, and data collection. It provides a comprehensive solution for managing different types of forms with advanced features like cascading dropdowns, conditional logic, and academic field types.

### Key Technologies
- **Framework**: Django 6.0.1 (Python)
- **Database**: PostgreSQL (configured as default)
- **Frontend**: HTML templates with Bootstrap 5
- **Authentication**: Django's built-in auth system with custom groups
- **Internationalization**: Multi-language support (Arabic, French, English)
- **File Storage**: Media file handling with Pillow

### Architecture
The project follows a modular Django application structure with two main apps:
- `forms_builder`: Core functionality for form creation, submission, and management
- `academic`: Academic structure models (Etablissement, Faculte, Domaine, Specialite)

## Project Structure

```
FormsBuilder/
├── ufas1forms/          # Django project settings and configuration
├── forms_builder/       # Main forms application
│   ├── models.py        # Form, FormField, FormSubmission, FormAnswer, UploadedFile
│   ├── views.py         # All views and API endpoints
│   ├── forms.py         # Form classes for user registration and form creation
│   ├── urls.py          # URL routing for forms
│   ├── apps.py          # App configuration
│   ├── context_processors.py  # Custom context processors
│   └── management/      # Custom management commands
│       └── commands/    # Seed data commands
├── academic/            # Academic structure app
│   ├── models.py        # Etablissement, Faculte, Domaine, Specialite models
│   ├── admin.py         # Admin configurations
│   ├── apps.py          # App configuration
│   └── management/      # Custom management commands
│       └── commands/    # Seed academic data command
├── templates/           # HTML templates
├── static/              # CSS and JavaScript files
├── media/               # Uploaded files storage
├── staticfiles/         # Static files collected for production
├── manage.py            # Django management script
├── README.md            # Project documentation
├── requirements.txt     # Python dependencies
├── QWEN.md              # Project context for AI assistants
├── deploy.sh            # Deployment script
├── ufas1forms_apache.conf          # Apache configuration
├── ufas1forms_apache_proxy.conf    # Apache proxy configuration
└── venv/                # Virtual environment
```

## Core Models

### Form Models
- `Form`: Represents a form with title, description, type, status, and access level
  - Includes image upload capability for form branding
  - Supports single submission and update permissions
  - Uses UUID-based slugs for unique identification
- `FormField`: Individual form fields with type, validation, and conditional logic
  - Supports 19 different field types including academic-specific ones
  - Includes parent-child relationships for cascading dropdowns
  - Supports conditional visibility and enabling based on other field values
  - Allows admin-only fields that only certain users can edit
- `FormSubmission`: Records of form submissions
  - Tracks IP address and user agent for security
  - Supports different submission statuses (pending, approved, rejected)
- `FormAnswer`: Individual field answers within submissions
  - Stores text values and JSON data separately
- `UploadedFile`: File uploads associated with form submissions
  - Tracks original and stored filenames, content type, and size

### Academic Models
- `Etablissement`: Educational institution (University level)
- `Faculte`: Faculty within an institution (College level)
- `Domaine`: Academic domain within a faculty (Department level)
- `Specialite`: Specialization within a domain (Major level)

## Features

### Form Types
- Registration forms
- Survey forms
- Data collection forms

### Field Types (19 total)
- Basic: text, email, number, textarea, password, hidden
- Selection: select, radio, checkbox
- Specialized: date, time, phone, url, file
- Academic: select_etablissement, select_faculte, select_domaine, select_specialite
- Layout: panel (for grouping fields)

### Advanced Features
- **Cascading Dropdowns**: Parent-child relationships between select fields
- **Conditional Logic**: Fields visible/enabled based on other field values
- **Visual Form Builder**: Drag-and-drop interface for form creation
- **Multiple Access Levels**: Public and authenticated-only forms
- **Submission Management**: Track, view, and export responses
- **File Upload Support**: Handle file attachments in forms
- **CSV Export**: Export form responses for analysis
- **Multi-language Support**: Arabic (primary), French, and English
- **Image Upload**: Forms can have associated images
- **Field Icons**: Bootstrap icons can be added to fields
- **Panel Grouping**: Fields can be grouped into panels for better organization

## User Roles
- `admin`: System administrators with full access
- `facadmin`: Faculty administrators (mentioned in docs)
- `student`: Regular users for form submission

## Building and Running

### Prerequisites
- Python 3.x
- PostgreSQL database
- Virtual environment recommended

### Setup Instructions
```bash
# Navigate to project directory
cd /home/djellal/workspace/FormsBuilder

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (if needed)
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Load academic data (optional)
python manage.py seed_academic_data

# Load sample form (optional)
python manage.py seed_inscription_form

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
- Follow internationalization best practices

### Model Design
- Use Django's built-in User model for authentication
- Leverage Django's choice fields for standardized options
- Use UUIDs for unique identifiers when needed
- Implement proper foreign key relationships
- Use JSON fields for flexible option storage

### Views and URLs
- Use Django's generic views where appropriate
- Implement proper permission checking with mixins
- Use RESTful URL patterns
- Return JSON responses for AJAX endpoints
- Implement proper error handling and user feedback

### Security Considerations
- Validate user permissions before allowing access to forms/submissions
- Sanitize user inputs
- Implement CSRF protection (Django default)
- Secure file uploads with proper validation
- Protect against SQL injection and XSS attacks

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
- `/fields/<int:field_pk>/` - Get field details

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
- `/api/specialites/` - Get list of specialities (filterable by domain)
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
- AdminRequiredMixin mixin restricts access to authorized users

### Multi-language Support
- Arabic is the default language
- Support for French and English
- Translation-ready templates using Django's i18n framework
- Language switcher available in the UI

### Panel Grouping
- Fields can be organized into panels for better UX
- Panels are a special field type that groups other fields
- Improves form organization and usability

### File Handling
- Uploaded files are stored with unique names to prevent conflicts
- File metadata (original name, content type, size) is preserved
- Files can be associated with specific form fields and submissions

### Academic Data Seeding
- Custom management command to populate academic hierarchy
- Creates realistic university structure with faculties, domains, and specialities
- Sample data includes University Ferhat Abbas Sétif 1 with multiple faculties

### Form Seeding
- Custom management command to create a sample master's inscription form
- Includes all necessary fields for academic registration
- Demonstrates the use of academic-specific field types

This project provides a robust foundation for creating and managing dynamic forms with advanced features tailored for academic institutions, with strong support for multi-language interfaces and complex academic hierarchies.