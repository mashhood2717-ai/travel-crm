# How to run this CRM

## 1. Open this folder in VS Code
File → Open Folder → `c:\Users\mashh\travel-crm`

## 2. Start the server (3 ways — pick any)

### Easiest: press F5
VS Code will start Django on http://127.0.0.1:8000/ using the included launch config.

### Or: Ctrl+Shift+B → choose "Run Django server"

### Or: in a terminal
```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

## 3. Log in
Open http://127.0.0.1:8000/

- Username: `admin`
- Password: `admin12345`  (change immediately at /admin/)

## 4. Common commands (Terminal → Run Task…)

| Task | What it does |
|---|---|
| Run Django server | Starts dev server on :8000 |
| Make migrations | After editing `crm/models.py` |
| Migrate DB | Apply pending migrations |
| Create superuser | Add a new admin user |
| Create staff user | Interactive helper |
| Django shell | Python REPL with models loaded |
| Collect static (prod) | Gather static files for production |
| Backup database | Copies `db.sqlite3` to `backups/` with timestamp |

## 5. Test walkthrough (5 minutes)
1. /admin/ → change `admin` password.
2. Sidebar → **Passengers → New Passenger** → save.
3. **Groups → New Group** → add the passenger as a member.
4. **Bookings → New Booking** → set package cost.
5. On the booking page → record a payment → click **Invoice** for branded PDF.
6. **Suppliers → New Supplier** → record a payment.
7. **Financial Report → Export Excel**.
8. **Dashboard** shows expiring-passport alerts.

## Where things live
- Models (DB schema): `crm/models.py`
- Pages / logic:       `crm/views.py`
- Forms:               `crm/forms.py`
- URL routes:          `crm/urls.py`
- Templates (HTML):    `crm/templates/crm/` and `templates/`
- Settings:            `travelcrm/settings.py`
- Database file:       `db.sqlite3`
- Uploaded files:      `media/`

## Reset everything
Stop the server, then:
```powershell
Remove-Item db.sqlite3, media -Recurse -Force -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
```

## Free production hosting
See `README.md` for full deploy guide (PythonAnywhere / Render / Fly.io / Supabase).
