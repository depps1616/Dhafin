import os
import json
import datetime
import getpass

class TabunganATM:
    USER_FILE = "users.json"
    REKENING_FILE = "rekening.json"
    TABUNGAN_FILE = "tabungan.json"
    HISTORY_FILE = "history.json"

    default_users = {
        "andi": {"password": "passandi"},
        "budi": {"password": "passbudi"},
        "citra": {"password": "passcitra"}
    }

    default_rekening = {
        "1111": {"pin": "1234", "saldo": 1500000},
        "2222": {"pin": "2345", "saldo": 2500000},
        "3333": {"pin": "3456", "saldo": 500000}
    }

    def __init__(self):
        self.ensure_files_exist()
        self.users = self.load_json(self.USER_FILE)
        self.rekening_db = self.load_json(self.REKENING_FILE)
        self.tabungan = self.load_json(self.TABUNGAN_FILE)
        self.history = self.load_json(self.HISTORY_FILE)
        self.user_aktif = None

    def ensure_files_exist(self):
        self.save_if_not_exists(self.USER_FILE, self.default_users)
        self.save_if_not_exists(self.REKENING_FILE, self.default_rekening)
        self.save_if_not_exists(self.TABUNGAN_FILE, {"saldo_tabungan": 0})
        self.save_if_not_exists(self.HISTORY_FILE, {})

    def save_if_not_exists(self, filename, data):
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)

    def load_json(self, filename):
        with open(filename, "r") as f:
            return json.load(f)

    def save_json(self, filename, data):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def login(self):
        print("===== LOGIN =====")
        for _ in range(3):
            username = input("Masukkan nama pengguna: ").lower()
            password = getpass.getpass("Masukkan password: ")
            if username in self.users and self.users[username]["password"] == password:
                self.user_aktif = username
                print("Login berhasil!\n")
                return
            else:
                print("Nama atau password salah.\n")
        print("Terlalu banyak percobaan. Program keluar.")
        exit()

    def validasi_rekening(self):
        norek = input("Masukkan nomor rekening: ")
        pin = getpass.getpass("Masukkan PIN rekening: ")
        if norek in self.rekening_db and self.rekening_db[norek]["pin"] == pin:
            return norek
        else:
            print("Nomor rekening atau PIN salah.")
            return None

    def tambah_history(self, jenis, norek, jumlah):
        waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.user_aktif not in self.history:
            self.history[self.user_aktif] = []
        self.history[self.user_aktif].append({
            "waktu": waktu,
            "jenis": jenis,
            "rekening": norek,
            "jumlah": jumlah
        })
        self.save_json(self.HISTORY_FILE, self.history)

    def cetak_struk(self, jenis, norek, jumlah):
        waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        saldo_rekening = self.rekening_db[norek]["saldo"]
        saldo_tabungan = self.tabungan["saldo_tabungan"]
        print("\n========== STRUK TRANSAKSI ==========")
        print(f"Tanggal/Waktu  : {waktu}")
        print(f"Nama Pengguna  : {self.user_aktif.capitalize()}")
        print(f"No. Rekening   : {norek}")
        print(f"Jenis Transaksi: {jenis}")
        print(f"Jumlah         : Rp{jumlah:,}")
        print(f"Saldo Rekening : Rp{saldo_rekening:,}")
        print(f"Saldo Tabungan : Rp{saldo_tabungan:,}")
        print("=====================================\n")

    def menu(self):
        while True:
            self.clear_screen()
            print(f"=== Selamat datang, {self.user_aktif.capitalize()} ===")
            print("1. Cek Saldo Tabungan")
            print("2. Setor ke Tabungan")
            print("3. Tarik dari Tabungan")
            print("4. Lihat Riwayat Transaksi Semua Akun")
            print("5. Logout")
            print("==============================")

            pilihan = input("Masukkan pilihan (1-5): ")

            if pilihan == "1":
                print(f"Saldo Tabungan Bersama: Rp{self.tabungan['saldo_tabungan']:,}")

            elif pilihan == "2":
                norek = self.validasi_rekening()
                if norek:
                    try:
                        jumlah = int(input("Masukkan jumlah setor (min Rp20.000): Rp"))
                        if jumlah < 20000:
                            print("Jumlah minimal setor adalah Rp20.000.")
                        elif self.rekening_db[norek]["saldo"] >= jumlah:
                            self.rekening_db[norek]["saldo"] -= jumlah
                            self.tabungan["saldo_tabungan"] += jumlah
                            self.save_json(self.REKENING_FILE, self.rekening_db)
                            self.save_json(self.TABUNGAN_FILE, self.tabungan)
                            self.tambah_history("Setor ke Tabungan", norek, jumlah)
                            print("Setor berhasil.")
                            self.cetak_struk("Setor ke Tabungan", norek, jumlah)
                        else:
                            print("Saldo rekening tidak mencukupi.")
                    except ValueError:
                        print("Input tidak valid.")

            elif pilihan == "3":
                norek = self.validasi_rekening()
                if norek:
                    try:
                        jumlah = int(input("Masukkan jumlah tarik: Rp"))
                        if jumlah <= 0:
                            print("Jumlah harus lebih dari 0.")
                        elif self.tabungan["saldo_tabungan"] >= jumlah:
                            self.tabungan["saldo_tabungan"] -= jumlah
                            self.rekening_db[norek]["saldo"] += jumlah
                            self.save_json(self.TABUNGAN_FILE, self.tabungan)
                            self.save_json(self.REKENING_FILE, self.rekening_db)
                            self.tambah_history("Tarik dari Tabungan", norek, jumlah)
                            print("Tarik berhasil.")
                            self.cetak_struk("Tarik dari Tabungan", norek, jumlah)
                        else:
                            print("Saldo tabungan tidak mencukupi.")
                    except ValueError:
                        print("Input tidak valid.")

            elif pilihan == "4":
                print("\n===== Riwayat Transaksi Semua Akun =====")
                semua_transaksi = [
                    {**item, "user": user}
                    for user, list_trans in self.history.items()
                    for item in list_trans
                ]
                semua_transaksi.sort(key=lambda x: x["waktu"])
                if not semua_transaksi:
                    print("Belum ada riwayat transaksi.")
                else:
                    for idx, transaksi in enumerate(semua_transaksi, 1):
                        print(f"{idx}. [{transaksi['waktu']}] {transaksi['jenis']} "
                              f"Rp{transaksi['jumlah']:,} oleh {transaksi['user'].capitalize()} "
                              f"ke Rek {transaksi['rekening']}")
                print("=========================================")

            elif pilihan == "5":
                print("Logout berhasil.")
                break

            else:
                print("Pilihan tidak valid.")

            input("\nTekan ENTER untuk kembali ke menu...")

    def run(self):
        while True:
            self.clear_screen()
            self.users = self.load_json(self.USER_FILE)
            self.rekening_db = self.load_json(self.REKENING_FILE)
            self.tabungan = self.load_json(self.TABUNGAN_FILE)
            self.history = self.load_json(self.HISTORY_FILE)
            self.login()
            self.menu()
            break


if __name__ == "__main__":
    atm = TabunganATM()
    atm.run()
