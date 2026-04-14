import socket
import threading

PORT = 5555

class NetworkManager:
    def __init__(self, receive_callback):
        self.conn = None
        self.receive_callback = receive_callback

    def host(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', PORT))
        server.listen(1)
        print("Czekam na przeciwnika")
        self.conn, addr = server.accept()
        print(f"Połączono z {addr}")

        # Nasłuchiwanie w tle
        threading.Thread(target=self._listen, daemon=True).start()

    def join(self, ip):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.conn.connect((ip, PORT))
            print("Połączono z hostem")
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
                self.receive_callback(data)
            except:
                print("Połączenie zerwane.")
                break