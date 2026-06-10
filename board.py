import tkinter as tk
import random
from tkinter import messagebox


class MinesweeperGame:
    def __init__(self, root, network, is_host, return_to_menu_cb):
        self.root = root
        self.network = network
        self.is_host = is_host
        self.return_to_menu_cb = return_to_menu_cb

        self.size = 10
        self.num_mines = 12

        self.mines = set()
        self.flags = set()
        self.revealed = set()
        self.game_over = False

        # Blokowanie klikania
        self.is_waiting_for_player = is_host

        self.my_buttons = []
        self.opponent_buttons = []

        self.root.title("Saper Duel")
        self.setup_ui()

        self.default_bg = self.my_buttons[0][0].cget("background")

        self.generate_mines()

    def start_game(self):
        self.is_waiting_for_player = False

    def generate_mines(self):
        while len(self.mines) < self.num_mines:
            r = random.randint(0, self.size - 1)
            c = random.randint(0, self.size - 1)
            self.mines.add((r, c))

    def setup_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=20, pady=20)

        my_section = tk.LabelFrame(main_frame, text="Twoja plansza", padx=10, pady=10)
        my_section.pack(side="left", padx=10)
        self._create_grid(my_section, self.my_buttons, is_interactive=True)

        opp_section = tk.LabelFrame(main_frame, text="Przeciwnik", padx=10, pady=10)
        opp_section.pack(side="right", padx=10)
        self._create_grid(opp_section, self.opponent_buttons, is_interactive=False)

    def _create_grid(self, frame, button_list, is_interactive):
        for r in range(self.size):
            row = []
            for c in range(self.size):
                if is_interactive:
                    btn = tk.Button(frame, width=2, height=1, font=("Arial", 12, "bold"),
                                    command=lambda r=r, c=c: self.handle_my_click(r, c))
                    btn.bind("<Button-3>", lambda event, r=r, c=c: self.handle_right_click(event, r, c))
                else:
                    btn = tk.Button(frame, width=2, height=1, font=("Arial", 12, "bold"),
                                    state=tk.DISABLED, disabledforeground="black")
                btn.grid(row=r, column=c)
                row.append(btn)
            button_list.append(row)

    def count_mines_around(self, r, c):
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if 0 <= r + dr < self.size and 0 <= c + dc < self.size:
                    if (r + dr, c + dc) in self.mines:
                        count += 1
        return count

    def handle_right_click(self, event, r, c):
        # Zablokowane podczas czekania na gracza
        if self.game_over or self.is_waiting_for_player or (r, c) in self.revealed:
            return

        btn = self.my_buttons[r][c]
        if (r, c) in self.flags:
            self.flags.remove((r, c))
            btn.config(text="")
        else:
            self.flags.add((r, c))
            btn.config(text="🚩", fg="red")

    def handle_my_click(self, r, c):
        if self.game_over or self.is_waiting_for_player or (r, c) in self.revealed or (r, c) in self.flags:
            return

        if (r, c) in self.mines:
            self.lose_game(r, c)
            return

        self.reveal_cell(r, c)
        self.check_win()

    def reveal_cell(self, r, c):
        if (r, c) in self.revealed or (r, c) in self.flags:
            return

        self.revealed.add((r, c))
        mines_around = self.count_mines_around(r, c)

        btn = self.my_buttons[r][c]
        colors = ["", "blue", "green", "red", "purple", "maroon", "turquoise", "black", "gray"]
        color = colors[mines_around] if mines_around > 0 else "black"

        btn.config(bg="white", text=str(mines_around) if mines_around > 0 else "", disabledforeground=color,
                   state=tk.DISABLED)

        if self.network:
            self.network.send(f"UPDATE:{r},{c}\n")

        if mines_around == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if 0 <= r + dr < self.size and 0 <= c + dc < self.size:
                        if dr != 0 or dc != 0:
                            self.reveal_cell(r + dr, c + dc)

    def check_win(self):
        if len(self.revealed) == (self.size * self.size) - self.num_mines:
            self.game_over = True
            if self.network:
                self.network.send("GAME_OVER:WIN\n")
            self.show_end_dialog("Wygrałeś! Odkryłeś wszystkie bezpieczne pola.")

    def lose_game(self, r, c):
        self.game_over = True
        btn = self.my_buttons[r][c]
        btn.config(bg="red", text="💣")

        for (mr, mc) in self.mines:
            if (mr, mc) != (r, c):
                self.my_buttons[mr][mc].config(text="💣", fg="black")

        if self.network:
            self.network.send("GAME_OVER:LOSE\n")

        self.show_end_dialog("Przegrałeś! Kliknąłeś na minę.")

    def show_end_dialog(self, message):
        # Pytanie o zagranie ponownie
        odpowiedz = messagebox.askyesno("Koniec gry", f"{message}\n\nCzy chcesz zagrać ponownie z tym samym graczem?")
        if odpowiedz:
            self.reset_board()
            if self.network:
                self.network.send("RESTART\n")
        else:
            self.return_to_menu_cb()

    def reset_board(self):
        # Reset planszy bez zerwania polaczenia
        self.mines.clear()
        self.flags.clear()
        self.revealed.clear()
        self.game_over = False

        self.generate_mines()

        for r in range(self.size):
            for c in range(self.size):
                self.my_buttons[r][c].config(bg=self.default_bg, text="", fg="black", state=tk.NORMAL,
                                             disabledforeground="black")
                self.opponent_buttons[r][c].config(bg=self.default_bg, text="", state=tk.DISABLED)

    def receive_message(self, message):
        # Rozlaczenie sie
        if message == "DISCONNECT":
            messagebox.showinfo("Rozłączono", "Przeciwnik opuścił grę.")
            self.root.after(0, self.return_to_menu_cb)
            return

        messages = message.split('\n')
        for msg in messages:
            if not msg.strip():
                continue

            if msg.startswith("UPDATE:"):
                data = msg.split(":")[1]
                r, c = map(int, data.split(","))
                self.root.after(0, self._update_opponent_view, r, c)
            elif msg.startswith("GAME_OVER:"):
                status = msg.split(":")[1]
                self.root.after(0, self._handle_opponent_game_over, status)
            elif msg == "RESTART":
                # Ponowna gra dopiero jak obie osoby klikna tak
                pass

    def _update_opponent_view(self, r, c):
        self.opponent_buttons[r][c].config(bg="gray")

    def _handle_opponent_game_over(self, status):
        self.game_over = True
        if status == "LOSE":
            self.show_end_dialog("Wygrałeś! Twój przeciwnik kliknął na minę.")
        elif status == "WIN":
            self.show_end_dialog("Przegrałeś! Twój przeciwnik odkrył całą swoją planszę.")