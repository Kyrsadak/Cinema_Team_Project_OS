import socket
import threading

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

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("Disconnected from server.")
                break
            print(data.decode().strip())
        except:
            break


def main():
    server_ip = input("Enter server IP: ").strip()
    server_port = int(input("Enter server port: ").strip())

    nickname = input("Enter your nickname: ").strip()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))

    sock.send(nickname.encode())

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    print("\nCINEMA CLIENT")
    print("-----------------------")

    while True:
        print("\nSelect an option:")
        print("1) Show movie list")
        print("2) Show sessions for a movie")
        print("3) Book a ticket")
        print("4) Check balance")
        print("5) Exit")

        choice = input("> ").strip()

        if choice == "1":
            sock.send("LIST".encode())

        elif choice == "2":
            movie = input("Enter movie name: ").strip()
            sock.send(f"GET|{movie}".encode())

        elif choice == "3":
            while True:
                movie = input("Enter movie name: ").strip()
                lowerMovie = movie.lower()
                if lowerMovie not in cinema:
                    print("Wrong name, try again.")
                else:
                    break
            
            while True:   
                print(f"Available time for {movie}")
                for t in cinema[movie].keys():
                    print(f"- {t}")
                time = input("Enter session time (ex: 16:00): ").strip()

                if time not in cinema[movie]:
                    print("Wrong time, try again.")
                else:
                    break
                
            while True:
                
                seats = cinema[movie][time]["seats"]

                seat_status = ["Free" if s == 0 else "Taken" for s in seats]

                print(f"Available time for {movie} at {time}")

                for i, status in enumerate(seat_status):
                    print(f"Seat {i}: {status}")

                seat = input("Enter seat number (0-4): ").strip()
                if seat not in ["0", "1", "2", "3", "4"]:
                    print("Invalid seat, try again.")
                else:
                    break

            sock.send(f"BOOK|{movie}|{time}|{seat}".encode())

        elif choice == "4":
            sock.send("BAL".encode())

        elif choice == "5":
            print("Goodbye!")
            sock.close()
            break
        elif choice == "!refill":
            sock.send("!refill".encode())
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
