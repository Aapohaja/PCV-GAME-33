import random
import tkinter as tk

# --- KONFIGURASI KARTU & ATURAN ---
# Mengatur nilai kartu sesuai proposal 
# As = 11, J, Q, K = 10, Angka = sesuai angka
SUITS = ['Heart', 'Diamond', 'Club', 'Spade']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 
    '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

def create_deck():
    # Membuat 52 kartu unik (Mencegah kartu keluar 2 kali)
    deck = []
    for suit in SUITS:
        for rank in RANKS:
            deck.append({'rank': rank, 'suit': suit, 'value': VALUES[rank]})
    random.shuffle(deck)
    #print("Deck setelah shuffle:", [(card['rank'], card['suit']) for card in deck])
    return deck

def calculate_score(hand):
    # Menjumlahkan nilai 3 kartu di tangan 
    return sum(card['value'] for card in hand)

def format_hand(hand, hidden=False):
    cards_str = []
    for i, card in enumerate(hand):
        if hidden:
            cards_str.append("[ TERTUTUP ]")
        else:
            cards_str.append(f"[{card['rank']} {card['suit']}]")
    if hidden:
        total = "???"
    else:
        total = str(calculate_score(hand))
    return " ".join(cards_str) + f"\nTotal: {total}"

class GameApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Game 33")
        self.root.geometry("780x640")
        self.root.configure(bg="#ffffff")
        self.root.resizable(False, False)

        self.deck = []
        self.player_hand = []
        self.computer_hand = []
        self.temp_hand = []
        self.current_round = 1
        self.max_rounds = 10
        self.game_over = False
        self.hide_computer = True

        self.container = tk.Frame(self.root, bg="#ffffff", padx=32, pady=32)
        self.container.pack(fill="both", expand=True)

        self.build_start_screen()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def build_start_screen(self):
        self.clear_container()

        title = tk.Label(
            self.container,
            text="Selamat Datang di Games 33",
            font=("Segoe UI", 22, "bold"),
            fg="#111827",
            bg="#ffffff"
        )
        title.pack(pady=(40, 12))

        desc = tk.Label(
            self.container,
            text="Capai total nilai kartu 33 tanpa melewati batas.\n"
                 "Tekan start untuk memulai.",
            font=("Segoe UI", 13),
            fg="#374151",
            bg="#ffffff",
            justify="center"
        )
        desc.pack(pady=(0, 30))

        start_btn = tk.Button(
            self.container,
            text="Start Game",
            font=("Segoe UI", 14, "bold"),
            bg="#d1fae5",
            fg="#065f46",
            activebackground="#a7f3d0",
            activeforeground="#065f46",
            relief="ridge",
            padx=28,
            pady=8,
            command=self.start_game
        )
        start_btn.pack()

    def start_game(self):
        self.deck = create_deck()

        self.player_hand = [self.deck.pop() for _ in range(3)]
        self.computer_hand = [self.deck.pop() for _ in range(3)]
        self.current_round = 1
        self.game_over = False
        self.hide_computer = True

        self.show_game_screen()
        self.start_round()

    def show_game_screen(self):
        self.clear_container()

        self.round_label = tk.Label(
            self.container,
            text="Ronde 1 / 10",
            font=("Segoe UI", 16, "bold"),
            fg="#111827",
            bg="#ffffff"
        )
        self.round_label.pack(anchor="w")

        hands_frame = tk.Frame(self.container, bg="#ffffff")
        hands_frame.pack(fill="x", pady=(16, 8))

        comp_frame = tk.Frame(hands_frame, bg="#f3f4f6", padx=12, pady=12, relief="groove", borderwidth=1)
        comp_frame.pack(side="left", expand=True, fill="both", padx=(0, 8))

        player_frame = tk.Frame(hands_frame, bg="#f3f4f6", padx=12, pady=12, relief="groove", borderwidth=1)
        player_frame.pack(side="left", expand=True, fill="both", padx=(8, 0))

        tk.Label(
            comp_frame,
            text="Kartu Komputer",
            font=("Segoe UI", 13, "bold"),
            fg="#111827",
            bg="#f3f4f6"
        ).pack(anchor="w")

        self.computer_cards_var = tk.StringVar()
        tk.Label(
            comp_frame,
            textvariable=self.computer_cards_var,
            font=("Consolas", 11),
            fg="#111827",
            bg="#f3f4f6",
            justify="left"
        ).pack(anchor="w", pady=(8, 0))

        tk.Label(
            player_frame,
            text="Kartu Anda",
            font=("Segoe UI", 13, "bold"),
            fg="#111827",
            bg="#f3f4f6"
        ).pack(anchor="w")

        self.player_cards_var = tk.StringVar()
        tk.Label(
            player_frame,
            textvariable=self.player_cards_var,
            font=("Consolas", 11),
            fg="#111827",
            bg="#f3f4f6",
            justify="left"
        ).pack(anchor="w", pady=(8, 0))

        self.message_var = tk.StringVar(value="Permainan dimulai.")
        self.message_label = tk.Label(
            self.container,
            textvariable=self.message_var,
            font=("Segoe UI", 12),
            fg="#374151",
            bg="#ffffff",
            justify="left",
            wraplength=700
        )
        self.message_label.pack(anchor="w", pady=(16, 8))

        self.control_frame = tk.Frame(self.container, bg="#ffffff")
        self.control_frame.pack(fill="x")

    def set_message(self, text):
        self.message_var.set(text)

    def clear_controls(self):
        for widget in self.control_frame.winfo_children():
            widget.destroy()

    def update_board(self):
        self.round_label.config(text=f"Ronde {self.current_round} / {self.max_rounds}")
        self.computer_cards_var.set(format_hand(self.computer_hand, hidden=self.hide_computer))
        self.player_cards_var.set(format_hand(self.player_hand, hidden=False))

    def start_round(self):
        if self.game_over:
            return

        self.hide_computer = True
        self.update_board()

        player_score = calculate_score(self.player_hand)
        if player_score == 33:
            self.finish_game("ANDA MENDAPATKAN 33! ANDA MENANG!")
            return

        self.new_card = self.deck.pop()
        self.temp_hand = self.player_hand + [self.new_card]

        self.set_message(
            f"Anda mengambil kartu: [{self.new_card['rank']} {self.new_card['suit']}].\n"
            "Pilih satu kartu untuk dibuang agar tetap memiliki 3 kartu."
        )
        self.render_discard_buttons()

    def render_discard_buttons(self):
        self.clear_controls()

        info = tk.Label(
            self.control_frame,
            text="Pilih kartu yang ingin dibuang:",
            font=("Segoe UI", 10, "bold"),
            fg="#111827",
            bg="#ffffff"
        )
        info.pack(anchor="w", pady=(0, 8))

        for idx, card in enumerate(self.temp_hand):
            btn = tk.Button(
                self.control_frame,
                text=f"Buang {card['rank']} {card['suit']} (Nilai {card['value']})",
                font=("Segoe UI", 10),
                bg="#e5e7eb",
                fg="#111827",
                activebackground="#d1d5db",
                activeforeground="#111827",
                relief="ridge",
                padx=10,
                pady=4,
                command=lambda i=idx: self.handle_discard(i)
            )
            btn.pack(fill="x", pady=4)

    def handle_discard(self, index):
        if self.game_over:
            return

        removed = self.temp_hand.pop(index)
        self.player_hand = self.temp_hand
        self.update_board()
        self.set_message(f"Anda membuang [{removed['rank']} {removed['suit']}]. Menunggu giliran komputer...")
        self.clear_controls()

        if calculate_score(self.player_hand) > 33:
            self.finish_game("Total nilai Anda melebihi 33 (BUST)! Anda Kalah.")
            return

        self.root.after(600, self.computer_turn)

    def computer_turn(self):
        if self.game_over:
            return

        c_new_card = self.deck.pop()
        c_temp_hand = self.computer_hand + [c_new_card]

        best_hand = None
        best_score = -1
        for i in range(4):
            test_hand = c_temp_hand[:]
            test_hand.pop(i)
            score = calculate_score(test_hand)
            if score <= 33 and score > best_score:
                best_score = score
                best_hand = test_hand

        if best_hand is None:
            min_score = 999
            for i in range(4):
                test_hand = c_temp_hand[:]
                test_hand.pop(i)
                score = calculate_score(test_hand)
                if score < min_score:
                    min_score = score
                    best_hand = test_hand

        self.computer_hand = best_hand
        self.update_board()
        self.set_message("Komputer telah memilih kartu terbaiknya.")

        if calculate_score(self.computer_hand) > 33:
            self.finish_game("Komputer melebihi 33 (BUST)! Anda Menang.")
            return

        self.post_round_prompt()

    # --- PERUBAHAN UTAMA DI SINI ---
    def post_round_prompt(self):
        if self.game_over:
            return

        if self.current_round < self.max_rounds:
            # Ubah pesan agar pemain tahu sistem berjalan otomatis
            self.set_message(
                "Ronde selesai. Melanjutkan ke ronde berikutnya..."
            )
            self.clear_controls()
            
            # Otomatis panggil next_round setelah 1.5 detik (1500 ms)
            self.root.after(0, self.next_round)
        else:
            self.finish_game("Batas ronde tercapai! Saatnya penentuan.")
    # -------------------------------

    def next_round(self):
        if self.game_over:
            return
        self.current_round += 1
        self.start_round()

    def finish_game(self, reason=None):
        if self.game_over:
            return
        self.game_over = True
        self.hide_computer = False
        self.update_board()
        self.clear_controls()

        summary = self.build_final_summary(reason)
        self.set_message(summary)

        restart_btn = tk.Button(
            self.control_frame,
            text="Main Lagi",
            font=("Segoe UI", 10, "bold"),
            bg="#d1fae5",
            fg="#065f46",
            activebackground="#a7f3d0",
            relief="ridge",
            padx=16,
            pady=6,
            command=self.build_start_screen
        )
        restart_btn.pack(side="left")

    def build_final_summary(self, reason=None):
        p_final = calculate_score(self.player_hand)
        c_final = calculate_score(self.computer_hand)

        lines = []
        if reason:
            lines.append(reason)

        lines.append(f"Skor Anda: {p_final}")
        lines.append(f"Skor Komputer: {c_final}")

        if p_final > 33 and c_final <= 33:
            lines.append("Anda Bust! Komputer Menang.")
        elif c_final > 33 and p_final <= 33:
            lines.append("Komputer Bust! Anda Menang.")
        elif p_final > 33 and c_final > 33:
            lines.append("Keduanya melebihi 33, tetapi tidak ada pemenang jelas.")
        else:
            if p_final > c_final:
                lines.append("SELAMAT! Anda Menang (lebih dekat ke 33).")
            elif c_final > p_final:
                lines.append("Komputer Menang (lebih dekat ke 33).")
            else:
                lines.append("SERI! Skor sama-sama dekat ke 33.")

        return "\n".join(lines)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    GameApp().run()