# VoteStar
``` Django Voting Platform ```

Voting platform where authenticated users create topics and rate them 1–5 stars.

![The website is responsive](/images-readme/mockup.jpg)

---

## Goals
The goal of Votestar website is to provide a reliable and user-friendly online platform that allows users to share and explore opinions on various topics, helping people make informed decisions based on community feedback. The website aims to enhance the user experience through the following features:

-   Allow users to create new voting topics, specifying the subject they want to evaluate, such as a local business, a transportation service, a story, or a movie.
-   Enable users to cast their votes on existing topics, expressing their opinion clearly and effectively.
-   Implement a 72-hour voting window for each topic, after which voting is closed and results are displayed automatically.
-   Allow users to edit or delete their votes before the 72-hour period expires, giving flexibility to change opinions.
-   Display voting results in an organized and transparent manner, making it easy for users to understand community trends and insights.
-   Provide user registration and personal accounts to manage votes and track participation history efficiently.
-   Serve as a trustworthy reference platform for people who want to gain an understanding of others’ experiences and opinions before making decisions.

---

##  Step-by-Step Local Setup

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
SECRET_KEY=your-very-secret-key-here
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

## Models Design Explained

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

## Business Rules — How They're Enforced

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

## Running Tests

### unit test for python code.

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

## Design

### FrontEnd Design

The UI uses a clean **editorial aesthetic**:
- **Font**: Sora (Google Fonts) — modern, geometric, professional
- **Palette**: Indigo (#4f46e5) primary + Amber (#f59e0b) for star ratings + Rose (#f43f5e) for danger
- **Star picker**: Pure vanilla JS — hover preview, click to select, hidden input synced
- **Responsive**: Single-column on mobile (<768px), 2-column on tablets, grid on desktop
- **No frameworks**: No Bootstrap, no other css library - just one CSS file

---

## Wireframe

- Desktop wireframe:

-   Home page
-   ![home page](/images-readme/index_wireframe.jpg)
-   Profile page
-   ![profile page](/images-readme/profile_wireframe.jpg)
-   Topic details page
-   ![register page](/images-readme/topic_wireframe.jpg)
-   Login page
-   ![register page](/images-readme/login_wireframe.jpg)
-   Register page
-   ![register page](/images-readme/register_wireframe.jpg)

---

- Mobile wireframe:
   ![home page](/images-readme/index_wireframe_m.jpg)
   ![profile page](/images-readme/profile_wireframe_m.jpg)
   ![register page](/images-readme/topic_wireframe_m.jpg)
   ![register page](/images-readme/login_wireframe_m.jpg)
  ![register page](/images-readme/register_wireframe_m.jpg)

---

## Key Features

- Home Page

  - The homepage displays all active and closed topics in a clean card-based layout, ordered by newest first. Each card shows the topic title, description, vote count, average star rating, and time remaining.
    ![Home Page](/images-readme/homepage.jpg)

  ---

  - Active topics are clearly marked with a green **● Live** badge, while expired topics show a **✓ Closed** badge. Users can instantly see their own vote on each card.
    ![Topic Cards](/images-readme/card.jpg)

---

- Register Page

  - A simple and clean registration form allowing new users to join VoteStar with minimal effort.
  - Fields include:
    - Email address
    - First name (optional)
    - Password
    - Password confirmation
  - Existing users are directed to the login page via the link: **_Already have an account? Log in._**
    ![Register Page](/images-readme/register.jpg)

---

- Login Page

  - Clean, minimal login form using email and password.
  - A prominent **Login** button for quick access.
  - New users are guided to the registration page via a clear call-to-action link.
    ![Login Page](/images-readme/login.jpg)

---

- Topic Detail Page

  - Full topic details including title, description, author, creation date, and time remaining.
  - A live **stats row** showing total votes, average star rating, and open/closed status.
  - A **rating distribution bar chart** showing how votes are spread across 1–5 stars.
  - Topic owner has access to a **Delete Topic** button exclusively visible to them.
    ![Topic Detail](/images-readme/topicdetail.jpg)

  ---

  - **Voting Panel** — authenticated users can:
    - Cast a new vote using an interactive **star picker** (1–5 stars).
    - Update their existing vote at any time while the topic is active.
    - Withdraw their vote with a single click.
  - Voting is automatically **locked after 72 hours** — the panel switches to a closed state.
    ![Vote Panel](/images-readme/votepanel.jpg)

  ---

  - Guest users (not logged in) see a friendly prompt inviting them to log in or register before voting.
    ![Guest Panel](/images-readme/guestpanel.jpg)

---

- Profile Page

  - Displays the user's name, email, and member-since date with an avatar initial.
  - **My Topics** section lists all topics the user has created with live/closed status and average rating.
  - **My Votes** section shows every topic the user has voted on, their given rating, and a direct link to update it if still active.
    ![Profile Page](/images-readme/profilepage.jpg)

  ---

  - **Danger Zone** — users can permanently delete their account. This action cascades and removes all their topics, votes, and notifications automatically.
  - Admin accounts display a **🔒 Admin accounts are protected** badge instead of the delete button — superuser accounts cannot be deleted by anyone.
    ![Danger Zone](/images-readme/dangerzone.jpg)

---

- Notifications Page

  - Users receive automatic notifications when a topic they created or voted on reaches its 72-hour expiry.
  - Unread notifications are highlighted with a blue left border and counted in the navbar bell icon **🔔**.
  - All notifications are marked as read automatically upon visiting the page.
  - A **Clear All** button allows users to remove all notifications at once.
    ![Notifications Page](/images-readme/notificationspage.jpg)

---

## Admin Page

- This is the Django admin dashboard, a built-in feature that allows superusers to manage and interact with all VoteStar models and data from the web interface.
  - Site administration panel:
    - This panel gives superusers full access to manage all sections of the VoteStar application.
  - Sections and Models:
    - AUTHENTICATION AND AUTHORIZATION:
      - Groups: Manage user groups and permissions.
      - Users: Add, view, edit, or delete user accounts. Superuser accounts are **protected from deletion** — the delete button is hidden entirely for admin accounts.
    - TOPICS:
      - Topics: View, search, and manage all topics created by users. Each topic displays its title, creator, creation date, expiry time, active status, and total vote count.
    - VOTES:
      - Votes: View and manage all votes cast by users. Each vote shows the voter's email, the topic voted on, the star rating (1–5), and timestamps for creation and last update.
    - NOTIFICATIONS:
      - Notifications: Manage all system notifications. Each notification shows the recipient user, the related topic, the message content, read/unread status, and creation date.
    - Recent Actions Panel:
      - On the right side, it displays a list of recent actions performed by the logged-in admin, such as adding, changing, or deleting topics, votes, or notifications.
    - Header:
      - The header includes links for the admin to view the live site, change their password, and log out.

    ---

    - This is the **Topic management** page in the Django admin interface. It allows the admin to view all topics with the following details:
      - **Title:** The topic's question or subject.
      - **Created By:** The user who created the topic.
      - **Created At:** The date and time the topic was created.
      - **End Time:** The exact time voting closes (72 hours after creation).
      - **Is Active:** Whether voting is currently open or closed.
      - **Vote Count:** The total number of votes the topic has received.

    ---

    - This is the **Vote management** page in the Django admin interface. It displays all votes cast across all topics:
      - **User:** The email of the voter.
      - **Topic:** The topic that was voted on.
      - **Rating:** The star rating given (1–5).
      - **Created At:** When the vote was first cast.
      - **Updated At:** When the vote was last modified.

    ---

    - This is the **User management** page in the Django admin interface. It allows the admin to view and manage all registered users:
      - **Email:** The user's unique login credential.
      - **First Name:** The user's display name.
      - **Is Staff:** Whether the user has admin access.
      - **Is Active:** Whether the account is active.
      - **Date Joined:** When the account was created.
      - Admin accounts display no delete button — they are fully protected from deletion at both the view and admin panel level.

    ---

    - This is the **Notification management** page in the Django admin interface. It shows all notifications generated when topics expire:
      - **User:** The notification recipient.
      - **Topic:** The related expired topic.
      - **Message:** The auto-generated notification message.
      - **Is Read:** Whether the user has viewed the notification.
      - **Created At:** When the notification was generated.

---


## Technologies

    - Python Modules:

        Django==5.0.4
        psycopg2-binary==2.9.9
        python-decouple==3.8
        dj-database-url==2.1.0
        gunicorn==21.2.0
        whitenoise==6.6.0

    - Django:
    - Python framework for web project development.
    - django-auth for managing user accounts in the system.

---

## Testing

- Manual Testing for VoteStar.

| Test Item | Test Carried Out | Result | Pass/Fail |
| --------- | ---------------- | ------ | --------- |
| Register with valid email and password | Submit registration form with valid data | Account created and user redirected to topics list | PASS |
| Register with duplicate email | Submit registration form with an already used email | Error message appears — email must be unique | PASS |
| Login with valid credentials | Submit login form with correct email and password | User logged in and redirected to topics list | PASS |
| Login with invalid credentials | Submit login form with wrong password | "Invalid email or password" error message appears | PASS |
| Create topic while having an active topic | Try to create a second topic while first is still open | Warning message appears — only one active topic allowed | PASS |
| Create topic with valid data | Submit topic form with title and description | Topic created successfully and voting opens for 72 hours | PASS |
| Vote on an active topic | Select a star rating and click Submit Vote | Vote saved and success message appears | PASS |
| Vote twice on the same topic | Attempt to submit a second vote on the same topic | Warning message appears — already voted | PASS |
| Update an existing vote | Change star rating and click Update Vote | Vote updated and success message appears | PASS |
| Withdraw a vote | Click Withdraw Vote on an existing vote | Vote removed and success message appears | PASS |
| Vote on an expired topic | Attempt to vote after 72 hours | Error message appears — voting is closed | PASS |
| Delete own topic | Click Delete Topic as the topic owner | Topic deleted along with all its votes | PASS |
| Delete another user's topic | Attempt to delete a topic owned by another user | Error message appears — permission denied | PASS |
| Delete account as normal user | Click Delete Account and confirm | Account, topics, votes, and notifications all deleted | PASS |
| Delete account as superuser | Attempt to delete admin account | Blocked — "Admin accounts are protected" message appears | PASS |
| View notifications after topic expires | Visit topic detail page after 72 hours | Notification automatically created for owner and voters | PASS |
| Mark notifications as read | Visit the notifications page | All unread notifications marked as read automatically | PASS |
| Clear all notifications | Click Clear All on notifications page | All notifications deleted and page shows empty state | PASS |

---

- Automatic Testing

  - Testing Users App.
    - Testing is essential to ensure that VoteStar's features and components work as expected. This suite of tests focuses on verifying the functionality of the User model and related authentication views. These tests ensure that:
      - The custom User model behaves correctly with email as the unique identifier.
      - Registration, login, logout, and account deletion views work as expected.
      - Superuser accounts are fully protected from deletion at both the view and admin panel level.
      -  ![Users App Test](/images-readme/users_unitTest_2.jpg)
      -  ![Users App Test](/images-readme/users_unitTest.jpg)

  ---

  - Testing Topics App.
    - This suite of tests verifies the Topic model and its related views. These tests ensure that:
      - Topics automatically set `end_time` to 72 hours after creation.
      - Topics are ordered by newest first.
      - The one-active-topic-per-user business rule is enforced correctly.
      - Only the topic owner can delete their own topic.
      -  ![Users App Test](/images-readme/topics_unitTest_2.jpg)
      -  ![Users App Test](/images-readme/topics_unitTest.jpg)

  ---

  - Testing Votes App.
    - Test Cases:
      - `test_one_vote_per_user_per_topic`
        - Attempts to create two votes from the same user on the same topic.
        - The second vote should fail — the database enforces a unique constraint.
      - `test_cannot_vote_on_expired_topic`
        - Attempts to cast a vote after the topic's 72-hour window has passed.
        - The request should be rejected with an error message — voting is locked.
      - `test_cannot_vote_twice`
        - Logs in and submits two consecutive votes on the same topic.
        - Only the first vote should be saved — the second is blocked.
      -  ![Users App Test](/images-readme/votes_unitTest_2.jpg)
      -  ![Users App Test](/images-readme/votes_unitTest.jpg)

  ---

  - Testing Notifications App.
    - Test Cases:
      - `test_no_notifications_for_active_topic`
        - Calls the notification utility on an active topic.
        - No notifications should be created — only expired topics trigger notifications.
      - `test_notifications_not_duplicated`
        - Calls the notification utility twice on the same expired topic.
        - Only one notification per user should exist — `get_or_create` prevents duplicates.
      - `test_notification_marked_read_on_list_view`
        - Visits the notifications page as an authenticated user.
        - All unread notifications should be automatically marked as read.
      -  ![Users App Test](/images-readme/notification_unitTest_2.jpg)
      -  ![Users App Test](/images-readme/notification_unitTest.jpg)

---

## Validator testing (HTML, CSS,  JS,  PYTHON):

- All HTML pages went through html w3c validator test and all files is passed.
-  ![html test](/images-readme/index.jpg)
-  ![html test](/images-readme/details.jpg)
-  ![html test](/images-readme/delete_account.jpg)
-  ![html test](/images-readme/profile.jpg)
-  ![html test](/images-readme/login_html.jpg)

---

- Css file test. CSS file went through a validater test, result; no error found.
  ![css test](/images-readme/css_test.jpg)

---

- Jshint.
- js file test: [site24x7.com](https://www.site24x7.com/tools/javascript-validator.html)
  - file name is stars.js
  - Valid javascript
  -   ![js test](/images-readme/js_test.jpg)
    ***
  - Pep8
    - Link for: [test python files](https://pep8ci.herokuapp.com/)
    - [test python files](/images-readme/python_linter_settings.jpg)
    - [test python files](/images-readme/python_linter_notification_views.jpg)
    - All Python code tested and no errors were found.
  - Lighthouse
    - Lighthouse  
      ![light house test](/images-readme/lighthouse.jpg)

---

## Bugs.

- JWT not suitable for this project:
  - I used Json Web token first time when I start to code this project.
  - I got error in terminal when I run server and server does not run.
  - I asked Chatgpt to solve this Isuue and it suggest to change JWT to Django-allauth.
  - Fix: Just I removed JWT from the project and used default package Django-allauth, that is integrated in Django.

- Try to admin accounts cannot be deleted:
  - This function not excutable.
  - ```if request.user.is_superuser:```.
  - ```  return```.
  - Fix: I give this function redirection order to return.
  - ```return redirect('users:profile')```

- Rename vote URLs to avoid Chrome Safe Browsing false positiv:
  - Web browser thinks there attempted phishing when I click on update or submit vote button.
  - I checked console in web browser there no error.
  - I checked logs in Heroku account there no error.
  - I asked Chatgpt to debug this issue and it suggest to change sub-url in urls file in votes application.
  - before
    ```path('<int:topic_pk>/cast/', ...)```
    ```path('<int:topic_pk>/update/', ...)```
    ```path('<int:topic_pk>/withdraw/', ...)```
  - after
    ```path('topics/<int:topic_pk>/vote/', ...)```
    ```path('topics/<int:topic_pk>/vote/edit/', ...)```
    ```path('topics/<int:topic_pk>/vote/remove/', ...)```
  - And Change also urls file in core project.
  - before
  ```path('votes/', include('votes.urls', namespace='votes'))```
  - after
  ```path('', include('votes.urls', namespace='votes'))```

- Unit test environmet could not see .env file:
  - When I try start to test python files, I get error.
  - Tester could not reach to .env file to read DATABASE_URL.
  - I write the below line in terminal for testing users application.
  - ```set DATABASE_URL=sqlite:///db.sqlite3& set SECRET_KEY=test-secret-key& set DEBUG=False& python manage.py test users```

- h3 html element not acceptable in html w3c validator:
  - Ask me to change this head html tag to h1 or h2.  
    ![light house test](/images-readme/change_h3_to_p_2.jpg)
    ![light house test](/images-readme/change_h3_to_p.jpg)
  - Change to h2.

- No Bugs is this project.


---

## Deployment

### Heroku deployment

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

##  URL Reference

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

---


## Credits
- All Code Institute staff.
- Youtube tutorials.
- AI modles: Chatgpt.

- [Back To Up](#voteStar)
