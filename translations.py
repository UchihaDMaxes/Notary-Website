"""Bilingual (Somali / English) string table."""

LANGUAGES = {"so": "Soomaali", "en": "English"}
DEFAULT_LANG = "so"

STRINGS = {
    "so": {
        # Brand / chrome
        "app_name": "SH. ISAXAAQ NOTARY",
        "app_subtitle": "Notaariyada Sharciga Ah",
        "dashboard": "Bogga Hore",
        "registry": "Kaydka",
        "administration": "Maamulka",
        "error": "Khalad",
        "home": "Hore",
        "iib": "Iib",
        "heshiis": "Heshiis",
        "search": "Raadin",
        "users": "Isticmaalayaal",
        "settings": "Dejinta",
        "logout": "Soo bixid",
        "login": "Gal",
        "language": "Luqad",

        # Auth
        "login_title": "Soo gal akoonkaaga",
        "username": "Magaca isticmaalaha",
        "password": "Furaha sirta ah",
        "remember": "Xusuusnow iiga",
        "forgot_note": "Lama hagaajin karo furaha sirta ah hadda. La xiriir maamulaha.",
        "welcome_back": "Ku soo dhawoow",

        # Modules
        "sales_registry": "Kaydka Iibka",
        "contracts_registry": "Kaydka Heshiiska",
        "new_record": "Diwaan cusub",
        "new_iib": "Iib cusub",
        "new_heshiis": "Heshiis cusub",
        "all_records": "Dhammaan diwaannada",
        "back": "Dib u noqo",
        "save": "Kaydi",
        "cancel": "Jooji",
        "clear": "Nadiifi",
        "edit": "Beddel",
        "delete": "Tirtir",
        "view": "Fiiri",
        "actions": "Ficil",

        # Fields
        "date": "Taariikh",
        "faahfaahin": "Faahfaahin",
        "cabir": "Cabir",
        "qiime": "Qiime",
        "kuyaalla": "Ku Yaalla",
        "iibiye": "Iibiye",
        "iibsade": "Iibsade",
        "damiin": "Damiin",
        "kireeye": "Kireeye",
        "kireyste": "Kireyste",
        "goob": "Goob",
        "number": "Lambarka",
        "notes": "Fiiro Gaar Ah",
        "documents": "Dukumentiyada",
        "upload_documents": "Ku dar dukumenti",
        "upload_hint": "PNG, JPG, WEBP ama PDF. Ilaa 32MB midkiiba.",
        "no_documents": "Dukumenti lama soo gelin.",
        "added_by": "Waxaa ku daray",
        "created_at": "Taariikhda diwaangelinta",
        "type": "Nooca",

        # Documents — import / scan
        "add_documents": "Ku dar dukumentiyo",
        "choose_source": "Xulo sida aad dukumentiga u gelinayso",
        "import_file": "Soo geli fayl",
        "import_file_hint": "Ka soo qaad kombuyuutarka — PNG, JPG, WEBP ama PDF.",
        "scan_document": "Iska scan",
        "scan_hint": "Isticmaal scanner-ka ku xiran ama kamaradda.",
        "device": "Qalabka",
        "resolution": "Tirako (DPI)",
        "color_mode": "Nooca midabka",
        "color": "Midab",
        "grayscale": "Madow & Cad",
        "start_scan": "Bilow scan",
        "scanning": "Waa la scan-garaynayaa…",
        "scanning_wait": "Fadlan sug inta scanner-ku shaqaynayo.",
        "use_camera": "Isticmaal kamarad",
        "capture": "Qaad sawir",
        "retake": "Dib u qaad",
        "add_to_record": "Ku dar diwaanka",
        "close": "Xir",
        "remove": "Ka saar",
        "pending": "Diyaar u ah kaydinta",
        "no_preview": "Weli bog lama qaadin.",
        "no_scanner": "Scanner lama helin. Isticmaal kamaradda ama soo geli fayl.",
        "scan_failed": "Scan-gu wuu guuldareystay.",
        "camera_failed": "Kamaradda lama furi karin.",
        "scanner_ready": "Scanner diyaar",
        "pages_ready": "boganeed diyaar",
        "select_scanner": "Dooro scanner",

        # Options
        "iib_dhul": "Iib Dhul",
        "iib_guri": "Iib Guri",
        "iib_gaadhi": "Iib Gaadhi",
        "isku_bedel_dhul_gaadhi": "Isku Bedel Dhul-Gaadhi",
        "isku_bedel_dhul_dhul": "Isku Bedel Dhul-Dhul",
        "hibo": "Hibo",
        "iib_kale": "Iib Kale",
        "heshiis_kiro": "Heshiis Kiro",
        "heshiis_laba_dhinac": "Heshiis Laba Dhinac",
        "heshiis_qandaraas": "Heshiis Qandaraas",
        "heshiis_kale": "Heshiis Kale",

        # Dashboard
        "total_iib": "Wadar Iib",
        "total_heshiis": "Wadar Heshiis",
        "total_records": "Wadar Diwaan",
        "total_documents": "Wadar Dukumenti",
        "recent_activity": "Dhaqdhaqaaqa Dhow",
        "recent_iib": "Iibka Ugu Dambeeyay",
        "recent_heshiis": "Heshiiska Ugu Dambeeyay",
        "no_records": "Weli diwaan lama diwaangelin.",
        "no_recent": "Wax diwaan ah lama diwaangelin weli.",

        # Search
        "search_title": "Raadi diwaanno",
        "search_placeholder": "Magac, lambar, goob ama faahfaahin...",
        "search_all": "Raadi dhammaan diwaannada",
        "results": "Natiijooyin",
        "no_results": "Natiijo lama helin.",
        "in_iib": "Iib",
        "in_heshiis": "Heshiis",

        # Users
        "manage_users": "Maaree isticmaalayaasha",
        "full_name": "Magaca oo dhan",
        "role": "Doorka",
        "admin": "Maamule",
        "staff": "Shaqaale",
        "active": "Shaqaynaya",
        "inactive": "Waa joojiyay",
        "create_user": "Samee isticmaale",
        "edit_user": "Beddel isticmaale",
        "new_password": "Furaha cusub",
        "password_optional": "Ka tag hadda aad rabto inaad la sii hesho.",
        "toggle_active": "Jooji / Shaqee",
        "delete_user_confirm": "Ma hubtaa inaad tirtirto isticmaahan?",
        "last_admin": "Kama tirtiri karto maamulaha ugu dambeeya.",

        # Settings
        "profile": "Xogta shaqsiga",
        "change_password": "Beddel furaha sirta ah",
        "current_password": "Furaha hadda",
        "confirm_password": "Xaqiiji furaha",
        "save_changes": "Kaydi isbeddelada",
        "update_profile": "Cusbooneysii xogta",

        # Messages
        "saved": "Waa la kaydiyay.",
        "updated": "Waa la cusbooneysiiyay.",
        "deleted": "Waa la tirtiray.",
        "login_failed": "Magaca isticmaalaha ama furaha sirta ah waa khalad.",
        "account_disabled": "Akoonkan waa la joojiyay. La xiriir maamulaha.",
        "unauthorized": "Ma laha oggolaansho aad ku gasho boggan.",
        "required_field": "Fadlan buuxi dhammaan beeraha waajibka ah.",
        "bad_file": "Faylkaani ma aha nooc la oggol yahay.",
        "wrong_password": "Furaha sirta ah hadda waa khalad.",
        "password_changed": "Furaha sirta ah waa la beddelay.",
        "profile_updated": "Xogta shaqsiga waa la cusbooneysiiyay.",
        "username_taken": "Magaca isticmaalaha waa la isticmaalay.",
        "confirm_delete": "Ma hubtaa inaad tirtirto diwaankan?",
        "search_prompt": "Ku qor furaha raadinta.",
    },
    "en": {
        # Brand / chrome
        "app_name": "SH. ISAXAAQ NOTARY",
        "app_subtitle": "Legal Notary Services",
        "dashboard": "Dashboard",
        "registry": "Registry",
        "administration": "Administration",
        "error": "Error",
        "home": "Home",
        "iib": "Sales",
        "heshiis": "Contracts",
        "search": "Search",
        "users": "Users",
        "settings": "Settings",
        "logout": "Log out",
        "login": "Log in",
        "language": "Language",

        # Auth
        "login_title": "Sign in to your account",
        "username": "Username",
        "password": "Password",
        "remember": "Remember me",
        "forgot_note": "Passwords cannot be recovered here. Contact the administrator.",
        "welcome_back": "Welcome back",

        # Modules
        "sales_registry": "Sales Registry",
        "contracts_registry": "Contracts Registry",
        "new_record": "New record",
        "new_iib": "New sale",
        "new_heshiis": "New contract",
        "all_records": "All records",
        "back": "Back",
        "save": "Save",
        "cancel": "Cancel",
        "clear": "Clear",
        "edit": "Edit",
        "delete": "Delete",
        "view": "View",
        "actions": "Actions",

        # Fields
        "date": "Date",
        "faahfaahin": "Details",
        "cabir": "Size",
        "qiime": "Price",
        "kuyaalla": "Located at",
        "iibiye": "Seller",
        "iibsade": "Buyer",
        "damiin": "Guarantor",
        "kireeye": "Lessor",
        "kireyste": "Lessee",
        "goob": "Place",
        "number": "Phone",
        "notes": "Special Notes",
        "documents": "Documents",
        "upload_documents": "Add documents",
        "upload_hint": "PNG, JPG, WEBP or PDF. Up to 32MB each.",
        "no_documents": "No documents uploaded.",
        "added_by": "Added by",
        "created_at": "Recorded on",
        "type": "Type",

        # Documents — import / scan
        "add_documents": "Add documents",
        "choose_source": "Choose how to add the document",
        "import_file": "Import file",
        "import_file_hint": "Pick from this computer — PNG, JPG, WEBP or PDF.",
        "scan_document": "Scan document",
        "scan_hint": "Use the attached scanner or your camera.",
        "device": "Device",
        "resolution": "Resolution (DPI)",
        "color_mode": "Colour mode",
        "color": "Colour",
        "grayscale": "Grayscale",
        "start_scan": "Start scan",
        "scanning": "Scanning…",
        "scanning_wait": "Please wait while the scanner is working.",
        "use_camera": "Use camera",
        "capture": "Capture",
        "retake": "Retake",
        "add_to_record": "Add to record",
        "close": "Close",
        "remove": "Remove",
        "pending": "Ready to save",
        "no_preview": "No page captured yet.",
        "no_scanner": "No scanner found. Use the camera or import a file instead.",
        "scan_failed": "Scanning failed.",
        "camera_failed": "Could not access the camera.",
        "scanner_ready": "Scanner ready",
        "pages_ready": "page(s) ready",
        "select_scanner": "Select scanner",

        # Options
        "iib_dhul": "Land Sale",
        "iib_guri": "House Sale",
        "iib_gaadhi": "Vehicle Sale",
        "isku_bedel_dhul_gaadhi": "Exchange Land-Vehicle",
        "isku_bedel_dhul_dhul": "Exchange Land-Land",
        "hibo": "Gift",
        "iib_kale": "Other Sale",
        "heshiis_kiro": "Rent Agreement",
        "heshiis_laba_dhinac": "Bilateral Agreement",
        "heshiis_qandaraas": "Service Contract",
        "heshiis_kale": "Other Contract",

        # Dashboard
        "total_iib": "Total Sales",
        "total_heshiis": "Total Contracts",
        "total_records": "Total Records",
        "total_documents": "Total Documents",
        "recent_activity": "Recent Activity",
        "recent_iib": "Latest Sales",
        "recent_heshiis": "Latest Contracts",
        "no_records": "No records yet.",
        "no_recent": "No records have been added yet.",

        # Search
        "search_title": "Search records",
        "search_placeholder": "Name, phone, place or detail...",
        "search_all": "Search all records",
        "results": "Results",
        "no_results": "No results found.",
        "in_iib": "Sale",
        "in_heshiis": "Contract",

        # Users
        "manage_users": "Manage users",
        "full_name": "Full name",
        "role": "Role",
        "admin": "Administrator",
        "staff": "Staff",
        "active": "Active",
        "inactive": "Disabled",
        "create_user": "Create user",
        "edit_user": "Edit user",
        "new_password": "New password",
        "password_optional": "Leave blank to keep the current password.",
        "toggle_active": "Enable / Disable",
        "delete_user_confirm": "Are you sure you want to delete this user?",
        "last_admin": "You cannot delete the last administrator.",

        # Settings
        "profile": "Profile",
        "change_password": "Change password",
        "current_password": "Current password",
        "confirm_password": "Confirm password",
        "save_changes": "Save changes",
        "update_profile": "Update profile",

        # Messages
        "saved": "Saved successfully.",
        "updated": "Updated successfully.",
        "deleted": "Deleted successfully.",
        "login_failed": "Incorrect username or password.",
        "account_disabled": "This account is disabled. Contact the administrator.",
        "unauthorized": "You do not have permission to view this page.",
        "required_field": "Please fill in all required fields.",
        "bad_file": "That file type is not allowed.",
        "wrong_password": "Current password is incorrect.",
        "password_changed": "Password changed successfully.",
        "profile_updated": "Profile updated successfully.",
        "username_taken": "That username is already taken.",
        "confirm_delete": "Are you sure you want to delete this record?",
        "search_prompt": "Enter a search term.",
    },
}


def translate(key, lang=DEFAULT_LANG):
    """Return the string for `key` in `lang`, falling back to Somali."""
    table = STRINGS.get(lang, STRINGS[DEFAULT_LANG])
    return table.get(key, STRINGS[DEFAULT_LANG].get(key, key))


# Human labels for record types, keyed by the stored option value.
TYPE_LABELS = {
    "so": {
        "IIB DHUL": "iib_dhul",
        "IIB GURI": "iib_guri",
        "IIB GAADHI": "iib_gaadhi",
        "ISKU BEDEL DHUL-GAADHI": "isku_bedel_dhul_gaadhi",
        "ISKU BEDEL DHUL-DHUL": "isku_bedel_dhul_dhul",
        "HIBO": "hibo",
        "IIB KALE": "iib_kale",
        "HESHIIS KIRO": "heshiis_kiro",
        "HESHIIS LABA DHINAC": "heshiis_laba_dhinac",
        "HESHIIS QANDARAAS": "heshiis_qandaraas",
        "HESHIIS KALE": "heshiis_kale",
    }
}

IIB_TYPES = [
    "IIB DHUL",
    "IIB GURI",
    "IIB GAADHI",
    "ISKU BEDEL DHUL-GAADHI",
    "ISKU BEDEL DHUL-DHUL",
    "HIBO",
    "IIB KALE",
]

HESHIIS_TYPES = [
    "HESHIIS KIRO",
    "HESHIIS LABA DHINAC",
    "HESHIIS QANDARAAS",
    "HESHIIS KALE",
]


def type_label(value, lang=DEFAULT_LANG):
    """Translate a stored type value like 'IIB DHUL' for display."""
    if not value:
        return ""
    key = TYPE_LABELS["so"].get(value)
    if key:
        return translate(key, lang)
    return value
