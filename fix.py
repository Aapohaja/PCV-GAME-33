import cv2
import numpy as np
import os
import random
import itertools
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# --- KONFIGURASI PENTING ---
# Path folder gambar kartu (Relatif terhadap file ini)
PATH_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "individual_cards_2") 

SUITS = ['Heart', 'Diamond', 'Club', 'Spade']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, '10':10, 'J':10, 'Q':10, 'K':10, 'A':11}

REF_WIDTH = 200
REF_HEIGHT = 280

# --- FUNGSI COMPUTER VISION ---

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0], rect[2] = pts[np.argmin(s)], pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1], rect[3] = pts[np.argmin(diff)], pts[np.argmax(diff)]
    return rect

def get_bird_view(image, pts):
    rect = order_points(pts)
    dst = np.array([
        [0, 0],
        [REF_WIDTH - 1, 0],
        [REF_WIDTH - 1, REF_HEIGHT - 1],
        [0, REF_HEIGHT - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (REF_WIDTH, REF_HEIGHT))
    return warped

def identify_card(warped_img, templates):
    gray_input = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)
    
    best_conf = 0
    best_name = None

    # Cek 1: Orientasi Normal
    for name, templ_img in templates.items():
        res = cv2.matchTemplate(gray_input, templ_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        if max_val > best_conf:
            best_conf = max_val
            best_name = name

    # Cek 2: Orientasi Putar 180 (jika kartu terbalik)
    gray_rotated = cv2.rotate(gray_input, cv2.ROTATE_180)
    for name, templ_img in templates.items():
        res = cv2.matchTemplate(gray_rotated, templ_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        if max_val > best_conf:
            best_conf = max_val
            best_name = name
    
    if best_conf > 0.60:
        return best_name, best_conf
    else:
        return None, 0.0

# --- APLIKASI UTAMA ---

class RobustCardGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Game 33 - Batas 10 Ronde")
        self.root.geometry("1000x650") 
        
        self.deck = []
        self.player_hand = []
        self.computer_hand = []
        self.templates = {}
        self.game_state = "IDLE" 
        self.detected_buffer = None
        
        self.current_round = 0
        self.max_rounds = 10
        
        self.setup_ui()
        self.load_templates()
        
        # Kamera (Ganti 0 jadi 1 jika menggunakan kamera eksternal)
        self.cap = cv2.VideoCapture(0)
        self.process_camera()

    def setup_ui(self):
        self.left_frame = tk.Frame(self.root, width=600, bg="black")
        self.left_frame.pack(side="left", fill="both", expand=True)
        self.video_label = tk.Label(self.left_frame, bg="black")
        self.video_label.pack(expand=True)
        
        self.right_frame = tk.Frame(self.root, width=400, bg="#f5f5f5", padx=20, pady=20)
        self.right_frame.pack(side="right", fill="both")
        
        tk.Label(self.right_frame, text="GAME 33", font=("Arial", 24, "bold")).pack(pady=5)
        
        self.lbl_round = tk.Label(self.right_frame, text="Ronde: -", font=("Arial", 12, "bold"), fg="#673AB7")
        self.lbl_round.pack(pady=5)

        self.lbl_info = tk.Label(self.right_frame, text="Siapkan kartu di background gelap.", font=("Arial", 11), fg="#555", wraplength=350)
        self.lbl_info.pack(pady=10)
        
        self.lbl_p_score = tk.Label(self.right_frame, text="Anda: 0", font=("Consolas", 14), bg="#c8e6c9", width=30)
        self.lbl_p_score.pack(pady=5)
        
        self.lbl_c_score = tk.Label(self.right_frame, text="Komputer: 0", font=("Consolas", 14), bg="#ffccbc", width=30)
        self.lbl_c_score.pack(pady=5)
        
        self.btn_main = tk.Button(self.right_frame, text="MULAI GAME", bg="#2196F3", fg="white", font=("Arial", 14, "bold"), command=self.start_game)
        self.btn_main.pack(pady=20, fill="x")
        
        self.discard_frame = tk.Frame(self.right_frame)
        self.discard_frame.pack(fill="x", pady=10)
        
        self.root.bind('<space>', self.handle_spacebar)

    def load_templates(self):
        print(f"Mencari template di: {PATH_FOLDER}")
        if not os.path.exists(PATH_FOLDER):
            messagebox.showerror("Error", f"Folder tidak ditemukan:\n{PATH_FOLDER}\nPastikan path folder benar.")
            return

        for s in SUITS:
            for r in RANKS:
                path = os.path.join(PATH_FOLDER, f"{r}_{s}.jpg")
                img = cv2.imread(path)
                if img is None: continue
                
                resized = cv2.resize(img, (REF_WIDTH, REF_HEIGHT))
                gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
                self.templates[f"{r} {s}"] = gray
                
        print(f"Berhasil memuat {len(self.templates)} template.")

    def start_game(self):
        self.deck = [{'rank': r, 'suit': s, 'value': VALUES[r]} for s in SUITS for r in RANKS]
        random.shuffle(self.deck)
        
        self.player_hand = []
        self.computer_hand = [self.deck.pop() for _ in range(3)]
        
        self.current_round = 1
        self.lbl_round.config(text=f"Ronde: {self.current_round}/{self.max_rounds}")
        
        self.game_state = "SCANNING"
        self.update_display()
        self.lbl_info.config(text="PINDAI KARTU:\nArahkan kartu ke kamera hingga terdeteksi, lalu tekan [SPASI].", fg="blue")
        self.btn_main.config(state="disabled", text="GAME BERJALAN")

    def process_camera(self):
        ret, frame = self.cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            edged = cv2.Canny(blur, 30, 150)
            
            contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
            
            self.detected_buffer = None
            display_text = "Mencari..."
            box_color = (0, 0, 255) 
            screen_contour = None
            
            for c in contours:
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                if len(approx) == 4 and cv2.contourArea(c) > 5000:
                    screen_contour = approx
                    break
            
            if screen_contour is not None:
                warped = get_bird_view(frame, screen_contour.reshape(4, 2))
                
                # Preview kecil hasil warp (Debug Visual)
                preview = cv2.resize(warped, (100, 140))
                frame[0:140, 0:100] = cv2.cvtColor(preview, cv2.COLOR_GRAY2BGR) if len(preview.shape) == 2 else preview
                cv2.rectangle(frame, (0,0), (100, 140), (0,255,0), 2)

                name, conf = identify_card(warped, self.templates)
                cv2.drawContours(frame, [screen_contour], -1, (0, 255, 255), 2)
                
                if name:
                    display_text = f"{name} ({int(conf*100)}%)"
                    r, s = name.split()
                    is_owned = any(c['rank'] == r and c['suit'] == s for c in self.player_hand)
                    
                    if is_owned:
                        display_text = "SUDAH PUNYA"
                        box_color = (0, 165, 255)
                    elif self.game_state == "SCANNING":
                        box_color = (0, 255, 0)
                        display_text = f"SIAP: {name}"
                        self.detected_buffer = {'rank': r, 'suit': s, 'value': VALUES[r]}
            
            cv2.rectangle(frame, (0,0), (600, 60), (0,0,0), -1)
            cv2.putText(frame, display_text, (110, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, box_color, 2)
            
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(img_rgb))
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)
        
        self.root.after(20, self.process_camera)

    def handle_spacebar(self, event=None):
        if self.game_state == "SCANNING" and self.detected_buffer:
            new_card = self.detected_buffer
            self.player_hand.append(new_card)
            self.update_display()
            self.detected_buffer = None
            
            if len(self.player_hand) < 3:
                self.lbl_info.config(text=f"Kartu {len(self.player_hand)} tersimpan. Cari kartu berikutnya.")
            elif len(self.player_hand) == 3:
                if self.calc_score(self.player_hand) == 33:
                    self.game_over("MENANG MUTLAK (33)!")
                else:
                    self.start_draw_phase()
            elif len(self.player_hand) == 4:
                self.game_state = "DISCARDING"
                self.lbl_info.config(text=f"Dapat {new_card['rank']} {new_card['suit']}.\nPILIH KARTU UNTUK DIBUANG DI TANGAN ->", fg="red")
                self.show_discard_buttons()

    def start_draw_phase(self):
        self.game_state = "SCANNING"
        self.lbl_info.config(text="RONDE BARU.\nSilakan scan 1 kartu lagi dari tumpukan.")

    def show_discard_buttons(self):
        for w in self.discard_frame.winfo_children(): w.destroy()
        for i, card in enumerate(self.player_hand):
            txt = f"Buang {card['rank']} {card['suit']} ({card['value']})"
            tk.Button(self.discard_frame, text=txt, bg="#ffcdd2", 
                      command=lambda idx=i: self.process_discard(idx)).pack(fill="x", pady=2)

    def process_discard(self, idx):
        self.player_hand.pop(idx)
        for w in self.discard_frame.winfo_children(): w.destroy()
        self.update_display()
        
        if self.calc_score(self.player_hand) > 33:
            self.game_over("BUST! (Skor > 33). Anda Kalah.")
            return
            
        self.lbl_info.config(text="Giliran Komputer...", fg="black")
        self.root.after(1000, self.computer_move)

    def computer_move(self):
        if not self.deck:
            self.game_over("Deck Habis. Seri.")
            return
            
        self.computer_hand.append(self.deck.pop())
        best_hand = self.computer_hand[:3]
        best_diff = 100
        
        for combo in itertools.combinations(self.computer_hand, 3):
            score = self.calc_score(combo)
            if score <= 33:
                diff = 33 - score
                if diff < best_diff:
                    best_diff = diff
                    best_hand = list(combo)
        
        self.computer_hand = best_hand
        self.update_display()
        
        c_score = self.calc_score(self.computer_hand)

        if c_score > 33:
            self.game_over("KOMPUTER BUST! ANDA MENANG.")
            return

        # --- LOGIKA FINAL SETELAH 10 RONDE ---
        if self.current_round >= self.max_rounds:
            p_score = self.calc_score(self.player_hand)
            
            # Hitung jarak/selisih ke angka 33
            diff_p = 33 - p_score
            diff_c = 33 - c_score
            
            if diff_p < diff_c:
                msg = f"ANDA MENANG!\nSkor Anda ({p_score}) lebih dekat ke 33 daripada Komputer ({c_score})."
            elif diff_c < diff_p:
                msg = f"ANDA KALAH.\nSkor Komputer ({c_score}) lebih dekat ke 33 daripada Anda ({p_score})."
            else:
                msg = f"SERI! Jarak ke 33 sama (Anda: {p_score}, Komputer: {c_score})."
            
            self.game_over(msg)
        else:
            self.current_round += 1
            self.lbl_round.config(text=f"Ronde: {self.current_round}/{self.max_rounds}")
            self.start_draw_phase()
        # -------------------------------------

    def calc_score(self, hand):
        return sum(c['value'] for c in hand)

    def update_display(self):
        p_str = " ".join([f"[{c['rank']}{c['suit'][0]}]" for c in self.player_hand])
        self.lbl_p_score.config(text=f"Anda ({self.calc_score(self.player_hand)}):\n{p_str}")
        
        if self.game_state == "GAME_OVER":
            c_str = " ".join([f"[{c['rank']}{c['suit'][0]}]" for c in self.computer_hand])
            val = self.calc_score(self.computer_hand)
        else:
            c_str = "[?] " * len(self.computer_hand)
            val = "?"
        self.lbl_c_score.config(text=f"Komputer ({val}):\n{c_str}")

    def game_over(self, msg):
        self.game_state = "GAME_OVER"
        self.update_display()
        self.lbl_info.config(text=msg + "\nTekan MAIN LAGI untuk reset.", fg="red", font=("Arial", 12, "bold"))
        self.btn_main.config(state="normal", text="MAIN LAGI")

if __name__ == "__main__":
    root = tk.Tk()
    app = RobustCardGame(root)
    root.mainloop()