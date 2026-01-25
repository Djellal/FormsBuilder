# Ufas1Forms - Dynamic Form Builder

A Django web application for creating dynamic forms for registration, surveys, and data collection.

## Quick Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run the development server
python manage.py runserver
```

Visit http://127.0.0.1:8000 and login with:
- **Username:** admin
- **Password:** admin123

## Features

- **Multiple Form Types**: Registration, Survey, and Data Collection forms
- **Dynamic Fields**: 16 field types including text, email, select, radio, checkbox, date, file upload
- **Cascading Dropdowns**: Master/detail select fields with parent-child relationships
- **Academic Fields**: Special field types for Faculte and Domaine selection
- **Conditional Logic**: Visible and Enabled properties based on other field values
- **Visual Form Builder**: Drag-and-drop interface to create and edit forms
- **Response Collection**: Store and view all form submissions
- **CSV Export**: Export responses to CSV for analysis
- **Bootstrap 5 UI**: Modern, responsive design

## User Groups

- `admin` - System administrator (full access)
- `facadmin` - Faculty administrator
- `student` - Student user

## Project Structure

```
FormsBuilder/
├── ufas1forms/          # Django project settings
├── forms_builder/       # Main forms app
│   ├── models.py        # Form, FormField, FormSubmission, etc.
│   ├── views.py         # All views and API endpoints
│   └── urls.py          # URL routing
├── academic/            # Academic structure app
│   └── models.py        # Etablissement, Faculte, Domaine
├── templates/           # HTML templates
└── static/              # CSS and JS files
```

## Field Types

| Type | Description |
|------|-------------|
| text | Single line text input |
| email | Email input with validation |
| number | Numeric input |
| textarea | Multi-line text |
| select | Dropdown selection |
| radio | Radio button group |
| checkbox | Checkbox group |
| date | Date picker |
| time | Time picker |
| phone | Phone number input |
| url | URL input |
| password | Password input |
| hidden | Hidden field |
| file | File upload |
| select_faculte | Faculte dropdown (auto-populated) |
| select_domaine | Domaine dropdown (cascades from Faculte) |

## Cascading Dropdowns

Set `parent_field` on a child Select field and include `parentValue` in options:

```json
[
  {"value": "dept1", "text": "Department 1", "parentValue": "faculty1"},
  {"value": "dept2", "text": "Department 2", "parentValue": "faculty1"},
  {"value": "dept3", "text": "Department 3", "parentValue": "faculty2"}
]
```

## Conditional Visibility/Enabling

Use JSON conditions on fields:

```json
{"field_name": "expected_value"}
```

The field will only be visible/enabled when the referenced field has the expected value.
