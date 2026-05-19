import socket
import threading
import time

BROADCAST_PORT = 5556
MAGIC_WORD = "SAPER_DUEL_SERVER"


class NetworkManager:
    def __init__(self, receive_callback=None):
        self.conn = None
        self.receive_callback = receive_callback
        self.is_hosting = False

    def host(self, on_connected_callback):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Uzycie portu 0 pozwala na uzycie pierwszego wolnego portu
        server.bind(('', 0))
        port = server.getsockname()[1]
        server.listen(1)

        self.is_hosting = True

        # Broadcast serwera gry
        threading.Thread(target=self._broadcast_presence, args=(port,), daemon=True).start()

        # Watek oczekiwania na gracza
        threading.Thread(target=self._accept_connection, args=(server, on_connected_callback), daemon=True).start()

    def _accept_connection(self, server, on_connected_callback):
        self.conn, addr = server.accept()
        self.is_hosting = False  # Wylaczenie nadawania po dolaczeniu do gry
        threading.Thread(target=self._listen, daemon=True).start()

        if on_connected_callback:
            on_connected_callback()

    def _broadcast_presence(self, port):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while self.is_hosting:
            message = f"{MAGIC_WORD}:{port}"
            try:
                udp_socket.sendto(message.encode('utf-8'), ('<broadcast>', BROADCAST_PORT))
            except Exception:
                pass
            time.sleep(1)
        udp_socket.close()

    def join(self, ip, port):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.conn.connect((ip, port))
            threading.Thread(target=self._listen, daemon=True).start()
            return True
        except Exception as e:
            print(f"Błąd łączenia: {e}")
            return False

    def send(self, message):
        if self.conn:
            try:
                self.conn.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Błąd wysyłania: {e}")

    def _listen(self):
        while True:
            try:
                data = self.conn.recv(1024).decode('utf-8')
                if not data:
                    break
                if self.receive_callback:
                    self.receive_callback(data)
            except:
                print("Połączenie zerwane.")
                break