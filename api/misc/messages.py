class Messages():
    WELCOME_MSG = """Selamat datang di Sobat Warung! 👋
Yuk mulai dengan isi namamu dulu!
Ketik dengan format: *Nama : Nama Panggilan*  
Contoh: *Nama : Budi*"""

    def REG_WARUNG_MSG(owner_name: str):
        return f"""👋 Hai *{owner_name}*!
Sekarang lanjut dengan isi nama warungmu.                    
Ketik dengan format: *Warung : Nama Warung*  
Contoh: *Warung : Ramirez Jatinangor*"""

    EXCEPTION_WELCOME_MSG = """Format salah!
Ketik dengan format: *Nama : Nama Panggilan*  
Contoh: *Nama : Budi*"""

    def REG_LOCATION_MSG(warung_name: str):
        return f"""Terimakasih *{warung_name}*!
Terakhir silahkan isi lokasi warungmu.
Kamu bisa kirim *share location* langsung (jika posisi sekarang di warung),
atau *isi manual* koordinatnya.
Ketik dengan format: *Latitude : angka, Longitude : angka*  
Contoh: *Latitude : -6.23, Longitude : 106.82*"""

    EXCEPTION_REG_WARUNG_MSG = """Format salah!
Ketik dengan format: *Warung : Nama Warung*  
Contoh: *Warung : Ramirez Jatinangor*"""

    def MENU_MSG(owner_name: str):
        return f"""👋 Hai {owner_name}!
Selamat datang di Sobat Warung.
Balas *angka* untuk pilih menu berikut :
1. Setor Penjualan Hari Ini
2. Prediksi Permintaan Besok
3. Cek Stok Warung"""

    EXCEPTION_REG_LOCATION_MSG = """Format salah!
Kamu bisa kirim *share location* langsung (jika posisi sekarang di warung),
atau *isi manual* koordinatnya.
Ketik dengan format: *Latitude : angka, Longitude : angka*  
Contoh: *Latitude : -6.23, Longitude : 106.82*"""