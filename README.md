# Travel & Tours CRM (Django, free stack)

A web-based CRM for a Travel & Tours agency: passengers, group bookings (Umrah / Hajj / Visit Visa / Flights), document vault, invoicing, payment tracking, supplier ledger, and reporting.

Built entirely on free, open-source software. SQLite for development; switch to free PostgreSQL (Supabase / Neon / Railway) for production with one line.

## Stack
- **Backend**: Django 5 (Python)
- **Frontend**: Django templates + Bootstrap 5 (responsive)
- **DB**: SQLite (dev) → PostgreSQL via `DATABASE_URL` (prod)
- **PDF**: ReportLab • **Excel**: openpyxl
- **Static files**: WhiteNoise (no separate web server needed)
- **Auth**: Django auth + `Admin` / `Staff` groups (auto-created)

## Run locally (Windows)

```powershell
cd c:\Users\mashh\travel-crm
.\.venv\Scripts\python.exe manage.py runserver
```

Then open http://127.0.0.1:8000/ and log in:

- **Username:** `admin`
- **Password:** `admin12345`  ← change immediately via `/admin/`

To create staff users: log in to `/admin/` → Users → Add user, then add them to the **Staff** group (auto-created on first migrate). Staff get add/change/view but not delete on financial models.

## First steps in the app
1. `/admin/` — change the admin password, create more users, assign to **Admin** or **Staff** group.
2. **Passengers** → New Passenger (capture passport + CNIC + expiry).
3. **Groups** → New Group → Add members for Umrah/Hajj/Tour batches.
4. **Bookings** → New Booking (auto-generates `BK-000001` reference).
5. Click a booking to record payments and download a branded PDF invoice/receipt.
6. **Suppliers** → log payments to airlines/hotels/visa providers.
7. **Financial Report** → totals + export to Excel.
8. **Dashboard** → outstanding balances, expiring passports/visas alerts.

## Branding
Edit `.env` (copy from `.env.example`) to set agency name, address, phone, email used in PDF invoices and the sidebar.

## Free production hosting options
| Host | Free tier | Notes |
|---|---|---|
| **PythonAnywhere** | Yes (1 web app) | Easiest for Django; built-in MySQL. |
| **Render** | Yes (web + free Postgres 90 days) | One-click Django deploy. |
| **Fly.io** | Yes (small VM) | Great with Postgres. |
| **Railway** | Trial credit | Postgres add-on. |
| **Supabase / Neon** | Free Postgres | Use as `DATABASE_URL` from any host. |

For production, in `.env`:
```
DEBUG=False
SECRET_KEY=<long random string>
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgres://USER:PASS@HOST:5432/DB
```

Then:
```
python manage.py collectstatic --noinput
python manage.py migrate
```

Use `gunicorn travelcrm.wsgi` (Linux hosts) — WhiteNoise serves static files, no nginx needed.

## Free automated daily backup
SQLite (dev): just copy `db.sqlite3` nightly via Windows Task Scheduler.

PostgreSQL (prod): use the host's built-in backups (Supabase/Neon include daily snapshots free), or a cron job:
```
pg_dump $DATABASE_URL | gzip > backup-$(date +%F).sql.gz
```

## Security defaults included
- CSRF protection on all forms
- Role-based permissions (Admin vs Staff)
- HttpOnly cookies, X-Frame DENY, HSTS in production
- 25 MB upload cap on documents
- File uploads stored under `media/passengers/<id>/`
- All views are `@login_required`

## Future API integrations (scaffolded for)
The architecture is decoupled enough to add later:
- SMS gateway (Twilio / local PK gateways) — hook into `Passenger.mobile`
- Ticketing APIs (Amadeus / Sabre / Travelport) — wrap as services in `crm/services/`
- Email notifications for expiry alerts (use Django's email + a free SMTP like Gmail or Brevo)

## Project layout
```
travel-crm/
├── manage.py
├── requirements.txt
├── .env.example
├── travelcrm/         # project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── crm/               # main app
│   ├── models.py      # Passenger, Group, Booking, Payment, Supplier, ...
│   ├── views.py       # all CRUD + PDF/Excel exports
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── signals.py     # auto-creates Admin & Staff groups
│   └── templates/crm/
└── templates/         # base.html + login.html
```
