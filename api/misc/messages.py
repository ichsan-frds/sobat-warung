class Messages():
    WELCOME_MSG = """Selamat datang di Sobat Warung! 👋
Yuk mulai dengan isi namamu dulu!
Ketik dengan format: *Nama : Nama Panggilan*  
Contoh: *Nama : Budi*"""

    EXCEPTION_WELCOME_MSG = """Format salah!
Ketik dengan format: *Nama : Nama Panggilan*  
Contoh: *Nama : Budi*"""

    def REG_WARUNG_MSG(owner_name: str):
        return f"""👋 Hai *{owner_name}*!
Sekarang lanjut dengan isi nama warungmu.                    
Ketik dengan format: *Warung : Nama Warung*  
Contoh: *Warung : Ramirez Jatinangor*"""

    EXCEPTION_REG_WARUNG_MSG = """Format salah!
Ketik dengan format: *Warung : Nama Warung*  
Contoh: *Warung : Ramirez Jatinangor*"""

    def REG_WILAYAH_MSG(warung_name: str):
        return f"""Terimakasih *{warung_name}*!
Kemudian silahkan isi wilayah warungmu.  
Contoh: *Desa : Bojong Kulur*
*Kecamatan : Gunung Putri*
*Kabupaten : Bogor*
*Provinsi : Jawa Barat*

❗Tulis setiap informasi di baris baru (tekan *Enter*
atau *Shift+Enter* di PC/Laptop)"""
    
    EXCEPTION_REG_WILAYAH_MSG = """Format salah!
❗Tulis setiap informasi di baris baru (tekan *Enter*
atau *Shift+Enter* di PC/Laptop)
Contoh: *Desa : Bojong Kulur*
*Kecamatan : Gunung Putri*
*Kabupaten : Bogor*
*Provinsi : Jawa Barat*"""

    REG_LOCATION_MSG = """Kemudian silahkan isi lokasi warungmu.
Kamu bisa kirim *share location* langsung (jika posisi sekarang di warung),
atau *isi manual* koordinatnya.
Ketik dengan format: *Latitude : angka, Longitude : angka*  
Contoh: *Latitude : -6.23, Longitude : 106.82*"""

    EXCEPTION_REG_LOCATION_MSG = """Format salah!
Kamu bisa kirim *share location* langsung (jika posisi sekarang di warung),
atau *isi manual* koordinatnya.
Ketik dengan format: *Latitude : angka, Longitude : angka*  
Contoh: *Latitude : -6.23, Longitude : 106.82*"""

    REG_TIPE_MSG = """Kemudian silahkan isi tipe warungmu.
Balas *A/B/C/D* sesuai *jumlah barang merk berbeda* yang dijual warung-mu:
A. Menjual > 100 Barang Beda Merk
B. Menjual 50 - 100 Barang Beda Merk
C. Menjual 20 - 50 Barang Beda Merk
D. Menjual < 20 Barang Beda Merk"""
    
    EXCEPTION_REG_TIPE_MSG = """Format salah!
Balas *A/B/C/D* sesuai *jumlah barang merk berbeda* yang dijual warung-mu:
A. Menjual > 100 Barang Beda Merk
B. Menjual 50 - 100 Barang Beda Merk
C. Menjual 20 - 50 Barang Beda Merk
D. Menjual < 20 Barang Beda Merk"""

    def MENU_MSG(owner_name: str):
        return f"""👋 Hai {owner_name}!
Selamat datang di Sobat Warung.
Balas *angka* untuk pilih menu berikut :
1. Setor Penjualan Hari Ini
2. Prediksi Permintaan Besok
3. Cek Stok Warung"""
    
    MENU_1_MSG = """Apa saja yang terjual hari ini?  
Ketik dengan format: 
*Terjual : Barang1, jumlah1* 
*Barang2, jumlah2*
Contoh: 
*Terjual : Indomie Goreng, 10*
*Indomie Kari Ayam, 15*

Ketik *Menu* untuk kembali ke menu utama
❗Tulis setiap informasi di baris baru (tekan *Enter*
atau *Shift+Enter* di PC/Laptop)"""

    def EXCEPTION_MENU_1_MSG(error_status_code: int = 400, error_message: str = "Format salah!"):
        return f"""{error_message}
❗Tulis setiap informasi di baris baru (tekan *Enter*
atau *Shift+Enter* di PC/Laptop)
Ketik *Menu* untuk kembali ke menu utama

Ketik dengan format: 
*Terjual : Barang1, jumlah1* 
*Barang2, jumlah2*
Contoh: 
*Terjual : Indomie Goreng, 10*
*Indomie Kari Ayam, 15*"""

    def MENU_3_CEK_STOK_MSG(stock_list: str):
        return f"""*Nama Barang*, *Stok Barang*, *Harga Barang*

{stock_list}
"""
    
    CEK_STOK_CHOICES_MSG = """
Tambah Barang   -> Ketik *Tambah*
(Menambah Barang yang belum ada di stok)
Update Barang   -> Ketik *Update*
(Memperbaharui nama, jumlah stok, atau harga barang)
Hapus Barang    -> Ketik *Hapus*
(Menghapus Barang yang ada di stok)
Menu Utama      -> Ketik *Menu*
"""

    def MENU_3_EDIT_STOK_MSG(edit_type: str):
        if edit_type in ["Tambah", "Update"]:
            message = f"""*{edit_type} Barang*
Ketik dengan format: 
*{edit_type} : Barang1, jumlah1, harga1* 
*Barang2, jumlah2, harga2*
Contoh: 
*{edit_type} : Indomie Goreng, 10, 3000*
*Indomie Kari Ayam, 15, 3000*"""
        
        else:
            message = f"""*{edit_type} Barang*
Ketik dengan format: 
*{edit_type} : Barang1* 
*Barang2*
Contoh: 
*{edit_type} : Indomie Goreng*
*Indomie Kari Ayam*"""
            
        return f"""{message}
        
Ketik *Menu* untuk kembali ke menu utama
❗Tulis setiap informasi di baris baru (tekan *Enter*
atau *Shift+Enter* di PC/Laptop)
"""
    
    def EXCEPTION_MENU_3_EDIT_STOK_MSG(edit_type: str, error_status_code: int = 400, error_message: str = "Format salah!"):
        if edit_type in ["Tambah", "Update"]:
            message = f"""*{edit_type} Barang*
Ketik dengan format: 
*{edit_type} : Barang1, jumlah1, harga1* 
*Barang2, jumlah2, harga2*
Contoh: 
*{edit_type} : Indomie Goreng, 10, 3000*
*Indomie Kari Ayam, 15, 3000*"""
        
        else:
            message = f"""*{edit_type} Barang*
Ketik dengan format: 
*{edit_type} : Barang1* 
*Barang2*
Contoh: 
*{edit_type} : Indomie Goreng*
*Indomie Kari Ayam*"""

        return f"""{error_message}
❗Tulis setiap informasi di baris baru (tekan *Enter*
atau *Shift+Enter* di PC/Laptop)
Ketik *Menu* untuk kembali ke menu utama

{message}"""

    MENU_3_INPUT_STOK_MSG = """Silahkan input Stok barang toko anda
Ketik dengan format: *Barang1, jumlah1, harga1* 
*Barang2, jumlah2, harga2*
dst

Contoh: *Indomie Goreng, 10, 3000*
*Indomie Kari Ayam, 15, 3000*
*Aqua 600 mL, 20, 4000*
*Aqua 1.5 L, 20, 8000*
*Aqua Gelas 1 Dus, 5, 45000*

Ketik *Menu* untuk kembali ke menu utama
❗Tulis setiap informasi di baris baru (tekan *Enter*
atau *Shift+Enter* di PC/Laptop)"""

    EXCEPTION_MENU_3_INPUT_STOK_MSG = """Format salah!
❗Tulis setiap informasi di baris baru (tekan *Enter*
atau *Shift+Enter* di PC/Laptop)
Ketik *Menu* untuk kembali ke menu utama

Contoh: *Indomie Goreng, 10, 3000*
*Indomie Kari Ayam, 15, 3000*
*Aqua 600 mL, 20, 4000*
*Aqua 1.5 L, 20, 8000*
*Aqua Gelas 1 Dus, 5, 45000*"""

    def MENU_POST_INPUT_MSG(owner_name: str):
        return f"""Terimakasih sudah meng-update stok {owner_name}!
Selamat datang di Sobat Warung.
Balas *angka* untuk pilih menu berikut :
1. Setor Penjualan Hari Ini
2. Prediksi Permintaan Besok
3. Cek Stok Warung"""