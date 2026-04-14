import tkinter as tk


class MinesweeperGame:
    def __init__(self, root, network):
        self.root = root
        self.network = network
        self.size = 10

        # Przechowywanie przycisków
        self.my_buttons = []
        self.opponent_buttons = []

        self.root.title("Saper Duel")
        self.setup_ui()

    def setup_ui(self):
        # Kontener na obie plansze
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=20, pady=20)

        # 1 plansza
        my_section = tk.LabelFrame(main_frame, text="Twoja plansza", padx=10, pady=10)
        my_section.pack(side="left", padx=10)
        self._create_grid(my_section, self.my_buttons, is_interactive=True)

        # 2 plansza
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
                else:
                    btn = tk.Button(frame, width=2, height=1, font=("Arial", 12, "bold"),
                                    state=tk.DISABLED, disabledforeground="black")

                btn.grid(row=r, column=c)
                row.append(btn)
            button_list.append(row)

    def handle_my_click(self, r, c):
        # Logika kliknięcia dodać tu sprawdzanie czy jest mina
        self.my_buttons[r][c].config(bg="white", text="0", state=tk.DISABLED)

        if self.network:
            self.network.send(f"UPDATE:{r},{c}")

    def receive_message(self, message):
        if message.startswith("UPDATE:"):
            data = message.split(":")[1]
            r, c = map(int, data.split(","))
            self.root.after(0, self._update_opponent_view, r, c)

    def _update_opponent_view(self, r, c):
        self.opponent_buttons[r][c].config(bg="gray")