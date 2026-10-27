# 🚀 Deploying the notary app

Two things to know before you start:

1. **The scanner only works on a Windows machine that has the scanner attached.**
   Direct scanning uses Windows WIA on the *server* running `app.py`. On a Linux host
   (PythonAnywhere, Render) the app still runs perfectly — the scan dialog simply says
   "no scanner found" and offers **Use camera** / **Import file** instead. Nothing crashes.
2. **Your data lives in two places**: `notary.db` (records) and `uploads/` (scans & files).
   Any host that wipes its disk on restart will lose both. Pick a host accordingly.

Everything below assumes the `notary-web` folder is the project root.

---

## Option A — PythonAnywhere (free, recommended for testing)

**Why:** the free *Beginner* plan gives you a **persistent 512 MB disk**, so your SQLite
database and uploads survive restarts. It is always awake (no cold starts).

**Limits:** URL is `yourname.pythonanywhere.com` — **no custom domain** on the free plan
(upgrade to *Developer*, $10/mo, when you buy the domain). Restricted outbound internet
(the app makes no outbound calls, so this is fine). 512 MB disk ≈ 400 scanned pages.

1. Create a free account at **https://www.pythonanywhere.com**.
2. Open a **Bash console** and bring the code over — either push the folder to GitHub
   (`git clone https://github.com/<you>/notary-web.git`) or upload a zip via **Files**
   and unzip it.
3. Create a virtualenv and install:

   ```bash
   cd ~/notary-web
   mkvirtualenv notary --python=/usr/bin/python3.12   # check `ls /usr/bin/python3*`
   pip install -r requirements.txt
   ```
4. **Web** tab → *Add a new web app* → **Manual configuration** → choose the same
   Python version (3.12).
5. Fill in on that page:
   - **Source code:** `/home/USERNAME/notary-web`
   - **Working directory:** `/home/USERNAME/notary-web`
   - **Virtualenv:** `/home/USERNAME/.virtualenvs/notary`
6. Click the **WSGI configuration file** link and replace its whole contents with:

   ```python
   import os, sys

   path = "/home/USERNAME/notary-web"
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ["SECRET_KEY"] = "PASTE-A-LONG-RANDOM-STRING-HERE"
   os.environ["DATA_DIR"] = "/home/USERNAME/notary-data"   # keeps DB + uploads safe
   os.environ["SESSION_COOKIE_SECURE"] = "1"

   from wsgi import app as application
   ```

7. Back on the **Web** tab, add a **Static files** mapping (faster + saves worker time):

   | URL      | Directory                          |
   |----------|------------------------------------|
   | `/static/` | `/home/USERNAME/notary-web/static` |

8. Click **Reload**. Open `https://USERNAME.pythonanywhere.com` and log in with
   `admin` / `admin123`, then **change the password immediately** (Settings).

> Free accounts must be renewed every 3 months — PythonAnywhere emails you a
> "Run until…" button. Click it or the site is disabled.

---

## Option B — Render (free, nicer URL, custom domain included)

**Why:** real HTTPS, 2 custom domains even on the free plan, deploys from GitHub,
one-click blueprint included (`render.yaml`).

**Warning:** the free plan has an **ephemeral disk**. Records and uploads are wiped on
every deploy and whenever the service sleeps. Fine for showing the app to someone;
**do not enter real notary records** until you attach a paid disk.

1. Push the project to GitHub (`.gitignore` already excludes `notary.db`, `uploads/`,
   `.venv/`):

   ```bash
   cd notary-web
   git init && git add . && git commit -m "Notary web app"
   git branch -M main
   git remote add origin https://github.com/<you>/notary-web.git
   git push -u origin main
   ```

2. In Render: **New → Blueprint** → select the repo → **Apply**. `render.yaml` sets the
   build command, the gunicorn start command and generates a `SECRET_KEY` for you.

   Manual alternative — **New → Web Service**:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
   - Environment: add `SECRET_KEY` (long random string), optional `SESSION_COOKIE_SECURE=1`

3. Free services sleep after ~15 minutes idle; the first request then takes ~50 seconds.
4. To keep data on Render: add a **Disk** (1 GB ≈ $0.25/mo), mount it at `/var/data`,
   and set `DATA_DIR=/var/data`.

---

## Going live properly (after you buy the domain)

Because scanning needs Windows + the physical scanner, you have two realistic setups:

### 1. Run it in the office + free Cloudflare Tunnel  ⭐ best for daily notary work
The app runs on the office Windows PC (where the scanner is), and Cloudflare gives you
a real domain with HTTPS for free — no port forwarding, no server bill.

- Buy the domain, add it to **Cloudflare** (free plan), and create a tunnel:
  ```bash
  winget install Cloudflare.cloudflared
  cloudflared tunnel login
  cloudflared tunnel create notary
  cloudflared tunnel route dns notary notary.yourdomain.com
  cloudflared tunnel run --url http://127.0.0.1:5000 notary
  ```
- Run the app on the PC with a production server (Windows-friendly):
  ```powershell
  pip install waitress
  waitress-serve --listen=127.0.0.1:5000 wsgi:app
  ```
- Install `cloudflared` and the app as Windows services so both start on boot.
- ✅ Scanner works, data stays on your disk, free, real domain + HTTPS.
- ⚠️ The PC must stay on and online.

### 2. Host it on Linux (PythonAnywhere paid / Render + disk / VPS)
- ✅ Always online, no office PC needed.
- ⚠️ Scanning is unavailable there — staff would scan on the PC and use **Import file**,
  or use the **camera** option.

---

## Buying the domain

| Registrar | Notes |
|-----------|-------|
| **Cloudflare Registrar** | Sells at wholesale cost, free WHOIS privacy, no upsells — recommended if you will also use Cloudflare Tunnel |
| **Porkbun / Namecheap** | Similar pricing, good first-year promos — check the *renewal* price, not just year one |

- `.com` ≈ $10–12/yr, `.org` ≈ $12–15/yr. Check `shisaxaaqnotary.com` and `.org`;
  if taken, try `shisaxaaq-notary.com`, `isaxaaqnotary.com`, `shisaxaaqnotary.so`.
- Use **.com** as the main address and redirect **.org** to it.
- Enable auto-renew and 2FA on the registrar account — losing the domain locks you out
  of your own records site.

---

## Environment variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `SECRET_KEY` | Signs login sessions — **must** be set in production | long random string |
| `DATA_DIR` | Folder holding `notary.db` + `uploads/` | `/var/data` |
| `DATABASE_URL` | Full SQLAlchemy URL (instead of SQLite) | `postgresql://…` |
| `UPLOAD_FOLDER` | Override just the uploads folder | `/var/data/uploads` |
| `SESSION_COOKIE_SECURE` | `1` = cookies only over HTTPS | `1` |
| `PORT` / `HOST` | Local server bind (default `5000` / `127.0.0.1`) | `8080`, `0.0.0.0` |
| `FLASK_DEBUG` | `0` disables the debugger/reloader | `0` |

Generate a secret key:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

---

## Before real records go in — checklist

- [ ] Admin password changed from `admin123`; staff accounts created with real names
- [ ] `SECRET_KEY` set to a random value (not the default)
- [ ] HTTPS working (Render/PythonAnywhere/Cloudflare all provide free certificates)
- [ ] `SESSION_COOKIE_SECURE=1` once on HTTPS
- [ ] Automated backup of `DATA_DIR` (the `.db` **and** `uploads/` together)
- [ ] `FLASK_DEBUG=0` on any public server
- [ ] Test a scan end-to-end on the actual scanner PC

A simple Windows backup (Task Scheduler, daily):

```powershell
$stamp = Get-Date -Format "yyyy-MM-dd"
Copy-Item "C:\...\notary-data" "D:\Backups\notary-$stamp" -Recurse -Force
```
