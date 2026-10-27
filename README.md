# SH. ISAXAAQ NOTARY — Web Application

A modern, bilingual (Somali / English) web version of the notary records desktop app,
rebuilt with **Flask + Jinja2** and a self-contained CSS design system (no CDN, works offline).

It replaces the old Tkinter / customtkinter desktop programs with a clean, responsive
web interface and adds the features the desktop app was missing: full **search**,
**edit / delete**, secure **document uploads**, **role-based login**, and a **dashboard**.

---

## ✨ Features

- **Dashboard** — live counts of sales, contracts and documents; recent activity.
- **Iib (Sales) registry** — land / house / vehicle sales, gifts, exchanges.
- **Heshiis (Contracts) registry** — rent, bilateral, service contracts.
- **Full search** — one search box finds records across both registries.
- **Documents, two ways** — *import a file* from disk **or** *scan directly from a scanner*
  (Windows WIA), with live preview, DPI/colour control, multi-page support and a
  browser-camera fallback. Files are stored on disk (not as BLOBs).
- **Users & roles** — administrator + staff accounts, enable/disable, password resets.
- **Bilingual UI** — toggle Somali ⇄ English from any page; each user's choice is saved.
- **Responsive** — works on desktop, tablet and phone (collapsible sidebar).

---

## 🚀 Getting started

```bash
cd notary-web
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

### Default administrator

On the very first run the app seeds an administrator account:

| Field    | Value    |
|----------|----------|
| Username | `admin`  |
| Password | `admin123` |

> ⚠️ **Log in and change this password immediately** via *Settings → Change password*,
> and create your own staff accounts under *Users*.

---

## 📄 Adding documents — import or scan

Every record form (and every saved record) offers **two ways to attach a document**:

### 1. Import file
Click **Import file** (or drag files onto the two cards) and pick images
(PNG / JPG / WEBP / GIF / TIFF) or PDFs. You can select several at once.

### 2. Scan document
Click **Scan document** to open the scanner dialog:

| Control | Purpose |
|---------|---------|
| **Device** | Which attached scanner to use (auto-listed from Windows) |
| **Resolution** | 150 / 200 / 300 / 600 DPI — 300 is a good default for legal paper |
| **Colour mode** | Colour or grayscale |
| **Start scan** | Acquires one page and shows a preview |
| **Use camera** | Fallback for machines without a scanner (or for loose pages) |

Click **Add to record** to stage each page; repeat for multi-page documents, then
**Close** and save the record. Staged pages appear as thumbnails and can be removed
before saving. Scanned pages are written to the `uploads/` folder exactly like
imported files.

### Scanner requirements

Direct scanning uses **Windows Image Acquisition (WIA)** through `pywin32`, which is
included in `requirements.txt` for Windows:

```bash
pip install -r requirements.txt
```

If `pywin32` is missing or no scanner is detected, the dialog says so and the app keeps
working — use **Use camera** or **Import file** instead. The scanner must also be
installed and visible in *Windows → Settings → Bluetooth & devices → Printers & scanners*.

> Scanners are accessed by the machine running `app.py`. If you host the app on a server,
> the scan button talks to the *server's* scanner, not the user's PC.

---

## 🗂 Project structure

```
notary-web/
├── app.py                 # App factory, blueprints, error pages, admin seeding
├── config.py              # Configuration (DB path, uploads, limits)
├── models.py              # SQLAlchemy models: User, Iib, Heshiis, Document
├── utils.py               # Language, permissions, file upload + data-URL helpers
├── scanner.py             # Windows WIA scanner access (pywin32, optional)
├── translations.py        # All bilingual UI strings
├── requirements.txt
├── uploads/               # Uploaded & scanned documents (created automatically)
├── blueprints/
│   ├── auth.py            # Login / logout
│   ├── main.py            # Dashboard, search, language, settings
│   ├── iib.py             # Sales CRUD + attach + document serving
│   ├── heshiis.py         # Contracts CRUD + attach + document serving
│   ├── scan.py            # /scan/devices, /scan/capture (JSON)
│   └── users.py           # User administration (admin only)
├── templates/             # Jinja2 templates
│   ├── base.html          # Layout: sidebar + topbar
│   ├── _macros.html       # Reusable macros (doc grid, key/value, money)
│   ├── _doc_picker.html   # Import-or-scan picker + scanner dialog
│   ├── login.html, dashboard.html, search.html, settings.html, error.html
│   ├── iib/               # list, form, detail
│   ├── heshiis/           # list, form, detail
│   └── users/             # list, form
└── static/
    ├── css/app.css        # Design system (cards, tables, buttons, scanner UI)
    ├── js/app.js          # Sidebar, flash messages, confirm dialogs
    └── js/scan.js         # Import/scan picker, camera capture, staged pages
```

---

## 🔧 Configuration

Environment variables (all optional) — see `config.py`:

| Variable       | Purpose                              | Default              |
|----------------|--------------------------------------|----------------------|
| `SECRET_KEY`   | Flask session secret                 | `dev-change-me...`   |
| `DATABASE_URL` | SQLAlchemy database URL              | SQLite `notary.db`   |

To use a production database (e.g. PostgreSQL) set `DATABASE_URL` accordingly and
install the matching driver (e.g. `psycopg2-binary`).

Uploaded files are stored in the `uploads/` folder. Back up **both** `notary.db`
and `uploads/` to preserve all data.

---

## 🗄 Data model

| Table       | Purpose                          | Key fields |
|-------------|----------------------------------|------------|
| `users`     | Login accounts & roles           | username, role, active, language |
| `iib`       | Sales records                    | date, type, size, price, location, seller/buyer/guarantor + phones, notes, documents |
| `heshiis`   | Contract records                 | date, type, price, place, lessor/lessee + phones, notes, documents |
| `documents` | Uploaded files (linked to a record) | stored filename, original name, type, size |

Deleting a record automatically removes its uploaded files.

---

## 🧩 Notes on the rewrite

Compared with the original desktop code, this version:

- Uses a clean component-based layout instead of fragile `place()` pixel coordinates.
- Implements the previously **broken search** (`on_find`) properly.
- Adds **edit** and **delete** for records and documents.
- Stores documents on disk instead of SQLite BLOBs.
- Adds authentication, roles, and per-user language — entirely absent before.

The original desktop files in the parent `WORKSPACE` folder are untouched and can still
be used; this web app is a self-contained sibling project.
