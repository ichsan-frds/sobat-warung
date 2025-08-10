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

    def REG_LOCATION_MSG():
        return """Kemudian silahkan isi lokasi warungmu.
Kamu bisa kirim *share location* langsung (jika posisi sekarang di warung),
atau *isi manual* koordinatnya.
Ketik dengan format: *Latitude : angka, Longitude : angka*  
Contoh: *Latitude : -6.23, Longitude : 106.82*"""

    EXCEPTION_REG_LOCATION_MSG = """Format salah!
Kamu bisa kirim *share location* langsung (jika posisi sekarang di warung),
atau *isi manual* koordinatnya.
Ketik dengan format: *Latitude : angka, Longitude : angka*  
Contoh: *Latitude : -6.23, Longitude : 106.82*"""

    def REG_TIPE_MSG():
        return """Kemudian silahkan isi tipe warungmu.
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
    
    def MENU_1_MSG():
        return """Apa saja yang terjual hari ini?  
Ketik dengan format: *Terjual : Barang, jumlah; Barang, jumlah; ...*  
Contoh: *Terjual : Indomie, 10; Teh Gelas, 5*"""