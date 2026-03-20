# ⭐ VoteStar — Django Voting Platform

A clean, production-ready voting platform where authenticated users create topics and rate them 1–5 stars.

---

## 📁 Project Structure

```
votestar/
├── config/               # Django project config
│   ├── settings.py       # All settings (env-aware)
│   ├── urls.py           # Root URL dispatcher
│   └── wsgi.py
├── users/                # Custom User model + auth
├── topics/               # Poll/topic CRUD
│   └── templatetags/     # Custom template filters
├── votes/                # Vote create/update/delete
├── notifications/        # DB notifications on topic expiry
├── templates/            # All HTML templates
│   ├── base.html
│   ├── users/
│   ├── topics/
│   ├── votes/
│   └── notifications/
├── static/
│   ├── css/main.css      # Full design system
│   └── js/stars.js       # Star picker UI
├── .env                  # Local secrets (never commit)
├── requirements.txt
├── Procfile              # Heroku process
└── runtime.txt           # Python version for Heroku
```

---

## 🚀 Step-by-Step Local Setup

### 1. Clone / create the project directory

```bash
cd ~/projects
# (copy votestar/ folder here)
cd votestar
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Edit `.env` (already created):

```ini
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

**To use PostgreSQL locally** instead of SQLite:

```bash
# 1. Create the database
createdb votestar_db

# 2. Update .env
DATABASE_URL=postgres://youruser:yourpassword@localhost/votestar_db
```

Generate a strong secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Run database migrations

```bash
python manage.py migrate
```

### 6. Create an admin superuser (optional but recommended)

```bash
python manage.py createsuperuser
# Enter email and password when prompted
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.
Admin panel: http://127.0.0.1:8000/admin

---

## 🧠 Models Design Explained

### `users.User` — Custom User Model
- Extends `AbstractUser`, removes `username`
- `email` is the unique login credential (`USERNAME_FIELD = 'email'`)
- `display_name` property: returns first name or email prefix
- **Why custom?** Django's default user uses username. We want email-only login, which requires replacing the model from the start (cannot be changed after first migration).

### `topics.Topic` — A Poll
- `title`, `description`, `created_by` (FK→User), `created_at`, `end_time`
- `end_time` is **auto-set** in `save()` to `created_at + 72h` — never editable
- `ordering = ['-created_at']` — newest first at the DB level
- Computed properties: `is_active`, `time_remaining`, `average_rating`, `vote_count`

### `votes.Vote` — A User's Rating
- FK to both `User` and `Topic`, each with `CASCADE` (delete user/topic → delete votes)
- `rating`: `PositiveSmallIntegerField` with `MinValueValidator(1)` and `MaxValueValidator(5)`
- `unique_together = ('user', 'topic')` — DB-level guarantee of one vote per user per topic

### `notifications.Notification` — Expiry Alert
- Created lazily when an expired topic's detail page is first viewed
- `get_or_create` makes the creation idempotent (safe to call many times)
- `is_read` toggled to `True` in bulk when the notifications list view is loaded

---

## 🔒 Business Rules — How They're Enforced

| Rule | Where Enforced |
|------|---------------|
| One vote per user per topic | `unique_together` in `Vote.Meta` (DB level) |
| Rating 1–5 only | `MinValueValidator` / `MaxValueValidator` on `Vote.rating` |
| Voting locked after 72h | `topic.is_active` check in every vote view |
| One active topic per user | Query in `topic_create_view` before saving |
| Topic immutable after creation | No edit view exists at all |
| Only owner can delete topic | `topic.created_by != request.user` check in delete view |
| Cascade delete on user | `on_delete=CASCADE` on all FKs to User |
| Notifications not duplicated | `get_or_create` in `maybe_create_expiry_notification` |

---

## 🧪 Running Tests

```bash
python manage.py test
```

Expected output: **38 tests, 0 errors, 0 failures**

Run a single app's tests:
```bash
python manage.py test users
python manage.py test topics
python manage.py test votes
python manage.py test notifications
```

Run with verbose output:
```bash
python manage.py test --verbosity=2
```

**What's tested:**
- `users`: model creation, email uniqueness, display name, register/login/delete views
- `topics`: 72h end time, active/expired state, ordering, one-topic rule, owner-only delete
- `votes`: one vote per user, 72h lock, create/update/withdraw, login required
- `notifications`: created on expiry, not duplicated, marked read on view, cleared

---

## 🎨 Frontend Design

The UI uses a clean **editorial aesthetic**:
- **Font**: Sora (Google Fonts) — modern, geometric, professional
- **Palette**: Indigo (#4f46e5) primary + Amber (#f59e0b) for star ratings + Rose (#f43f5e) for danger
- **Star picker**: Pure vanilla JS — hover preview, click to select, hidden input synced
- **Responsive**: Single-column on mobile (<768px), 2-column on tablets, grid on desktop
- **No frameworks**: No Bootstrap, no Tailwind CDN — just one clean CSS file

---

## 🚀 Heroku Deployment

### Prerequisites
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
- Git repository initialised

### Step-by-step

```bash
# 1. Initialise git (if not done)
git init
git add .
git commit -m "Initial commit"

# 2. Create Heroku app
heroku create your-app-name

# 3. Add PostgreSQL addon (free tier)
heroku addons:create heroku-postgresql:essential-0

# 4. Set environment variables
heroku config:set SECRET_KEY="$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
# DATABASE_URL is set automatically by the PostgreSQL addon

# 5. Deploy
git push heroku main

# 6. Run migrations on Heroku
heroku run python manage.py migrate

# 7. Create superuser on Heroku
heroku run python manage.py createsuperuser

# 8. Collect static files (WhiteNoise serves them)
heroku run python manage.py collectstatic --noinput

# 9. Open the app
heroku open
```

### What each deployment file does

| File | Purpose |
|------|---------|
| `Procfile` | Tells Heroku to run `gunicorn config.wsgi` as the web process |
| `runtime.txt` | Pins Python version to 3.12.3 |
| `requirements.txt` | All pip dependencies Heroku installs |
| `whitenoise` | Serves static files directly from Django — no S3 needed |
| `dj-database-url` | Parses `DATABASE_URL` env var into Django `DATABASES` dict |

### Production settings that activate when `DEBUG=False`
- `SECURE_SSL_REDIRECT = True` — force HTTPS
- `SECURE_HSTS_SECONDS = 31536000` — HTTP Strict Transport Security
- `SESSION_COOKIE_SECURE = True` — cookie only over HTTPS
- `CSRF_COOKIE_SECURE = True` — CSRF token only over HTTPS
- WhiteNoise `CompressedManifestStaticFilesStorage` — gzip + cache-busting hashes

---

## 🔗 URL Reference

| URL | View | Auth Required |
|-----|------|:---:|
| `/` | Topic list | No |
| `/topics/create/` | Create topic | ✅ |
| `/topics/<pk>/` | Topic detail | No |
| `/topics/<pk>/delete/` | Delete topic | ✅ (owner) |
| `/users/register/` | Register | No |
| `/users/login/` | Login | No |
| `/users/logout/` | Logout | ✅ |
| `/users/profile/` | Profile + votes | ✅ |
| `/users/delete/` | Delete account | ✅ |
| `/votes/<topic_pk>/cast/` | Cast vote | ✅ |
| `/votes/<topic_pk>/update/` | Update vote | ✅ |
| `/votes/<topic_pk>/withdraw/` | Delete vote | ✅ |
| `/notifications/` | View notifications | ✅ |
| `/notifications/clear/` | Clear all | ✅ |
| `/admin/` | Django admin | ✅ (staff) |
