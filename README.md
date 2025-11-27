JNU Health Center — Flask-Based Hospital Management System

**Project Overview**
- **Name**: JNU Health Center
- **Description**: A small Flask application to manage hospital workflows: patient registration, appointments, doctors, departments, treatment records, and simple reporting. The app uses server-side templates and SQLite for data storage.
- **Purpose**: Provide a lightweight, self-hosted clinic/hospital management UI for administrative staff, doctors, and patients.

**Key Features**
- **User Roles**: Admin, Doctor, Patient (separate templates and dashboards).
- **Appointments**: Create and manage patient appointments.
- **Patient Records**: Add and update patient history and treatments.
- **Doctor Management**: Add departments and doctors, view availability and profiles.
- **Templates & Static Assets**: HTML templates in `templates/`, CSS in `static/`.

**Requirements**
- **Python**: 3.8+ recommended
- **Primary libraries**: Flask and SQLite (bundled with Python). If a `requirements.txt` exists, use it.

**Quick Setup (Windows PowerShell)**
- Create and activate a virtual environment, install dependencies, then run the app:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

If you don't have a `requirements.txt`, you can at minimum install Flask:

```powershell
pip install flask
python app.py
```

**Configuration & Database**
- The project uses a SQLite DB stored at `instance/hms.sqlite3` (an example `instance/` folder is present).
- Additional configuration (secret keys or DB path) may be in `application/database.py` or `app.py` — check these files if you need to change settings.

**Run (development)**
- Run `python app.py` and open http://127.0.0.1:5000/ in your browser.
- If the app uses Flask CLI, you can also set environment variables and use `flask run` (see `app.py` for details).

**Project Structure (important files)**
- `app.py`: Application entry point.
- `application/controllers.py`: Route handlers and controllers.
- `application/database.py`: DB connection and helpers.
- `application/models.py`: ORM/models and data utilities.
- `templates/`: HTML templates (login, dashboards, patient forms, reports).
- `static/`: CSS and uploaded assets (`static/uploads/`).
- `instance/hms.sqlite3`: SQLite database file (created/used by the app).

**Common Tasks**
- **Reset DB**: Backup and remove `instance/hms.sqlite3`, then run migration or initialization script if available.
- **Add a new template**: Place the file under `templates/` and update appropriate routes in `application/controllers.py`.
- **Static assets**: Put CSS/JS/images in `static/` and reference them in templates with `url_for('static', filename='...')`.

**Contributing**
- Fork the repo and open a pull request with a clear description.
- Prefer small, focused commits. Write or update tests when adding features.

**Notes & TODOs**
- Consider adding a `requirements.txt` for reproducible installs.
- Add a `README` section for default admin/test credentials if any exist.
- Add instructions for running under a production server (Gunicorn, waitress, or IIS + WSGI) and creating a backup/restore procedure for `instance/hms.sqlite3`.

**License & Contact**
- **License**: (Add your license here — e.g., MIT)
- **Author / Maintainer**: (Add contact info)

---

If you'd like, I can:
- Add a `requirements.txt` automatically from imports in the project.
- Replace the existing `READme` file with this content (if you prefer to keep casing), or update/expand this `README.md` with screenshots and sample data.

Tell me which next step you prefer.