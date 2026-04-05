# Grievance Redressal System

A web-based grievance redressal system built with Django, developed as a WPL mini-project. The system allows students to submit complaints and enables designated grievance officers to review, update, and resolve them.

## Features

- **Student portal** — Register, submit complaints by category and department, track status, download complaint PDF
- **Grievance officer portal** — Review all complaints, update status, add remarks, view audit history
- **Role-based access** — Student, teaching staff, non-teaching staff, and grievance officer roles
- **Audit trail** — Full history of every status change with timestamps
- **Email activation** — Account activation via email link on registration
- **PDF export** — Generate formatted complaint PDFs with full status history

## Tech Stack

- Python 3.12 / Django 4.2
- SQLite (development) / PostgreSQL (production)
- Bootstrap 4
- ReportLab (PDF generation)

## Setup

**1. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

**2. Install dependencies**
```bash
pip install "Django==4.2.*" django-crispy-forms crispy-bootstrap4 reportlab Pillow django-extensions django-allauth django-phonenumber-field phonenumberslite
```

**3. Apply migrations**
```bash
cd GRsytemproject/web
python manage.py migrate
```

**4. Create a superuser (grievance officer)**
```bash
python manage.py createsuperuser
```
Then go to `/admin/` and set the user's Profile `type_user` to `grievance`.

**5. Run the development server**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`

## Project Structure

```
GRsytemproject/
└── web/
    ├── GRsystem/          # Main app
    │   ├── models.py      # Complaint, Profile, ComplaintHistory
    │   ├── views.py       # Student and officer views
    │   ├── forms.py       # Registration and complaint forms
    │   ├── templates/     # HTML templates
    │   └── migrations/    # Database migrations
    └── web/
        ├── settings.py
        └── urls.py
```

## User Roles

| Role | Access |
|------|--------|
| `student` | Submit complaints, track own complaints, download PDFs |
| `teaching_staff` | Same as student |
| `non_teaching_staff` | Same as student |
| `grievance` | View all complaints, update status, add remarks |
