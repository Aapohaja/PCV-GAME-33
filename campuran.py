import cv2
import numpy as np
import os
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk 

# --- KONFIGURASI KARTU & ATURAN ---
SUITS_STR = ['Heart', 'Diamond', 'Club', 'Spade']
RANKS_STR = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 
    '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

# --- FUNGSI COMPUTER VISION ---

def titik(pts):
    rect = np.zeros((4,2), dtype = "float32")
    s = pts.sum(axis = 1)
    diff = np.diff(pts, axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def klasifikasi_kartu(kartu_warped, all_templates):
    gray_warped = cv2.cvtColor(kartu_warped, cv2.COLOR_BGR2GRAY)
    _, threshold_warped = cv2.threshold(gray_warped, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    best_match = ("unknow", float('inf'))
    
    for nama_kartu, gambar in all_templates.items():
        if threshold_warped.shape != gambar.shape:
            gambar = cv2.resize(gambar, (threshold_warped.shape[1], threshold_warped.shape[0]))
        
        img1 = threshold_warped.astype(np.float32)
        img2 = gambar.astype(np.float32)
        diff = np.abs(img1 - img2)
        sad_value = np.sum(diff)
        
        if sad_value < best_match[1]:
            best_match = (nama_kartu, sad_value)
    
    kartu_terklasifikasi = best_match[0]
    sad_value = best_match[1]
    
    max_possible_sad = threshold_warped.shape[0] * threshold_warped.shape[1] * 255.0
    confidence = 1.0 - (sad_value / max_possible_sad)
    confidence = max(0.0, min(1.0, confidence))
    
    if confidence < 0.6:
        kartu_terklasifikasi = "tidak tau"
    
    return kartu_terklasifikasi, confidence

# --- LOGIKA GAME UTAMA ---

class GameApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Game 33 - Mixed Reality (Embedded Camera)")
        self.root.geometry("1000x800") # Diperbesar sedikit untuk video
        self.root.configure(bg="#ffffff")
        self.root.resizable(False, False)

        # Inisialisasi variabel game
        self.deck = [] # Deck virtual (Master Deck)
        self.player_hand = []
        self.computer_hand = []
        self.temp_hand = []
        self.current_round = 1
        self.max_rounds = 10
        self.game_over = False
        self.hide_computer = True
        
        # Variabel Kamera & CV
        self.cap = None
        self.scanning_active = False
        self.current_valid_card = None # Menyimpan kartu valid yang sedang dilihat kamera
        self.scanned_cards_temp = []
        self.target_scan_count = 0
        
        # Inisialisasi CV Template
        self.templates = {}
        self.cam_width = 300
        self.cam_height = 420
        self.init_cv_templates()
        
        # Container GUI
        self.container = tk.Frame(self.root, bg="#ffffff", padx=20, pady=20)
        self.container.pack(fill="both", expand=True)

        self.build_start_screen()

    def init_cv_templates(self):
        # PASTIKAN PATH INI BENAR SESUAI KOMPUTER ANDA
        self.folder_path = r"C:\Users\aaron\Downloads\individual_cards_2"
        
        ranks = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
        suits = ["Spade","Heart","Diamond","Club"]
        
        print("Memuat template kartu...")
        if not os.path.exists(self.folder_path):
            messagebox.showerror("Error", f"Folder tidak ditemukan:\n{self.folder_path}")
            return

        for suit in suits:
            for rank in ranks:
                nama_kartu = f"{rank} {suit}"
                namafile = f"{rank}_{suit}.jpg"
                path = os.path.join(self.folder_path, namafile)
                template = cv2.imread(path)
                
                if template is not None:
                    Resized = cv2.resize(template, (self.cam_width, self.cam_height))
                    template_gray = cv2.cvtColor(Resized, cv2.COLOR_BGR2GRAY)
                    _, template_thresh = cv2.threshold(template_gray, 150, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
                    self.templates[nama_kartu] = template_thresh
        
        print(f"Total template dimuat: {len(self.templates)}")

    def create_deck(self):
        deck = []
        for suit in SUITS_STR:
            for rank in RANKS_STR:
                deck.append({'rank': rank, 'suit': suit, 'value': VALUES[rank]})
        random.shuffle(deck)
        return deck

    def is_card_available(self, rank, suit):
        for card in self.deck:
            if card['rank'] == rank and card['suit'] == suit:
                return True
        return False

    def remove_card_from_deck(self, rank, suit):
        self.deck = [c for c in self.deck if not (c['rank'] == rank and c['suit'] == suit)]

    def calculate_score(self, hand):
        return sum(card['value'] for card in hand)

    def format_hand(self, hand, hidden=False):
        cards_str = []
        for i, card in enumerate(hand):
            if hidden:
                cards_str.append("[ TERTUTUP ]")
            else:
                cards_str.append(f"[{card['rank']} {card['suit']}]")
        if hidden:
            total = "???"
        else:
            total = str(self.calculate_score(hand))
        return " ".join(cards_str) + f"\nTotal: {total}"

    # --- GUI & NAVIGASI ---

    def clear_container(self):
        # Unbind spacebar jika berpindah layar agar tidak error
        self.root.unbind('<space>')
        for widget in self.container.winfo_children():
            widget.destroy()

    def build_start_screen(self):
        self.clear_container()
        tk.Label(self.container, text="Game 33: Mode Kamera (Embedded)", font=("Segoe UI", 22, "bold"), bg="#ffffff").pack(pady=(40, 12))
        tk.Label(self.container, text="Siapkan kartu fisik Anda.\nAnda akan bermain melawan komputer.\nTekan Start untuk memindai kartu awal.", font=("Segoe UI", 13), bg="#ffffff").pack(pady=(0, 30))
        
        tk.Button(self.container, text="Start Game & Scan Awal", font=("Segoe UI", 14, "bold"), bg="#d1fae5", 
                  command=self.start_game_sequence).pack()

    def start_game_sequence(self):
        self.deck = self.create_deck()
        self.player_hand = []
        self.computer_hand = [self.deck.pop() for _ in range(3)] 
        
        self.current_round = 1
        self.game_over = False
        self.hide_computer = True

        self.start_camera_scan(count=3)

    # --- KAMERA TERINTEGRASI (EMBEDDED) ---

    def start_camera_scan(self, count):
        self.clear_container()
        self.target_scan_count = count
        self.scanned_cards_temp = []
        self.current_valid_card = None
        self.scanning_active = True

        # Header UI
        msg = "Pindai 3 Kartu Awal" if count == 3 else "Pindai 1 Kartu Baru"
        tk.Label(self.container, text=msg, font=("Segoe UI", 18, "bold"), bg="white").pack(pady=(0, 10))

        # Video Frame Holder
        self.video_label = tk.Label(self.container, bg="black")
        self.video_label.pack()

        # Status & Instruksi
        self.status_label = tk.Label(self.container, text="Sedang menyiapkan kamera...", font=("Segoe UI", 12, "bold"), bg="white", fg="#555")
        self.status_label.pack(pady=10)
        
        self.progress_label = tk.Label(self.container, text=f"Terkumpul: 0 / {count}", font=("Segoe UI", 11), bg="white")
        self.progress_label.pack()

        # Tombol Capture
        self.capture_btn = tk.Button(
            self.container, 
            text="AMBIL KARTU (Space)", 
            font=("Segoe UI", 12, "bold"), 
            bg="#ccc", 
            fg="white",
            state="disabled",
            command=self.capture_current_card
        )
        self.capture_btn.pack(pady=10)

        # Bind Tombol Spasi untuk Capture
        self.root.bind('<space>', lambda event: self.capture_current_card())

        # Mulai Stream Kamera
        self.cap = cv2.VideoCapture(0) # Ganti index kamera jika perlu
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Kamera tidak terdeteksi")
            self.return_to_game()
            return
        
        self.process_video_frame()

    def process_video_frame(self):
        if not self.scanning_active:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.root.after(10, self.process_video_frame)
            return

        # -- LOGIKA DETEKSI --
        img_output = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        edges = cv2.Canny(blur, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        area_min = (frame.shape[0] * frame.shape[1]) / 150
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        detected_text = "Arahkan kartu..."
        status_color = (0, 0, 255) # Merah (default)
        self.current_valid_card = None # Reset setiap frame
        btn_state = "disabled"
        btn_bg = "#ccc"

        for c in contours:
            if cv2.contourArea(c) < area_min: continue
            
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            
            if len(approx) == 4:
                # Gambar kontur
                cv2.drawContours(img_output, [approx], -1, (0, 255, 0), 2)
                
                # Warp & Klasifikasi
                src_pts = titik(approx.reshape(4,2))
                dst_pts = np.array([[0, 0], [self.cam_width-1, 0], [self.cam_width-1, self.cam_height-1], [0, self.cam_height-1]], dtype="float32")
                m = cv2.getPerspectiveTransform(src_pts, dst_pts)
                warped = cv2.warpPerspective(frame, m, (self.cam_width, self.cam_height))
                
                name, conf = klasifikasi_kartu(warped, self.templates)
                
                if conf > 0.65:
                    parts = name.split()
                    if len(parts) == 2:
                        rank_det, suit_det = parts[0], parts[1]
                        
                        # Validasi Duplikasi
                        already_scanned = any(c['rank'] == rank_det and c['suit'] == suit_det for c in self.scanned_cards_temp)
                        available_in_deck = self.is_card_available(rank_det, suit_det)

                        if already_scanned:
                            detected_text = f"{name} (SUDAH DIAMBIL)"
                            status_color = (0, 165, 255) # Orange
                        elif available_in_deck:
                            detected_text = f"SIAP: {name}"
                            status_color = (0, 255, 0) # Hijau
                            self.current_valid_card = {'rank': rank_det, 'suit': suit_det, 'value': VALUES.get(rank_det, 0)}
                            btn_state = "normal"
                            btn_bg = "#3b82f6" # Biru aktif
                        else:
                            detected_text = f"{name} (MILIK LAWAN/HABIS)"
                            status_color = (0, 0, 255) # Merah
                    
                    # Tulis teks di atas kartu
                    cv2.putText(img_output, detected_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
                break

        # -- UPDATE UI TKINTER --
        
        # 1. Update Video Frame
        # Convert BGR (OpenCV) ke RGB (Tkinter/PIL)
        img_rgb = cv2.cvtColor(img_output, cv2.COLOR_BGR2RGB)
        # Resize sedikit agar pas di GUI jika perlu (opsional)
        img_pil = Image.fromarray(img_rgb)
        imgtk = ImageTk.PhotoImage(image=img_pil)
        
        self.video_label.imgtk = imgtk # Keep reference agar tidak garbage collected
        self.video_label.configure(image=imgtk)

        # 2. Update Label & Button
        self.status_label.config(text=detected_text, fg=("green" if self.current_valid_card else "red"))
        self.capture_btn.config(state=btn_state, bg=btn_bg)

        # Loop lagi
        if self.scanning_active:
            self.root.after(20, self.process_video_frame)

    def capture_current_card(self):
        if self.current_valid_card and self.scanning_active:
            card = self.current_valid_card
            
            # Hapus dari deck master
            self.remove_card_from_deck(card['rank'], card['suit'])
            
            # Simpan
            self.scanned_cards_temp.append(card)
            
            # Update Progress
            current_count = len(self.scanned_cards_temp)
            self.progress_label.config(text=f"Terkumpul: {current_count} / {self.target_scan_count}")
            
            # Reset sementara agar tidak double click cepat
            self.current_valid_card = None 
            self.capture_btn.config(state="disabled", bg="#ccc")
            
            # Cek apakah sudah selesai
            if current_count >= self.target_scan_count:
                self.scanning_active = False
                self.stop_camera_and_proceed()

    def stop_camera_and_proceed(self):
        if self.cap:
            self.cap.release()
        
        if self.target_scan_count == 3:
            self.player_hand = self.scanned_cards_temp
            self.show_game_screen()
            self.start_round()
        else:
            # Draw 1 kartu
            self.handle_scanned_draw(self.scanned_cards_temp[0])

    # --- LOGIKA GAME BIASA ---

    def show_game_screen(self):
        self.clear_container()
        
        self.round_label = tk.Label(self.container, text=f"Ronde {self.current_round} / {self.max_rounds}", font=("Segoe UI", 16, "bold"), bg="white")
        self.round_label.pack(anchor="w")

        hands_frame = tk.Frame(self.container, bg="white")
        hands_frame.pack(fill="x", pady=10)

        comp_frame = tk.Frame(hands_frame, bg="#f3f4f6", padx=10, pady=10, relief="groove", bd=1)
        comp_frame.pack(side="left", expand=True, fill="both", padx=5)
        tk.Label(comp_frame, text="Komputer", font=("bold"), bg="#f3f4f6").pack(anchor="w")
        self.computer_cards_var = tk.StringVar()
        tk.Label(comp_frame, textvariable=self.computer_cards_var, font=("Consolas", 10), bg="#f3f4f6", justify="left").pack(anchor="w")

        player_frame = tk.Frame(hands_frame, bg="#f3f4f6", padx=10, pady=10, relief="groove", bd=1)
        player_frame.pack(side="left", expand=True, fill="both", padx=5)
        tk.Label(player_frame, text="Anda (Kartu Fisik)", font=("bold"), bg="#f3f4f6").pack(anchor="w")
        self.player_cards_var = tk.StringVar()
        tk.Label(player_frame, textvariable=self.player_cards_var, font=("Consolas", 10), bg="#f3f4f6", justify="left").pack(anchor="w")

        self.message_var = tk.StringVar(value="Permainan dimulai.")
        self.message_label = tk.Label(self.container, textvariable=self.message_var, font=("Segoe UI", 12), bg="white", wraplength=700)
        self.message_label.pack(anchor="w", pady=10)

        self.control_frame = tk.Frame(self.container, bg="white")
        self.control_frame.pack(fill="x")
        
        self.update_board()

    def update_board(self):
        self.round_label.config(text=f"Ronde {self.current_round} / {self.max_rounds}")
        self.computer_cards_var.set(self.format_hand(self.computer_hand, hidden=self.hide_computer))
        self.player_cards_var.set(self.format_hand(self.player_hand, hidden=False))

    def set_message(self, text):
        self.message_var.set(text)

    def clear_controls(self):
        for widget in self.control_frame.winfo_children():
            widget.destroy()

    def start_round(self):
        if self.game_over: return
        self.hide_computer = True
        self.update_board()

        player_score = self.calculate_score(self.player_hand)
        if player_score == 33:
            self.finish_game("ANDA MENDAPATKAN 33! ANDA MENANG!")
            return

        self.clear_controls()
        self.set_message("Giliran Anda: Silakan ambil kartu dari tumpukan fisik dan pindai.")
        
        btn = tk.Button(self.control_frame, text="SCAN KARTU BARU", bg="#3b82f6", fg="white", 
                        font=("Segoe UI", 12, "bold"), padx=20, pady=10,
                        command=lambda: self.start_camera_scan(count=1))
        btn.pack()

    def handle_scanned_draw(self, new_card):
        self.temp_hand = self.player_hand + [new_card]
        self.set_message(f"Terdeteksi: [{new_card['rank']} {new_card['suit']}].\nPilih kartu untuk dibuang.")
        self.render_discard_buttons()

    def render_discard_buttons(self):
        self.clear_controls()
        tk.Label(self.control_frame, text="Pilih kartu untuk dibuang (klik tombol):", bg="white").pack(anchor="w")

        for idx, card in enumerate(self.temp_hand):
            txt = f"Buang {card['rank']} {card['suit']} (Nilai {card['value']})"
            tk.Button(self.control_frame, text=txt, bg="#e5e7eb", anchor="w",
                      command=lambda i=idx: self.handle_discard(i)).pack(fill="x", pady=2)

    def handle_discard(self, index):
        removed = self.temp_hand.pop(index)
        self.player_hand = self.temp_hand
        self.update_board()
        self.set_message(f"Anda membuang [{removed['rank']} {removed['suit']}]. Giliran Komputer...")
        self.clear_controls()

        if self.calculate_score(self.player_hand) > 33:
            self.finish_game("Total nilai Anda melebihi 33 (BUST)! Anda Kalah.")
            return

        self.root.after(800, self.computer_turn)

    def computer_turn(self):
        if self.game_over: return
        
        if not self.deck: 
             self.finish_game("Deck Habis! Permainan berakhir Seri.")
             return

        c_new_card = self.deck.pop()
        c_temp = self.computer_hand + [c_new_card]

        best_hand = None
        valid_moves = []
        for i in range(4):
            test = c_temp[:]
            test.pop(i)
            sc = self.calculate_score(test)
            if sc <= 33: valid_moves.append((sc, test))
        
        if valid_moves:
            valid_moves.sort(key=lambda x: x[0], reverse=True)
            best_hand = valid_moves[0][1]
        else:
            min_score = 999
            for i in range(4):
                test = c_temp[:]
                test.pop(i)
                sc = self.calculate_score(test)
                if sc < min_score:
                    min_score = sc
                    best_hand = test

        self.computer_hand = best_hand
        self.update_board()
        
        if self.calculate_score(self.computer_hand) > 33:
            self.finish_game("Komputer BUST! Anda Menang.")
            return
            
        self.set_message("Komputer selesai bermain. Lanjut ronde berikutnya...")
        self.root.after(1500, self.next_round)

    def next_round(self):
        if self.current_round < self.max_rounds:
            self.current_round += 1
            self.start_round()
        else:
            self.finish_game("Ronde habis! Penentuan pemenang.")

    def finish_game(self, reason):
        self.game_over = True
        self.hide_computer = False
        self.update_board()
        self.clear_controls()
        
        p_score = self.calculate_score(self.player_hand)
        c_score = self.calculate_score(self.computer_hand)
        
        msg = f"{reason}\n\nSkor Anda: {p_score}\nSkor Komputer: {c_score}\n"
        
        if p_score <= 33 and c_score <= 33:
            if p_score > c_score: msg += "ANDA MENANG!"
            elif c_score > p_score: msg += "KOMPUTER MENANG!"
            else: msg += "SERI!"
        
        self.set_message(msg)
        tk.Button(self.control_frame, text="Main Lagi", bg="#d1fae5", font=("bold"), command=self.build_start_screen).pack(pady=10)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = GameApp()
    app.run()