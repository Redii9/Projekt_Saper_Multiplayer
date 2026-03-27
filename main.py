import socket
import threading
import sys

PORT = 5555

def receive_data(conn):
    while True:
        try:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                print("\nPrzeciwnik sie rozlaczyl")
                break

            if data == "WYGRANA":
                print("\nPrzeciwnik ukonczyl plansze jako pierwszy PRZEGRYWASZ.")
            elif data == "BOMBA":
                print("\nPrzeciwnik trafil na mine WYGRYWASZ!")
            else:
                print(f"\nWiadomosc z sieci: {data}")

        except ConnectionResetError:
            print("\nPolaczenie zerwane.")
            break


def host_game():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', PORT))
    server.listen(1)
    print(f"Lobby utworzone port: {PORT}")

    conn, addr = server.accept()
    print(f"Gracz dolaczyl z adresu: {addr}")

    threading.Thread(target=receive_data, args=(conn,), daemon=True).start()
    return conn


def join_game(host_ip):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host_ip, PORT))
        print("Pomyslnie polaczono z hostem")

        # Watek nasluchiwania
        threading.Thread(target=receive_data, args=(client,), daemon=True).start()
        return client
    except Exception as e:
        print(f"Nie udalo sie polaczyc: {e}")
        return None


# Proste menu do testu
print("Saaaaper")
choice = input("Chcesz (1) Stworzyc lobby czy (2) Dolaczyc? : ")

if choice == '1':
    connection = host_game()
elif choice == '2':
    ip = input("Podaj IP Hosta: ")
    connection = join_game(ip)
else:
    print("Zly wybor.")
    sys.exit()

# Petla gry
if connection:
    print("Start (Wpisz 'w', aby zasymulowac wygrana, 'b' by zasymulowac bombe, 'q' by wyjsc)")
    while True:
        action = input("Twoj ruch: ")

        if action == 'w':
            connection.send("WYGRANA".encode('utf-8'))
            print("Wygrales")
        elif action == 'b':
            connection.send("BOMBA".encode('utf-8'))
            print("Uderzyles w mine")
        elif action == 'q':
            break

    connection.close()