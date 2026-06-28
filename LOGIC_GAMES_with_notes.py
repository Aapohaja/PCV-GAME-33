"""
Versi beranotasi dari LOGIC GAMES.py.
Setiap blok kode diberi komentar penjelasan di sebelah atau tepat di atasnya.
"""

import random  # Mengacak kartu
import tkinter as tk  # Membuat UI desktop sederhana

# --- KONFIGURASI KARTU & ATURAN ---
# Daftar jenis kartu, angka kartu, dan nilai numeriknya.
SUITS = ['Heart', 'Diamond', 'Club', 'Spade']  # 4 jenis kartu remi standar
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']  # 13 nilai kartu dari 2 sampai As
VALUES = {  # Dictionary untuk mapping rank ke nilai numerik
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,  # Angka 2-9 = nilai sesuai angka
    '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11  # 10, J, Q, K = 10 poin; As = 11 poin
}


def create_deck():
    """
    Membuat 52 kartu unik lalu mengacak urutannya.
    """
    deck = []  # Inisialisasi list kosong untuk menyimpan kartu
    for suit in SUITS:  # Loop untuk setiap jenis kartu (Heart, Diamond, Club, Spade)
        for rank in RANKS:  # Loop setiap angka/rank (2 sampai A)
            deck.append({'rank': rank, 'suit': suit, 'value': VALUES[rank]})  # Tambahkan kartu sebagai dictionary dengan rank, suit, dan value
    random.shuffle(deck)  # Mengacak urutan deck secara random agar tidak teratur
    #print("Deck setelah shuffle:", [(card['rank'], card['suit']) for card in deck])
    return deck  # Kembalikan deck yang sudah diacak


def calculate_score(hand):
    """
    Menghitung total nilai dari 3 kartu di tangan.
    """
    return sum(card['value'] for card in hand)  # Jumlahkan semua nilai 'value' dari setiap kartu dalam hand


def format_hand(hand, hidden=False):
    """
    Mengubah kartu menjadi teks siap tampil.
    Jika hidden=True, semua kartu ditutup.
    """
    cards_str = []  # List untuk menyimpan string representasi setiap kartu
    for _idx, card in enumerate(hand):  # Loop melalui setiap kartu dalam hand
        if hidden:  # Jika kartu harus disembunyikan
            cards_str.append("[ TERTUTUP ]")  # Tampilkan sebagai tertutup
        else:  # Jika kartu boleh ditampilkan
            cards_str.append(f"[{card['rank']} {card['suit']}]")  # Tampilkan rank dan suit kartu

    total = "???" if hidden else str(calculate_score(hand))  # Total skor: "???" jika hidden, atau nilai sebenarnya jika tidak
    return " ".join(cards_str) + f"\nTotal: {total}"  # Gabungkan semua kartu dengan spasi, tambahkan total di baris baru


class GameApp:
    """
    Kelas utama yang memegang seluruh state permainan dan UI Tkinter.
    """

    def __init__(self):
        self.root = tk.Tk()  # Membuat window utama Tkinter
        self.root.title("Games 33")  # Set judul window
        self.root.geometry("780x640")  # Set ukuran window (lebar x tinggi)
        self.root.configure(bg="#ffffff")  # Set warna background menjadi putih
        self.root.resizable(False, False)  # Nonaktifkan resize agar ukuran tetap

        # Variabel state permainan
        self.deck = []  # List untuk menyimpan deck kartu
        self.player_hand = []  # List untuk menyimpan 3 kartu pemain
        self.computer_hand = []  # List untuk menyimpan 3 kartu komputer
        self.temp_hand = []  # List sementara untuk menyimpan 4 kartu saat pemain memilih kartu yang dibuang
        self.current_round = 1  # Penghitung ronde saat ini (mulai dari 1)
        self.max_rounds = 10  # Batas maksimal ronde permainan
        self.game_over = False  # Flag untuk menandai apakah permainan sudah berakhir
        self.hide_computer = True  # Flag untuk menyembunyikan/menampilkan kartu komputer

        # Container utama untuk semua layout
        self.container = tk.Frame(self.root, bg="#ffffff", padx=32, pady=32)  # Frame utama dengan padding
        self.container.pack(fill="both", expand=True)  # Pack frame agar mengisi seluruh window

        self.build_start_screen()  # Tampilkan layar awal segera saat aplikasi dimulai

    # ---------- UTILITAS UI ----------
    def clear_container(self):
        """
        Menghapus semua widget di container utama
        agar bisa diganti tampilan lain.
        """
        for widget in self.container.winfo_children():  # Loop melalui semua widget anak di container
            widget.destroy()  # Hapus widget dari memori

    def build_start_screen(self):
        """
        Menyusun tampilan awal dengan judul, deskripsi, dan tombol start.
        """
        self.clear_container()  # Hapus semua widget yang ada sebelumnya

        tk.Label(  # Membuat label untuk judul
            self.container,  # Parent widget
            text="Selamat Datang di Games 33",  # Teks yang ditampilkan
            font=("Segoe UI", 22, "bold"),  # Font, ukuran, dan style
            fg="#111827",  # Warna teks (abu-abu gelap)
            bg="#ffffff"  # Warna background (putih)
        ).pack(pady=(40, 12))  # Pack dengan padding vertikal atas 40, bawah 12

        tk.Label(  # Membuat label untuk deskripsi
            self.container,  # Parent widget
            text="Capai total nilai kartu 33 tanpa melewati batas.\nTekan start untuk memulai.",  # Teks deskripsi dengan newline
            font=("Segoe UI", 13),  # Font dan ukuran
            fg="#374151",  # Warna teks (abu-abu sedang)
            bg="#ffffff",  # Warna background
            justify="center"  # Rata tengah teks
        ).pack(pady=(0, 30))  # Pack dengan padding bawah 30

        tk.Button(  # Membuat tombol start
            self.container,  # Parent widget
            text="Start Game",  # Teks pada tombol
            font=("Segoe UI", 14, "bold"),  # Font, ukuran, dan style
            bg="#d1fae5",  # Warna background tombol (hijau muda)
            fg="#065f46",  # Warna teks (hijau gelap)
            activebackground="#a7f3d0",  # Warna saat tombol diklik
            activeforeground="#065f46",  # Warna teks saat diklik
            relief="ridge",  # Style border tombol
            padx=28,  # Padding horizontal
            pady=8,  # Padding vertikal
            command=self.start_game  # Fungsi yang dipanggil saat tombol diklik
        ).pack()  # Pack tombol ke container

    # ---------- ALUR START GAME ----------
    def start_game(self):
        """
        Reset deck, bagi kartu, mulai ronde baru.
        """
        self.deck = create_deck()  # Buat deck baru yang sudah diacak
        self.player_hand = [self.deck.pop() for _ in range(3)]  # Ambil 3 kartu dari deck untuk pemain (pop menghapus dari deck)
        self.computer_hand = [self.deck.pop() for _ in range(3)]  # Ambil 3 kartu dari deck untuk komputer
        self.current_round = 1  # Reset ronde ke 1
        self.game_over = False  # Reset flag game_over menjadi False
        self.hide_computer = True  # Sembunyikan kartu komputer

        self.show_game_screen()  # Tampilkan layout permainan
        self.start_round()  # Mulai ronde pertama

    def show_game_screen(self):
        """
        Layout utama setelah game dimulai:
        - Label ronde
        - Panel kartu komputer & pemain
        - Pesan status + area tombol tindakan
        """
        self.clear_container()  # Hapus semua widget sebelumnya

        self.round_label = tk.Label(  # Label untuk menampilkan ronde saat ini
            self.container,  # Parent widget
            text="Ronde 1 / 10",  # Teks awal
            font=("Segoe UI", 16, "bold"),  # Font dan ukuran
            fg="#111827",  # Warna teks
            bg="#ffffff"  # Warna background
        )
        self.round_label.pack(anchor="w")  # Pack dengan anchor kiri (west)

        hands_frame = tk.Frame(self.container, bg="#ffffff")  # Frame untuk menampung panel kartu
        hands_frame.pack(fill="x", pady=(16, 8))  # Pack dengan fill horizontal, padding vertikal

        # Panel komputer
        comp_frame = tk.Frame(hands_frame, bg="#f3f4f6", padx=12, pady=12, relief="groove", borderwidth=1)  # Frame untuk kartu komputer dengan border
        comp_frame.pack(side="left", expand=True, fill="both", padx=(0, 8))  # Pack di sisi kiri, expand dan fill, padding kanan 8
        tk.Label(comp_frame, text="Kartu Komputer", font=("Segoe UI", 13, "bold"), fg="#111827", bg="#f3f4f6").pack(anchor="w")  # Label judul panel komputer
        self.computer_cards_var = tk.StringVar()  # Variabel untuk menyimpan teks kartu komputer (bisa diupdate)
        tk.Label(comp_frame, textvariable=self.computer_cards_var, font=("Consolas", 11), fg="#111827", bg="#f3f4f6", justify="left").pack(anchor="w", pady=(8, 0))  # Label yang menampilkan kartu komputer

        # Panel pemain
        player_frame = tk.Frame(hands_frame, bg="#f3f4f6", padx=12, pady=12, relief="groove", borderwidth=1)  # Frame untuk kartu pemain dengan border
        player_frame.pack(side="left", expand=True, fill="both", padx=(8, 0))  # Pack di sisi kiri, expand dan fill, padding kiri 8
        tk.Label(player_frame, text="Kartu Anda", font=("Segoe UI", 13, "bold"), fg="#111827", bg="#f3f4f6").pack(anchor="w")  # Label judul panel pemain
        self.player_cards_var = tk.StringVar()  # Variabel untuk menyimpan teks kartu pemain (bisa diupdate)
        tk.Label(player_frame, textvariable=self.player_cards_var, font=("Consolas", 11), fg="#111827", bg="#f3f4f6", justify="left").pack(anchor="w", pady=(8, 0))  # Label yang menampilkan kartu pemain

        # Pesan dan kontrol
        self.message_var = tk.StringVar(value="Permainan dimulai.")  # Variabel untuk menyimpan pesan status
        tk.Label(  # Label untuk menampilkan pesan
            self.container,  # Parent widget
            textvariable=self.message_var,  # Menggunakan StringVar agar bisa diupdate
            font=("Segoe UI", 12),  # Font dan ukuran
            fg="#374151",  # Warna teks
            bg="#ffffff",  # Warna background
            justify="left",  # Rata kiri
            wraplength=700  # Panjang maksimal sebelum wrap teks
        ).pack(anchor="w", pady=(16, 8))  # Pack dengan anchor kiri, padding vertikal

        self.control_frame = tk.Frame(self.container, bg="#ffffff")  # Frame untuk menampung tombol-tombol kontrol
        self.control_frame.pack(fill="x")  # Pack dengan fill horizontal

    # ---------- UTIL UPDATE ----------
    def set_message(self, text):
        """Memperbarui teks status."""
        self.message_var.set(text)  # Update teks pesan status dengan teks baru

    def clear_controls(self):
        """Menghapus tombol/controls yang aktif."""
        for widget in self.control_frame.winfo_children():  # Loop melalui semua widget anak di control_frame
            widget.destroy()  # Hapus widget dari memori

    def update_board(self):
        """Refresh tampilan kartu + teks ronde."""
        self.round_label.config(text=f"Ronde {self.current_round} / {self.max_rounds}")  # Update label ronde dengan ronde saat ini
        self.computer_cards_var.set(format_hand(self.computer_hand, hidden=self.hide_computer))  # Update kartu komputer (tersembunyi atau tidak tergantung flag)
        self.player_cards_var.set(format_hand(self.player_hand, hidden=False))  # Update kartu pemain (selalu terlihat)

    # ---------- SIKLUS RONDE ----------
    def start_round(self):
        """Inisiasi ronde baru untuk pemain."""
        if self.game_over:  # Cek apakah permainan sudah berakhir
            return  # Keluar jika sudah berakhir

        self.hide_computer = True  # Sembunyikan kartu komputer selama permainan
        self.update_board()  # Update tampilan papan permainan

        player_score = calculate_score(self.player_hand)  # Hitung skor pemain saat ini
        if player_score == 33:  # Jika pemain langsung mendapat 33
            self.finish_game("ANDA MENDAPATKAN 33! ANDA MENANG!")  # Pemain menang langsung
            return  # Keluar dari fungsi

        self.new_card = self.deck.pop()  # Ambil 1 kartu baru dari deck (pop menghapus dari deck)
        self.temp_hand = self.player_hand + [self.new_card]  # Gabungkan 3 kartu lama dengan 1 kartu baru = 4 kartu sementara
        self.set_message(  # Update pesan status
            f"Anda mengambil kartu: [{self.new_card['rank']} {self.new_card['suit']}].\n"  # Tampilkan kartu yang diambil
            "Pilih satu kartu untuk dibuang agar tetap memiliki 3 kartu."  # Instruksi untuk pemain
        )
        self.render_discard_buttons()  # Tampilkan tombol-tombol untuk memilih kartu yang dibuang

    def render_discard_buttons(self):
        """Menampilkan tombol pilihan kartu mana yang dibuang."""
        self.clear_controls()  # Hapus tombol-tombol sebelumnya
        tk.Label(  # Label instruksi
            self.control_frame,  # Parent widget
            text="Pilih kartu yang ingin dibuang:",  # Teks instruksi
            font=("Segoe UI", 10, "bold"),  # Font dan ukuran
            fg="#111827",  # Warna teks
            bg="#ffffff"  # Warna background
        ).pack(anchor="w", pady=(0, 8))  # Pack dengan anchor kiri, padding bawah 8

        for idx, card in enumerate(self.temp_hand):  # Loop melalui setiap kartu dalam temp_hand (4 kartu)
            tk.Button(  # Membuat tombol untuk setiap kartu
                self.control_frame,  # Parent widget
                text=f"Buang {card['rank']} {card['suit']} (Nilai {card['value']})",  # Teks tombol menampilkan rank, suit, dan nilai kartu
                font=("Segoe UI", 10),  # Font dan ukuran
                bg="#e5e7eb",  # Warna background (abu-abu muda)
                fg="#111827",  # Warna teks
                activebackground="#d1d5db",  # Warna saat diklik
                activeforeground="#111827",  # Warna teks saat diklik
                relief="ridge",  # Style border
                padx=10,  # Padding horizontal
                pady=4,  # Padding vertikal
                command=lambda i=idx: self.handle_discard(i)  # Fungsi yang dipanggil saat diklik, kirim index kartu
            ).pack(fill="x", pady=4)  # Pack dengan fill horizontal, padding vertikal 4

    def handle_discard(self, index):
        """Dijalankan saat pemain memilih kartu untuk dibuang."""
        if self.game_over:  # Cek apakah permainan sudah berakhir
            return  # Keluar jika sudah berakhir

        removed = self.temp_hand.pop(index)  # Hapus kartu di posisi index dari temp_hand, simpan ke removed
        self.player_hand = self.temp_hand  # Update player_hand dengan 3 kartu yang tersisa setelah membuang
        self.update_board()  # Update tampilan papan permainan
        self.set_message(f"Anda membuang [{removed['rank']} {removed['suit']}]. Menunggu giliran komputer...")  # Update pesan status
        self.clear_controls()  # Hapus tombol-tombol pilihan kartu

        if calculate_score(self.player_hand) > 33:  # Cek apakah skor pemain melebihi 33 (BUST)
            self.finish_game("Total nilai Anda melebihi 33 (BUST)! Anda Kalah.")  # Pemain kalah karena bust
            return  # Keluar dari fungsi

        self.root.after(600, self.computer_turn)  # Delay 600ms sebelum giliran komputer (biar terasa natural)

    def computer_turn(self):
        """Logika AI sederhana untuk memilih kartu terbaik."""
        if self.game_over:  # Cek apakah permainan sudah berakhir, jika ya keluar dari fungsi
            return  # Keluar dari fungsi jika game sudah selesai

        c_new_card = self.deck.pop()  # Ambil 1 kartu baru dari tumpukan deck (kartu teratas)
        c_temp_hand = self.computer_hand + [c_new_card]  # Gabungkan 3 kartu lama dengan 1 kartu baru = 4 kartu sementara

        best_hand = None  # Variabel untuk menyimpan kombinasi kartu terbaik yang ditemukan
        best_score = -1  # Variabel untuk menyimpan skor tertinggi yang valid (<=33), mulai dari -1
        
        # FASE 1: Mencari kombinasi terbaik (skor tertinggi yang <= 33)
        for i in range(4):  # Loop untuk mencoba membuang setiap kartu dari 4 kartu (indeks 0,1,2,3)
            test_hand = c_temp_hand[:]  # Salin semua 4 kartu ke variabel test (copy list agar tidak mengubah aslinya)
            test_hand.pop(i)  # Buang kartu di posisi i, sekarang test_hand berisi 3 kartu
            score = calculate_score(test_hand)  # Hitung total nilai dari 3 kartu yang tersisa
            if score <= 33 and score > best_score:  # Jika skor <= 33 (valid) DAN lebih besar dari best_score sebelumnya
                best_score = score  # Update best_score dengan skor yang lebih baik ini
                best_hand = test_hand  # Simpan kombinasi kartu ini sebagai pilihan terbaik

        # FASE 2: Fallback jika semua kombinasi melebihi 33 (BUST)
        if best_hand is None:  # Jika tidak ada kombinasi yang <= 33 (semua kombinasi > 33)
            min_score = 999  # Inisialisasi dengan nilai besar untuk mencari skor terkecil
            for i in range(4):  # Loop lagi untuk mencoba semua 4 kemungkinan membuang kartu
                test_hand = c_temp_hand[:]  # Salin lagi 4 kartu untuk diuji
                test_hand.pop(i)  # Buang kartu di posisi i
                score = calculate_score(test_hand)  # Hitung skor dari 3 kartu yang tersisa
                if score < min_score:  # Jika skor ini lebih kecil dari min_score yang pernah ditemukan
                    min_score = score  # Update min_score dengan skor yang lebih kecil
                    best_hand = test_hand  # Simpan kombinasi ini (meskipun tetap > 33, ini yang paling kecil)

        self.computer_hand = best_hand  # Terapkan kombinasi terbaik yang ditemukan ke tangan komputer
        self.update_board()  # Update tampilan UI untuk menampilkan kartu komputer yang baru
        self.set_message("Komputer telah memilih kartu terbaiknya.")  # Tampilkan pesan ke user

        if calculate_score(self.computer_hand) > 33:  # Cek apakah setelah memilih, komputer tetap melebihi 33
            self.finish_game("Komputer melebihi 33 (BUST)! Anda Menang.")  # Jika ya, komputer kalah, pemain menang
            return  # Keluar dari fungsi karena game sudah berakhir

        self.post_round_prompt()  # Jika komputer tidak bust, lanjutkan ke prompt untuk ronde berikutnya

    def post_round_prompt(self):
        """
        Dipanggil setelah kedua pihak selesai.
        Hanya memberikan tombol lanjut ronde sampai ronde ke-10.
        """
        if self.game_over:  # Cek apakah permainan sudah berakhir
            return  # Keluar jika sudah berakhir

        if self.current_round < self.max_rounds:  # Jika belum mencapai ronde maksimal (10)
            self.set_message("Ronde selesai. Tekan 'Lanjut Ronde' untuk melanjutkan permainan.")  # Update pesan status
            self.clear_controls()  # Hapus tombol-tombol sebelumnya

            tk.Button(  # Membuat tombol lanjut ronde
                self.control_frame,  # Parent widget
                text="Lanjut Ronde",  # Teks tombol
                font=("Segoe UI", 10, "bold"),  # Font dan ukuran
                bg="#dbeafe",  # Warna background (biru muda)
                fg="#1e3a8a",  # Warna teks (biru gelap)
                activebackground="#bfdbfe",  # Warna saat diklik
                relief="ridge",  # Style border
                padx=16,  # Padding horizontal
                pady=6,  # Padding vertikal
                command=self.next_round  # Fungsi yang dipanggil saat diklik
            ).pack(side="left")  # Pack di sisi kiri
        else:  # Jika sudah mencapai ronde maksimal
            self.finish_game("Batas ronde tercapai! Saatnya penentuan.")  # Akhiri permainan

    def next_round(self):
        """Menambah penghitung ronde dan memulai ronde berikutnya."""
        if self.game_over:  # Cek apakah permainan sudah berakhir
            return  # Keluar jika sudah berakhir
        self.current_round += 1  # Tambah penghitung ronde
        self.start_round()  # Mulai ronde berikutnya

    # ---------- TAMAT ----------
    def finish_game(self, reason=None):
        """Menutup permainan dan menampilkan ringkasan hasil."""
        if self.game_over:  # Cek apakah permainan sudah berakhir
            return  # Keluar jika sudah berakhir
        self.game_over = True  # Set flag game_over menjadi True
        self.hide_computer = False  # Buka kartu komputer agar terlihat
        self.update_board()  # Update tampilan papan permainan
        self.clear_controls()  # Hapus tombol-tombol sebelumnya

        summary = self.build_final_summary(reason)  # Buat ringkasan hasil akhir
        self.set_message(summary)  # Tampilkan ringkasan di pesan status

        tk.Button(  # Membuat tombol main lagi
            self.control_frame,  # Parent widget
            text="Main Lagi",  # Teks tombol
            font=("Segoe UI", 10, "bold"),  # Font dan ukuran
            bg="#d1fae5",  # Warna background (hijau muda)
            fg="#065f46",  # Warna teks (hijau gelap)
            activebackground="#a7f3d0",  # Warna saat diklik
            relief="ridge",  # Style border
            padx=16,  # Padding horizontal
            pady=6,  # Padding vertikal
            command=self.build_start_screen  # Fungsi yang dipanggil saat diklik (kembali ke layar awal)
        ).pack(side="left")  # Pack di sisi kiri

    def build_final_summary(self, reason=None):
        """Menyusun string hasil akhir (skor, pemenang, alasan)."""
        p_final = calculate_score(self.player_hand)  # Hitung skor akhir pemain
        c_final = calculate_score(self.computer_hand)  # Hitung skor akhir komputer

        lines = []  # List untuk menyimpan baris-baris teks ringkasan
        if reason:  # Jika ada alasan khusus (seperti bust atau menang langsung)
            lines.append(reason)  # Tambahkan alasan ke list
        lines.append(f"Skor Anda: {p_final}")  # Tambahkan skor pemain
        lines.append(f"Skor Komputer: {c_final}")  # Tambahkan skor komputer

        if p_final > 33 and c_final <= 33:  # Jika pemain bust dan komputer tidak
            lines.append("Anda Bust! Komputer Menang.")  # Komputer menang
        elif c_final > 33 and p_final <= 33:  # Jika komputer bust dan pemain tidak
            lines.append("Komputer Bust! Anda Menang.")  # Pemain menang
        elif p_final > 33 and c_final > 33:  # Jika keduanya bust
            lines.append("Keduanya melebihi 33, tetapi tidak ada pemenang jelas.")  # Tidak ada pemenang jelas
        else:  # Jika keduanya tidak bust (<= 33)
            if p_final > c_final:  # Jika skor pemain lebih besar dari komputer
                lines.append("SELAMAT! Anda Menang (lebih dekat ke 33).")  # Pemain menang
            elif c_final > p_final:  # Jika skor komputer lebih besar dari pemain
                lines.append("Komputer Menang (lebih dekat ke 33).")  # Komputer menang
            else:  # Jika skor sama
                lines.append("SERI! Skor sama-sama dekat ke 33.")  # Seri

        return "\n".join(lines)  # Gabungkan semua baris dengan newline menjadi satu string

    def run(self):
        """Menjalankan event-loop Tkinter."""
        self.root.mainloop()  # Mulai event loop Tkinter untuk menampilkan UI dan menangani event


if __name__ == "__main__":  # Cek apakah file ini dijalankan langsung (bukan diimport)
    GameApp().run()  # Buat instance GameApp dan jalankan aplikasi
