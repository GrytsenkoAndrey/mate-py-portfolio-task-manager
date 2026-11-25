# mate-py-portfolio-task-manager

A task manager for an IT company, built with Django. Workers are grouped
into teams, each team works on projects, and each project has tasks
with a type, priority, deadline and tags.

## Features

- **Dashboard**: open, completed and overdue task counts, upcoming
  deadlines, progress for each project, open tasks per priority and
  "my tasks" (tasks from the projects of the current user's teams).
- **Workers**: a custom user model (`manager.Worker`) with a position,
  plus a profile page and a profile edit form (including a password change).
- **Teams**: create, edit and delete teams and manage their members.
- **Projects**: create, edit and delete projects. Each project has a
  team and a deadline, and its detail page shows task progress and the team.
- **Tasks**: create, edit and delete tasks with a type, a priority
  (Urgent / High / Normal / Low), a deadline, tags and a completion status.
- **Tags**: add, rename and delete tags.
- Authentication: every page requires login (Django's built-in auth views).

## Tech stack

- Python 3.14, Django 6.1
- SQLite
- Bootstrap 5, `django-crispy-forms` + `crispy-bootstrap5`
- `django-debug-toolbar`, `whitenoise`
- `flake8` and `black` for code style

## Project structure

```
manage.py
mate_py_porfolio_task_manager/   # project settings and root urls
manager/                         # main app: models, views, forms, urls
  ├── enums.py                   # positions, task types, priorities
  ├── fixtures/                  # sample data
  └── templatetags/ru_plural.py  # Russian plural forms filter
templates/                       # HTML templates
static/                          # CSS and JS
```

## Run locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd mate-py-porfolio-task-manager
```

### 2. Create a virtual environment and install dependencies

With `pip`:

```bash
python3.14 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv venv --python 3.14
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Replace the example `DJANGO_SECRET_KEY` with a unique secret (for example,
generate one with `openssl rand -base64 48`). Set `DJANGO_DEBUG` to `True` for
local development or `False` for production. The `.env` file is ignored by Git.

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Load sample data (optional)

```bash
python manage.py loaddata initial_data projects_data
```

- `initial_data` adds positions and task types (taken from `manager/enums.py`).
- `projects_data` adds sample workers, teams and projects. It depends on
  the positions from `initial_data`, so load both together.

All sample workers have the password `Password123!`. For example, you
can log in as `a.koval`.

### 6. Create an admin user (optional)

A worker must have a position, and `createsuperuser` doesn't ask for
one, so create the superuser in the Django shell (after step 4, or
after creating a `Position` yourself):

```bash
python manage.py shell
```

```python
from manager.models import Position, Worker

position = Position.objects.first()
Worker.objects.create_superuser(
    username="admin",
    email="admin@example.com",
    password="admin12345",
    position=position,
)
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ and log in. The Django admin is at
http://127.0.0.1:8000/admin/.

## Code style

```bash
flake8 manager/
black .
```

## Notes

- `SECRET_KEY` and `DEBUG` are read from `DJANGO_SECRET_KEY` and
  `DJANGO_DEBUG`; settings load these values from `.env` for local development.
  Before deploying, set `DJANGO_DEBUG=False`, configure `ALLOWED_HOSTS`, and
  run `python manage.py collectstatic`.
