from dotenv import load_dotenv
import os
# import requests
from fastapi import FastAPI, Request, HTTPException
# from pydantic import BaseModel
from twilio.rest import Client
# from apscheduler.schedulers.background import BackgroundScheduler
from db import owner, warung

load_dotenv()

app = FastAPI()
client = Client(os.getenv("ACCOUNT_SID"), os.getenv("AUTH_TOKEN"))

# COMMENT KALAU SUDAH BERHASIL MENGIRIM PESAN DARI BOT KE USER
@app.get("/")
def root():
    return {"message": "Hello, World!"}

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()
    print("Incoming:", form_data) # UNCOMMENT DI PRODUCTION

    state = (await owner.find_one({"phone_number": form_data["From"]}) or {}).get("state")

    if state is None:
        await owner.insert_one({
            "phone_number": form_data["From"],
            "state": "WAITING_FOR_NAME"
        })
        # UNCOMMENT KALAU INGIN MENGIRIM PESAN DARI BOT KE USER ($0.01 / msg)
        message = client.messages.create(
                to = form_data["From"],
                from_ = os.getenv("FROM_WA_NUMBER"),
                body=
                """Selamat datang di Sobat Warung! 👋
Yuk mulai dengan isi namamu dulu!
Ketik dengan format: *Nama : Nama Panggilan*  
Contoh: *Nama : Budi*"""
)
    elif state == "WAITING_FOR_NAME":  
        try:
            if "Nama :" in form_data["Body"]:
                owner_name = form_data["Body"].split("Nama :")[1].strip()
                if not owner_name:
                    raise HTTPException(status_code=400, detail="Nama Panggilan tidak boleh kosong")
                
            else:
                raise HTTPException(status_code=400, detail="Format tidak sesuai")
        
            await owner.update_one({"phone_number": form_data["From"]}, {"$set": {"owner_name": owner_name, "state": "INPUT_NAMA_WARUNG"}})

            # UNCOMMENT KALAU INGIN MENGIRIM PESAN DARI BOT KE USER ($0.01 / msg)
            message = client.messages.create(
                    to = form_data["From"],
                    from_ = os.getenv("FROM_WA_NUMBER"),
                    body=f"""👋 Hai *{owner_name}*!
Sekarang lanjut dengan isi nama warungmu.                    
Ketik dengan format: *Warung : Nama Warung*  
Contoh: *Warung : Ramirez Jatinangor*""",
)
        except Exception:
                # UNCOMMENT KALAU INGIN MENGIRIM PESAN DARI BOT KE USER ($0.01 / msg)
                message = client.messages.create(
                        to = form_data["From"],
                        from_ = os.getenv("FROM_WA_NUMBER"),
                        body="""Format salah!
Ketik dengan format: *Nama : Nama Panggilan*  
Contoh: *Nama : Budi*"""
)
            
    elif state == "INPUT_NAMA_WARUNG":  
        try:
            if "Warung :" in form_data["Body"]:
                warung_name = form_data["Body"].split("Warung :")[1].strip()
                if not warung_name:
                    raise HTTPException(status_code=400, detail="Nama Warung tidak boleh kosong")
                
            else:
                raise HTTPException(status_code=400, detail="Format tidak sesuai")
            
            owner_data = await owner.find_one({"phone_number": form_data["From"]})
            owner_id = owner_data.get("_id")
            await owner.update_one({"phone_number": form_data["From"]}, {"$set": {"state": "INPUT_LOKASI_WARUNG"}})

            await warung.insert_one({
                "warung_name": warung_name,
                "owner_id": owner_id,
            })

            # UNCOMMENT KALAU INGIN MENGIRIM PESAN DARI BOT KE USER ($0.01 / msg)
            message = client.messages.create(
                    to = form_data["From"],
                    from_ = os.getenv("FROM_WA_NUMBER"),
                    body=f"""Terimakasih *{warung_name}*!
Terakhir silahkan isi lokasi warungmu.
Kamu bisa kirim *share location* langsung (jika posisi sekarang di warung),
atau *isi manual* koordinatnya.
Ketik dengan format: *Latitude : angka, Longitude : angka*  
Contoh: *Latitude : -6.23, Longitude : 106.82*""",
)
        except Exception:
                # UNCOMMENT KALAU INGIN MENGIRIM PESAN DARI BOT KE USER ($0.01 / msg)
                message = client.messages.create(
                        to = form_data["From"],
                        from_ = os.getenv("FROM_WA_NUMBER"),
                        body="""Format salah!
Ketik dengan format: *Warung : Nama Warung*  
Contoh: *Warung : Ramirez Jatinangor*""",
)
            
    elif state == "INPUT_LOKASI_WARUNG":  
        try:
            if form_data["MessageType"] == "location":
                latitude = form_data["Latitude"]
                longitude = form_data["Longitude"]

            elif "Latitude :" in form_data["Body"] and "Longitude :" in form_data["Body"]:
                latitude = form_data["Body"].split("Latitude :")[1].split(",")[0].strip()
                longitude = form_data["Body"].split("Longitude :")[1].strip()
                
            else:
                raise HTTPException(status_code=400, detail="Format tidak sesuai")

            if not latitude or not longitude:
                raise HTTPException(status_code=400, detail="Latitude dan Longitude tidak boleh kosong")
            
            latitude = float(latitude)
            longitude = float(longitude)
            
            owner_data = await owner.find_one({"phone_number": form_data["From"]})
            owner_id = owner_data.get("_id")
            await owner.update_one({"phone_number": form_data["From"]}, {"$set": {"state": "MENU"}})

            await warung.update_one({"owner_id": owner_id},{"$set": {"latitude": latitude, "longitude": longitude}})

            # UNCOMMENT KALAU INGIN MENGIRIM PESAN DARI BOT KE USER ($0.01 / msg)
            message = client.messages.create(
                    to = form_data["From"],
                    from_ = os.getenv("FROM_WA_NUMBER"),
                    body=f"""👋 Hai {owner_name}!
Selamat datang di Sobat Warung.
Balas *angka* untuk pilih menu berikut :
1. Setor Penjualan Hari Ini
2. Prediksi Permintaan Besok
3. Cek Stok Warung""",
)
        except Exception:
            # UNCOMMENT KALAU INGIN MENGIRIM PESAN DARI BOT KE USER ($0.01 / msg)
                message = client.messages.create(
                        to = form_data["From"],
                        from_ = os.getenv("FROM_WA_NUMBER"),
                        body="""Format salah!
Kamu bisa kirim *share location* langsung (jika posisi sekarang di warung),
atau *isi manual* koordinatnya.
Ketik dengan format: *Latitude : angka, Longitude : angka*  
Contoh: *Latitude : -6.23, Longitude : 106.82*""",
)
        
    elif state == "MENU":
        if form_data["Body"] == '1': 
            # UNCOMMENT KALAU INGIN MENGIRIM PESAN DARI BOT KE USER ($0.01 / msg)
            message = client.messages.create(
                    to = form_data["From"],
                    from_ = os.getenv("FROM_WA_NUMBER"),
                    body=
                    """Apa saja yang terjual hari ini?  
Ketik dengan format: *Terjual : Barang, jumlah; Barang, jumlah; ...*  
Contoh: *Terjual : Indomie, 10; Teh Gelas, 5*"""
)
        elif "Setor :" in form_data["Body"]:
            pass
        
        elif form_data["Body"] == '2':
            # Panggil Function Predict Model Forecast
            pass 
        
        elif form_data["Body"] == '3':
            # IF TOKO SUDAH INPUT STOK, FETCH STOK DARI DATABASE
            pass

            # ELSE, SURUH TOKO INPUT STOK TERLEBIH DAHULU
            
            # Pilihan 1 : Input lewat WA (dikasi format)
            # Pilihan 2 : Input lewat GForms (dikasi link)

            # UNCOMMENT KALAU INGIN MENGIRIM PESAN DARI BOT KE USER ($0.01 / msg)
            message = client.messages.create(
                    to = form_data["From"],
                    from_ = os.getenv("FROM_WA_NUMBER"),
                    body =
                    """Silahkan input Stok barang toko anda
Ketik dengan format: *Barang, jumlah, harga; Barang, jumlah, harga; ...*
Contoh: *Indomie, 10, 3000; Teh Gelas, 5, 1000*"""
)
        
        else:
            owner_name = (await owner.find_one({"phone_number": form_data["From"]}) or {}).get("owner_name", "Sobat Warung")
            # UNCOMMENT KALAU INGIN MENGIRIM PESAN DARI BOT KE USER ($0.01 / msg)
            message = client.messages.create(
                    to = form_data["From"],
                    from_ = os.getenv("FROM_WA_NUMBER"),
                    body =f"""👋 Hai {owner_name}!
Selamat datang di Sobat Warung.
Balas *angka* untuk pilih menu berikut :
1. Setor Penjualan Hari Ini
2. Prediksi Permintaan Besok
3. Cek Stok Warung""",
)
    
    return "Success"

# @app.post("/ultramsg-whatsapp")
# async def receive_message(request: Request):
#     data = await request.json()
#     print("Incoming Message:", data)

#     sender = data.get("from")

#     url = f"https://api.ultramsg.com/{os.getenv("INSTANCE_ID")}/messages/chat"
#     payload = {"token": os.getenv("TOKEN"), "to": sender, "body": "HAI, SAYA BOT!"}
#     requests.post(url, data=payload)

#     return "Success"