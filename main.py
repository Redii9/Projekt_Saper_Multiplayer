import tkinter as tk
from tkinter import messagebox
import socket
import threading
import time

from network import NetworkManager, BROADCAST_PORT, MAGIC_WORD
from board import MinesweeperGame

discovered_servers = {}
update_job = None
menu_window = None


def start_server_browser(listbox):
    def listen_for_servers():
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            udp_socket.bind(('', BROADCAST_PORT))
        except Exception as e:
            print(f"Błąd uruchamiania wyszukiwarki: {e}")
            return

        while True:
            try:
                data, addr = udp_socket.recvfrom(1024)
                msg = data.decode('utf-8')

                if msg.startswith(MAGIC_WORD):
                    port = int(msg.split(":")[1])
                    ip = addr[0]
                    discovered_servers[(ip, port)] = time.time()
            except Exception:
                pass

    threading.Thread(target=listen_for_servers, daemon=True).start()
    update_listbox(listbox)


def update_listbox(listbox):
    global update_job
    if not listbox.winfo_exists():
        return

    current_time = time.time()

    active_servers = {k: v for k, v in discovered_servers.items() if current_time - v < 3}
    discovered_servers.clear()
    discovered_servers.update(active_servers)

    new_items = [f"{ip}:{port}" for (ip, port) in discovered_servers.keys()]
    current_items = list(listbox.get(0, tk.END))

    if current_items != new_items:
        current_selection = listbox.curselection()
        selected_text = listbox.get(current_selection[0]) if current_selection else None

        listbox.delete(0, tk.END)
        for item in new_items:
            listbox.insert(tk.END, item)

            if item == selected_text:
                idx = listbox.get(0, tk.END).index(item)
                listbox.selection_set(idx)

    update_job = listbox.after(1000, update_listbox, listbox)


def launch_game_window(network, is_host):
    global menu_window

    # Ukrycie okna menu
    menu_window.withdraw()

    # Stworzenie okna gry
    game_window = tk.Toplevel(menu_window)

    def back_to_menu():
        network.close()
        game_window.destroy()  # Zamkniecie okna z gra
        menu_window.deiconify()  # Przywrocenie okna menu

    # Zamykanie na X
    game_window.protocol("WM_DELETE_WINDOW", back_to_menu)

    game = MinesweeperGame(game_window, network, is_host, back_to_menu)
    network.receive_callback = game.receive_message

    if is_host:
        game_window.title("Saper Duel - Oczekiwanie na gracza...")

        def on_connected():
            game_window.title("Saper Duel - GRA TRWA!")
            game.start_game()

        network.host(on_connected)
    else:
        game.start_game()


def host_game():
    network = NetworkManager()
    launch_game_window(network, True)


def join_game(listbox):
    selection = listbox.curselection()
    if not selection:
        messagebox.showwarning("Błąd", "Najpierw wybierz grę z listy!")
        return

    server_str = listbox.get(selection[0])
    ip, port_str = server_str.split(":")
    port = int(port_str)

    network = NetworkManager()
    if network.join(ip, port):
        launch_game_window(network, False)
    else:
        messagebox.showerror("Błąd", "Nie udało się połączyć.")


def init_app():
    global menu_window

    menu_window = tk.Tk()
    menu_window.title("Saper - Lobby")
    menu_window.geometry("350x400")

    tk.Label(menu_window, text="Saper Multiplayer", font=("Arial", 16, "bold")).pack(pady=15)
    tk.Button(menu_window, text="Stwórz lobby (Host)", command=host_game, bg="lightgreen", font=("Arial", 12)).pack(
        fill='x', padx=20, pady=5)

    tk.Label(menu_window, text="Dostępne gry w sieci LAN:").pack(pady=(20, 0))

    server_listbox = tk.Listbox(menu_window, width=40, height=8, font=("Arial", 10))
    server_listbox.pack(padx=20, pady=5)

    tk.Button(menu_window, text="Dołącz do wybranej gry", command=lambda: join_game(server_listbox), bg="lightblue",
              font=("Arial", 12)).pack(fill='x', padx=20, pady=5)

    start_server_browser(server_listbox)
    menu_window.mainloop()


if __name__ == "__main__":
    init_app()