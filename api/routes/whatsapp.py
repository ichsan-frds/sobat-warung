from fastapi import APIRouter, Request, HTTPException
from api.core.twilio import client
import os
from api.misc.messages import Messages
from api.misc.states import State
from api.misc.aggregate import Aggregate
from api.misc.utils import find_similar_product, predict_demand
from api.core.database import owner, warung, stock, product, transaction, forecast
from datetime import datetime, timedelta

router = APIRouter()

def send_message(to: str, body: str):
    print(body)
    # return client.messages.create(
    #     to=to,
    #     from_=os.getenv("FROM_WA_NUMBER"),
    #     body=body
    # )

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
            if "Nama" in form_data["Body"]:
                owner_name = form_data["Body"].split(":")[1].strip()
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
        except Exception as e:
            print(e)
            send_message(form_data["From"], Messages.EXCEPTION_WELCOME_MSG)
    
    elif state == State.INPUT_NAMA_WARUNG.value:
        try:
            if "Warung" in form_data["Body"]:
                warung_name = form_data["Body"].split(":")[1].strip()
                if not warung_name:
                    raise HTTPException(
                        status_code=400, detail="Nama Warung tidak boleh kosong")
            else:
                raise HTTPException(
                    status_code=400, detail="Format tidak sesuai")

            owner_data = await owner.find_one({"phone_number": form_data["From"]})
            owner_id = owner_data.get("_id")
            await warung.insert_one({
                "warung_name": warung_name,
                "owner_id": owner_id,
            })

            await owner.update_one({"phone_number": form_data["From"]}, {
                "$set": {
                    "state": State.INPUT_WILAYAH_WARUNG.value
                    }
                })

            send_message(form_data["From"], Messages.REG_WILAYAH_MSG(warung_name))
        except Exception as e:
            print(e)
            send_message(form_data["From"], Messages.EXCEPTION_REG_WARUNG_MSG)
    
    elif state == State.INPUT_WILAYAH_WARUNG.value:
        try:
            if (
                ("Desa" in form_data["Body"] or "Kelurahan" in form_data["Body"]) 
                and "Kecamatan" in form_data["Body"] 
                and ("Kota" in form_data["Body"] or "Kabupaten" in form_data["Body"]) 
                and "Provinsi" in form_data["Body"]
            ):
                lines = form_data["Body"].split("\n")
                desa_kel = kecamatan = kota_kab = provinsi = None
                for line in lines:
                    if line.startswith("Desa") or line.startswith("Kelurahan"):
                        desa_kel = line.split(":", 1)[1].strip()
                    elif line.startswith("Kecamatan"):
                        kecamatan = line.split(":", 1)[1].strip()
                    elif line.startswith("Kota") or line.startswith("Kabupaten"):
                        kota_kab = line.split(":", 1)[1].strip()
                    elif line.startswith("Provinsi"):
                        provinsi = line.split(":", 1)[1].strip()
                if not desa_kel or not kecamatan or not kota_kab or not provinsi:
                    raise HTTPException(
                        status_code=400, detail="Tidak boleh ada yang kosong")
                
            owner_data = await owner.find_one({"phone_number": form_data["From"]})
            owner_id = owner_data.get("_id")

            await warung.update_one({"owner_id": owner_id},{
                "$set": {
                    "desa/kelurahan": desa_kel, 
                    "kecamatan": kecamatan,
                    "kota/kabupaten": kota_kab,
                    "provinsi": provinsi
                    }
                })
                
            await owner.update_one({"phone_number": form_data["From"]}, {
                "$set": {
                    "state": State.INPUT_LOKASI_WARUNG.value
                    }
                })
            
            send_message(form_data["From"], Messages.REG_LOCATION_MSG)
        except Exception as e:
            print(e)
            send_message(form_data["From"], Messages.EXCEPTION_REG_WILAYAH_MSG)

    elif state == State.INPUT_LOKASI_WARUNG.value:  
        try:
            if form_data["MessageType"] == "location":
                latitude = form_data["Latitude"]
                longitude = form_data["Longitude"]
            elif "Latitude" in form_data["Body"] and "Longitude" in form_data["Body"]:
                latitude, longitude = form_data["Body"].split(",")
                latitude = latitude.split(":")[1].strip()
                longitude = longitude.split(":")[1].strip()
            else:
                raise HTTPException(status_code=400, detail="Format tidak sesuai")

            if not latitude or not longitude:
                raise HTTPException(status_code=400, detail="Latitude dan Longitude tidak boleh kosong")
            
            latitude = float(latitude)
            longitude = float(longitude)
            
            owner_data = await owner.find_one({"phone_number": form_data["From"]})
            owner_id = owner_data.get("_id")
            await warung.update_one({"owner_id": owner_id}, {
                "$set": {
                    "latitude": latitude,
                    "longitude": longitude
                }
            })
            
            await owner.update_one({"phone_number": form_data["From"]}, {
                "$set": {
                    "state": State.TIPE_WARUNG.value
                    }
                })

            send_message(form_data["From"], Messages.REG_TIPE_MSG)
        except Exception as e:
            print(e)
            send_message(form_data["From"], Messages.EXCEPTION_REG_LOCATION_MSG)

    elif state == State.TIPE_WARUNG.value:
        try:
            if form_data["Body"] in ['A', 'B', 'C', 'D']:
                owner_data = await owner.find_one({"phone_number": form_data["From"]})
                owner_id = owner_data.get("_id")
                owner_name = owner_data.get("owner_name", "Sobat Warung")
                await warung.update_one({"owner_id": owner_id},{
                    "$set": {
                        "type": form_data["Body"]
                        }   
                    })
                
                await owner.update_one({"phone_number": form_data["From"]}, {
                    "$set": {
                        "state": State.MENU.value
                        }
                    })

            else:
                raise HTTPException(
                    status_code=400, detail="Format tidak sesuai")
            send_message(form_data["From"], Messages.MENU_MSG(owner_name))
        except Exception as e:
            print(e)
            send_message(form_data["From"], Messages.EXCEPTION_REG_TIPE_MSG)

    elif state == State.MENU.value:
        if form_data["Body"] == '1': 
            owner_data = await owner.find_one({"phone_number": form_data["From"]})
            warung_data = await warung.find_one({"owner_id": owner_data.get("_id")})
            stock_data = await stock.find_one({"warung_id": warung_data.get("_id")})
            
            if not stock_data:
                send_message(form_data["From"], Messages.WARUNG_NO_STOCK)
            else:
                send_message(form_data["From"], Messages.MENU_1_MSG)
        elif "Terjual :" in form_data["Body"]:
            try:
                lines = form_data["Body"].strip().split("\n")

                try:
                    _, first_data = lines[0].split(":", 1)
                    first_data = first_data.strip()
                except ValueError:
                    raise HTTPException(status_code=400, detail="Format tidak sesuai")
                
                owner_data = await owner.find_one({"phone_number": form_data["From"]})
                warung_data = await warung.find_one({"owner_id": owner_data["_id"]})
                warung_id = warung_data["_id"]

                product_lines = [first_data.strip()] + lines[1:]
                    
                for line in product_lines:
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) != 2:
                        raise HTTPException(status_code=400, detail=f"Format tidak sesuai: {line}")

                    product_name = parts[0]
                    quantity_sold = int(parts[1])

                    product_data = await find_similar_product(product_name)
                    if not product_data:
                        raise HTTPException(status_code=404, detail=f"Produk '{name}' tidak ditemukan")
                    else:
                        product_id = product_data["_id"]

                    stock_data = await stock.find_one({"warung_id": warung_id, "product_id": product_id})
                    if not stock_data:
                        raise HTTPException(status_code=404, detail=f"Stok produk '{product_data['product_name']}' tidak ditemukan")
                    if quantity_sold > stock_data["stock_count"]:
                        raise HTTPException(
                            status_code=404,
                            detail=(
                                f"Stok {product_data['product_name']} kurang (tersedia {stock_data['stock_count']})"
                            )
                        )
                    product_price = stock_data["price"]

                    await transaction.insert_one(
                        {
                            "date": datetime.now(),
                            "warung_id": warung_id,
                            "product_id": product_id,
                            "quantity_sold": quantity_sold,
                            "total_price": quantity_sold * product_price
                        }
                    )

                    await stock.update_one(
                        {"warung_id": warung_id, "product_id": product_id},
                        {
                            "$inc": {"stock_count": -quantity_sold},
                            "$set": {"last_transaction": datetime.now()}
                        }
                    )

                owner_data = await owner.find_one({"phone_number": form_data["From"]})
                owner_name = owner_data.get("owner_name", "Sobat Warung")
                send_message(form_data["From"], Messages.MENU_POST_INPUT_MSG(owner_data["owner_name"]))

            except Exception as e:
                if isinstance(e, HTTPException) and e.status_code == 404:
                    send_message(form_data["From"], Messages.EXCEPTION_MENU_1_MSG(e.status_code, e.detail))
                else:
                    print(e)
                    send_message(form_data["From"], Messages.EXCEPTION_MENU_1_MSG())
        
        elif form_data["Body"] == '2':
            owner_data = await owner.find_one({"phone_number": form_data["From"]})
            owner_id = owner_data["_id"]
            
            warung_data = await warung.find_one({"owner_id": owner_id})
            warung_id = warung_data["_id"]
            
            today = datetime.now().date()
            start = datetime.combine(today, datetime.min.time())
            end = datetime.combine(today + timedelta(days=1), datetime.min.time())
            
            today_transactions = await transaction.find({
                "warung_id": warung_id,
                "date": {
                    "$gte": start,
                    "$lt": end
                }
            }).to_list(length=None)

            if today_transactions:
                forecast_results = predict_demand(today_transactions)
                
                for f in forecast_results:
                    await forecast.insert_one({
                        "date": datetime.now(),
                        "warung_id": warung_id,
                        "product_id": f["product_id"],
                        "predicted_sell": f["predicted_sell"]
                    })
                    
                insight_text = "Rekomendasi restock:\n"
                for f in forecast_results:
                    prod_data = await product.find_one({"_id": f["product_id"]})
                    prod_name = prod_data["product_name"] if prod_data else "Produk tidak diketahui"
                    insight_text += f"- {prod_name}: {f['predicted_sell']} pcs\n"
                
                send_message(form_data["From"], insight_text.strip())
            else:
                send_message(form_data["From"], "Belum ada transaksi hari ini. Silakan input data transaksi terlebih dahulu.")
        
        elif form_data["Body"] == '3':
            # IF TOKO SUDAH INPUT STOK, FETCH STOK DARI DATABASE
            pipeline = Aggregate.get_stock_by_phone_pipeline(form_data["From"])
            cursor = await owner.aggregate(pipeline)
            results = await cursor.to_list(length=None)

            # ELSE, SURUH TOKO INPUT STOK TERLEBIH DAHULU
            if not results:
                await owner.update_one({"phone_number": form_data["From"]}, {
                    "$set": {
                        "state": State.INPUT_STOK.value
                        }
                    })
                
                send_message(form_data["From"], Messages.MENU_3_INPUT_STOK_MSG)
            else:
                stock_list = "\n".join(
                    f"{item['product_name']}, {item['stock_count']}, {item['price']}"
                    for item in results
                )

                send_message(form_data["From"], Messages.MENU_3_CEK_STOK_MSG(stock_list))
                send_message(form_data["From"], Messages.CEK_STOK_CHOICES_MSG)

        elif form_data["Body"] in ['Tambah', 'Update', 'Hapus']:
            await owner.update_one({"phone_number": form_data["From"]}, {
                    "$set": {
                        "state": State.EDIT_STOK.value
                        }
                    })
            send_message(form_data["From"], Messages.MENU_3_EDIT_STOK_MSG(form_data["Body"]))

        else:
            owner_name = (await owner.find_one({"phone_number": form_data["From"]}) or {}).get("owner_name", "Sobat Warung")
            send_message(form_data["From"], Messages.MENU_MSG(owner_name))

    elif state == State.EDIT_STOK.value:
        if form_data["Body"] in ['Tambah', 'Update', 'Hapus']:
            await owner.update_one({"phone_number": form_data["From"]}, {
                    "$set": {
                        "state": State.EDIT_STOK.value
                        }
                    })
            send_message(form_data["From"], Messages.MENU_3_EDIT_STOK_MSG(form_data["Body"]))
        if form_data["Body"] == 'Menu':
            await owner.update_one({"phone_number": form_data["From"]}, {
                    "$set": {
                        "state": State.MENU.value
                        }
                    })
            owner_name = (await owner.find_one({"phone_number": form_data["From"]}) or {}).get("owner_name", "Sobat Warung")
            send_message(form_data["From"], Messages.MENU_MSG(owner_name))
        else:
            try:
                lines = form_data["Body"].strip().split("\n")
                edit_type = None

                # Ambil edit_type & first_data dari baris pertama
                try:
                    edit_type, first_data = lines[0].split(":", 1)
                    edit_type = edit_type.strip()
                    first_data = first_data.strip()
                except ValueError:
                    raise HTTPException(status_code=400, detail="Format tidak sesuai")

                # Validasi edit_type
                if edit_type not in ["Tambah", "Update", "Hapus"]:
                    raise HTTPException(status_code=400, detail="Format tidak sesuai")

                owner_data = await owner.find_one({"phone_number": form_data["From"]})
                warung_data = await warung.find_one({"owner_id": owner_data["_id"]})
                warung_id = warung_data["_id"]
                
                if edit_type in ["Tambah", "Update"]:
                    # Gabungkan ulang data produk (baris pertama tanpa edit_type + baris lainnya)
                    product_lines = [first_data.strip()] + lines[1:]
                    
                    for line in product_lines:
                        parts = [p.strip() for p in line.split(",")]
                        if len(parts) != 3:
                            raise HTTPException(status_code=400, detail=f"Format tidak sesuai: {line}")

                        product_name = parts[0]
                        stock_count = int(parts[1])
                        price = int(parts[2])

                        product_data = await find_similar_product(product_name)
                        if not product_data:
                            insert_result = await product.insert_one({"product_name": product_name})
                            product_id = insert_result.inserted_id
                            new_stock_count = stock_count
                        else:
                            stock_data = await stock.find_one({"product_id": product_data.get("_id"), "warung_id": warung_id})
                            if stock_data:
                                new_stock_count = int(stock_data.get("stock_count")) + stock_count
                            
                            product_id = product_data["_id"]

                        await stock.update_one(
                            {"warung_id": warung_id, "product_id": product_id},
                            {"$set": {"stock_count": new_stock_count, "price": price, "last_transaction": datetime.now()}},
                            upsert=True
                        )
                else:
                    # Ambil semua produk (baris pertama tanpa edit_type + baris berikutnya)
                    product_names = [first_data.strip()] + [line.strip() for line in lines[1:]]

                    for name in product_names:
                        if not name:  # kalau kosong
                            raise HTTPException(status_code=400, detail=f"Format tidak sesuai: {name}")

                        product_data = await find_similar_product(name)
                        if not product_data:
                            raise HTTPException(status_code=404, detail=f"Produk '{name}' tidak ditemukan")
                        else:
                            product_id = product_data["_id"]

                        await stock.delete_one({"warung_id": warung_id, "product_id": product_id})

                await owner.update_one({"phone_number": form_data["From"]}, {
                        "$set": {
                            "state": State.MENU.value
                            }
                    })
                owner_data = await owner.find_one({"phone_number": form_data["From"]})
                owner_name = owner_data.get("owner_name", "Sobat Warung")
                send_message(form_data["From"], Messages.MENU_POST_INPUT_MSG(owner_data["owner_name"]))
                
            except Exception as e:
                if isinstance(e, HTTPException) and e.status_code == 404:
                    send_message(form_data["From"], Messages.EXCEPTION_MENU_3_EDIT_STOK_MSG(edit_type, e.status_code, e.detail))
                else:
                    print(e)
                    send_message(form_data["From"], Messages.EXCEPTION_MENU_3_EDIT_STOK_MSG(edit_type))

    elif state == State.INPUT_STOK.value:
        if form_data["Body"] == 'Menu':
            await owner.update_one({"phone_number": form_data["From"]}, {
                    "$set": {
                        "state": State.MENU.value
                        }
                    })
            owner_name = (await owner.find_one({"phone_number": form_data["From"]}) or {}).get("owner_name", "Sobat Warung")
            send_message(form_data["From"], Messages.MENU_MSG(owner_name))
        else:
            try:
                owner_data = await owner.find_one({"phone_number": form_data["From"]})
                warung_data = await warung.find_one({"owner_id": owner_data["_id"]})
                warung_id = warung_data["_id"]

                lines = form_data["Body"].split("\n")
                for line in lines:
                    parts = line.split(",")
                    if len(parts) != 3:
                        raise HTTPException(
                            status_code=400, detail="Format tidak sesuai")
                    
                    product_name = parts[0].strip()
                    stock_count = int(parts[1].strip())
                    price = int(parts[2].strip())

                    product_data = await find_similar_product(product_name)
                    if not product_data:
                        insert_result = await product.insert_one({"product_name": product_name})
                        product_id = insert_result.inserted_id
                    else:
                        product_id = product_data["_id"]
                    
                    await stock.update_one(
                        {"warung_id": warung_id, "product_id": product_id},
                        {"$set": {"stock_count": stock_count, "price": price, "last_transaction": datetime.now()}},
                        upsert=True
                    )

                    await owner.update_one({"phone_number": form_data["From"]}, {
                        "$set": {
                            "state": State.MENU.value
                            }
                    })
                    owner_data = await owner.find_one({"phone_number": form_data["From"]})
                    owner_name = owner_data.get("owner_name", "Sobat Warung")
                    
                send_message(form_data["From"], Messages.MENU_POST_INPUT_MSG(owner_data["owner_name"]))
            except Exception as e:
                print(e)
                send_message(form_data["From"], Messages.EXCEPTION_MENU_3_INPUT_STOK_MSG)