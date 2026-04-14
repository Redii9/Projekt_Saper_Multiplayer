import tkinter as tk
from network import NetworkManager
from board import MinesweeperGame

def start_game(is_host, ip=""):
    menu_window.destroy()
    root = tk.Tk()
    game = MinesweeperGame(root, None)

    network = NetworkManager(game.receive_message)
    game.network = network

    if is_host:
        network.host()
    else:
        success = network.join(ip)
        if not success:
            print("Nie udało się połączyć")
            return

    root.mainloop()

menu_window = tk.Tk()
menu_window.title("Saper")
menu_window.geometry("300x150")

tk.Label(menu_window, text="Wybierz tryb gry:").pack(pady=10)

tk.Button(menu_window, text="Stwórz lobby (Host)", command=lambda: start_game(True)).pack(fill='x', padx=20, pady=5)

join_frame = tk.Frame(menu_window)
join_frame.pack(fill='x', padx=20, pady=5)

ip_entry = tk.Entry(join_frame, width=15)
ip_entry.insert(0, "127.0.0.1")
ip_entry.pack(side='left', padx=5)

tk.Button(join_frame, text="Dołącz", command=lambda: start_game(False, ip_entry.get())).pack(side='left', expand=True,
                                                                                             fill='x')

menu_window.mainloop()