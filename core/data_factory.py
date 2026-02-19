# termux_version/core/data_factory.py
import random
import string
import uuid

# DATA FACTORY (v70 GIGATON)
# Generates realistic Indonesian identities to bypass filters.

FIRST_NAMES = [
    "Agus", "Budi", "Citra", "Dewi", "Eko", "Fajar", "Gilang", "Hesti", "Indah", "Joko",
    "Kurniawan", "Lestari", "Mega", "Nur", "Oki", "Putri", "Rizky", "Siti", "Tono", "Utami",
    "Vina", "Wahyu", "Xavier", "Yulia", "Zainal", "Adit", "Bayu", "Cahya", "Dian", "Erwin"
]

LAST_NAMES = [
    "Santoso", "Wijaya", "Saputra", "Hidayat", "Pratama", "Nugroho", "Wibowo", "Kusuma",
    "Permana", "Utama", "Anwar", "Setiawan", "Siregar", "Nasution", "Sihombing", "Manullang"
]

DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"]

def get_random_identity():
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    full_name = f"{first} {last}"
    
    # Email generation
    sep = random.choice(["", ".", "_", "-"])
    num = random.randint(10, 9999)
    email = f"{first.lower()}{sep}{last.lower()}{num}@{random.choice(DOMAINS)}"
    
    # Device ID
    device_id = str(uuid.uuid4())
    
    # Password
    chars = string.ascii_letters + string.digits + "!@#$"
    password = "".join(random.choice(chars) for _ in range(12))
    
    return {
        "name": full_name,
        "email": email,
        "device_id": device_id,
        "password": password,
        "user_id": str(random.randint(1000000, 9999999))
    }
