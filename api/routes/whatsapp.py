from fastapi import APIRouter, Request, HTTPException
from api.core.twilio import client
import os
from api.misc.messages import Messages
from api.misc.states import State
from api.core.database import owner, warung

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
    print("Incomming:\n", form_data)
    
    state = (await owner.find_one({"phone_number": form_data["From"]}) or {}).get("state")
    
    if state is None:
        await owner.insert_one({
            "phone_number": form_data["From"],
            "state": State.WAITING_FOR_NAME.value
        })
        
        send_message(form_data["From"], Messages.WELCOME_MSG)
    elif state == State.WAITING_FOR_NAME.value:
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

            send_message(form_data["From"], Messages.REG_LOCATION_MSG(warung_name))
        except Exception:
            send_message(form_data["From"], Messages.EXCEPTION_REG_WARUNG_MSG)
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

            send_message(form_data["From"], Messages.MENU_MSG(owner_name))
        except Exception:
            send_message(form_data["From"], Messages.EXCEPTION_REG_LOCATION_MSG)
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
            send_message(form_data["From"], Messages.MENU_MSG(owner_name))