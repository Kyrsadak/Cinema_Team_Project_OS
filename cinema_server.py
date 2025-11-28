import socket
import threading

HOST = "0.0.0.0"
PORT = int(input("Enter the port for server (1024-49151): "))

cinema = {
    "avatar 3": {
        "16:00": {
            "price": 50000, "seats": [0, 0, 0, 0, 0]
            },
        "19:00": {
            "price": 60000, "seats": [0, 0, 0, 0, 0]
            }
    },
    "interstellar": {
        "18:00": {
            "price": 40000, "seats": [0, 0, 0, 0, 0]
            }
    },
    "zootopia 2": {
        "20:00": {
            "price": 30000, "seats": [0, 0, 0, 0, 0]
            }
    },
    "formula 1": {
        "15:00": {
            "price": 45000, "seats": [0, 0, 0, 0, 0]
        }
    }
}

clients = {}    
balances = {}    


def send(conn, msg):
    conn.send((msg + "\n").encode())



def handle_booking(nick, movie, time, seat, conn):
    movie = movie.strip()
    time  = time.strip()

    if movie not in cinema:
        send(conn, "ERROR: Movie not found.")
        return

    if time not in cinema[movie]:
        send(conn, "ERROR: Time not found.")
        return

    session = cinema[movie][time]
    price = session["price"]

    if seat < 0 or seat >= len(session["seats"]):
        send(conn, "ERROR: Invalid seat.")
        return

    if session["seats"][seat] == 1:
        send(conn, "ERROR: Seat already taken.")
        return

    if balances[nick] < price:
        send(conn, "ERROR: Not enough balance.")
        return


    session["seats"][seat] = 1
    balances[nick] -= price
    print(f"[PURCHASE] {nick} bought seat {seat} for '{movie}' at {time}. Remaining balace = {balances[nick]}")

    send(conn, f"SUCCESS: Seat {seat} booked for '{movie}' at {time}. Remaining balance: {balances[nick]}")



def client_thread(conn, addr):

    nickname = conn.recv(1024).decode().strip()
    clients[conn] = nickname
    balances[nickname] = 100000

    send(conn, "Connected to CINEMA SERVER")
    send(conn, f"Your balance: {balances[nickname]}")
    print(f"[SERVER] {nickname} connected to the server from {addr}, balance {balances[nickname]}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            msg = data.decode().strip()
            parts = msg.split("|")

            command = parts[0]

            if command == "LIST":
                send(conn, "=== MOVIES ===")
                for m in cinema:
                    send(conn, f"- {m}")
                


            elif command == "GET":
                movie = parts[1]

                if movie not in cinema:
                    send(conn, "ERROR: Movie not found.")
                    continue

                send(conn, f"=== {movie} sessions ===")
                for t in cinema[movie]:
                    session = cinema[movie][t]
                    send(conn, f"{t} | price={session['price']} | seats={session['seats']}")

            elif command == "BOOK":
                if len(parts) < 4:
                    send(conn, "ERROR: Invalid command format.")

                movie = parts[1]

                time = parts[2]
                
                try:
                    seat = int(parts[3])
                except:
                    send(conn, "ERROR: The seat must to be a number.")

                handle_booking(nickname, movie, time, seat, conn)

            elif command == "BAL":
                send(conn, f"BALANCE: {balances[nickname]}")
            
            elif command == "!refill":
                balances[nickname] += 20000
                send(conn, f"The cheat code was successfully executed. Current balance {balances[nickname]}")

            else:
                send(conn, "ERROR: Unknown command.")

    except:
        print(f"[SERVER] Error with client {addr}")

    finally:
        print(f"[SERVER] Client {clients[conn]} disconnected")
        del clients[conn]
        conn.close()


def start_server():
    print(f"[SERVER] Simple Cinema Server running on {HOST}:{PORT}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=client_thread, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()
