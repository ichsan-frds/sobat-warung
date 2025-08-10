from fastapi import APIRouter, Request, HTTPException
from api.core.twilio import client
import os
from api.misc.messages import Messages
from api.misc.states import State
from api.core.database import owner, warung, stock

router = APIRouter()

def send_message(to: str, body: str):
    return client.messages.create(
        to=to,
        from_=os.getenv("FROM_WA_NUMBER"),
        body=body
    )

@router.post("/")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()
    print("Incoming:\n", form_data) # UNCOMMENT DI PRODUCTION
    
    state = (await owner.find_one({"phone_number": form_data["From"]}) or {}).get("state")
    
    if state is None:
        await owner.insert_one({
            "phone_number": form_data["From"],
            "state": State.INPUT_NAMA.value
        })
        send_message(form_data["From"], Messages.WELCOME_MSG)
    
    elif state == State.INPUT_NAMA.value:
        try:
            if "Nama :" in form_data["Body"]:
                owner_name = form_data["Body"].split("Nama :")[1].strip()
                if not owner_name:
                    raise HTTPException(
                        status_code=400, detail="Nama Panggilan tidak boleh kosong")
            else:
                raise HTTPException(
                    status_code=400, detail="Format tidak sesuai")

            await owner.update_one({"phone_number": form_data["From"]}, {
                "$set": {
                    "owner_name": owner_name, 
                    "state": State.INPUT_NAMA_WARUNG.value
                    }
                })

            send_message(form_data["From"], Messages.REG_WARUNG_MSG(owner_name))
        except Exception:
            send_message(form_data["From"], Messages.EXCEPTION_WELCOME_MSG)
    
    elif state == State.INPUT_NAMA_WARUNG.value:
        try:
            if "Warung :" in form_data["Body"]:
                warung_name = form_data["Body"].split("Warung :")[1].strip()
                if not warung_name:
                    raise HTTPException(
                        status_code=400, detail="Nama Warung tidak boleh kosong")
            else:
                raise HTTPException(
                    status_code=400, detail="Format tidak sesuai")

            owner_data = await owner.find_one({"phone_number": form_data["From"]})
            owner_id = owner_data.get("_id")
            await owner.update_one({"phone_number": form_data["From"]}, {
                "$set": {
                    "state": "INPUT_LOKASI_WARUNG"
                    }
                })

            await warung.insert_one({
                "warung_name": warung_name,
                "owner_id": owner_id,
            })

            send_message(form_data["From"], Messages.REG_WILAYAH_MSG(warung_name))
        except Exception:
            send_message(form_data["From"], Messages.EXCEPTION_REG_WARUNG_MSG)
    
    elif state == State.INPUT_WILAYAH_WARUNG.value:
        try:
            if (
                ("Desa :" in form_data["Body"] or "Kelurahan :" in form_data["Body"]) 
                and "Kecamatan :" in form_data["Body"] 
                and ("Kota :" in form_data["Body"] or "Kabupaten :" in form_data["Body"]) 
                and "Provinsi :" in form_data["Body"]
            ):
                lines = form_data["Body"].split("\n")
                desa_kel = kecamatan = kota_kab = provinsi = None
                for line in lines:
                    if line.startswith("Desa :") or line.startswith("Kelurahan :"):
                        desa_kel = line.split(":", 1)[1].strip()
                    elif line.startswith("Kecamatan :"):
                        kecamatan = line.split(":", 1)[1].strip()
                    elif line.startswith("Kota :") or line.startswith("Kabupaten :"):
                        kota_kab = line.split(":", 1)[1].strip()
                    elif line.startswith("Provinsi :"):
                        provinsi = line.split(":", 1)[1].strip()
                if not desa_kel or not kecamatan or not kota_kab or not provinsi:
                    raise HTTPException(
                        status_code=400, detail="Tidak boleh ada yang kosong")
                
            owner_data = await owner.find_one({"phone_number": form_data["From"]})
            owner_id = owner_data.get("_id")
            await owner.update_one({"phone_number": form_data["From"]}, {"$set": {"state": "INPUT_LOKASI_WARUNG"}})

            await warung.update_one({"owner_id": owner_id},
                                    {"$set": {"desa/kelurahan": desa_kel, 
                                            "kecamatan": kecamatan,
                                            "kota/kabupaten": kota_kab,
                                            "provinsi": provinsi}})
                
            send_message(form_data["From"], Messages.REG_LOCATION_MSG())
        except Exception:
            send_message(form_data["From"], Messages.EXCEPTION_REG_WILAYAH_MSG)

    elif state == State.INPUT_LOKASI_WARUNG.value:  
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
            owner_id = owner_data.get("owner_id")
            await owner.update_one({"phone_number": form_data["From"]}, {
                "$set": {
                    "state": "MENU"
                    }
                })

            await warung.update_one({"owner_id": owner_id}, {
                "$set": {
                    "latitude": latitude, 
                    "longitude": longitude
                    }
                })

            send_message(form_data["From"], Messages.REG_TIPE_MSG())
        except Exception:
            send_message(form_data["From"], Messages.EXCEPTION_REG_LOCATION_MSG)
    
    elif state == State.TIPE_WARUNG.value:
        try:
            if form_data["Body"] in ['A', 'B', 'C', 'D']:
                owner_data = await owner.find_one({"phone_number": form_data["From"]})
                owner_id = owner_data.get("_id")
                owner_name = owner_data.get("owner_name", "Sobat Warung")
                await owner.update_one({"phone_number": form_data["From"]}, {"$set": {"state": "MENU"}})

                await warung.update_one({"owner_id": owner_id},{"$set": {"type": form_data["Body"]}})
                
            else:
                raise HTTPException(
                    status_code=400, detail="Format tidak sesuai")
            send_message(form_data["From"], Messages.MENU_MSG(owner_name))
        except Exception:
            send_message(form_data["From"], Messages.EXCEPTION_REG_TIPE_MSG)

    elif state == State.MENU.value:
        if form_data["Body"] == '1': 
            send_message(form_data["From"], Messages.MENU_1_MSG())
        elif "Terjual :" in form_data["Body"]:
            pass
        
        elif form_data["Body"] == '2':
            # Panggil Function Predict Model Forecast
            pass 
        
        elif form_data["Body"] == '3':
            # IF TOKO SUDAH INPUT STOK, FETCH STOK DARI DATABASE
            owner_data = await owner.find_one({"phone_number": form_data["From"]})
            owner_id = owner_data.get("_id")
            warung_data = await warung.find_one({"owner_id": owner_id})
            warung_id = warung_data.get("_id")
            stock_data = (await stock.find({"warung_id": warung_id}) or {}).get()
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
            send_message(form_data["From"], Messages.MENU_MSG(owner_name))