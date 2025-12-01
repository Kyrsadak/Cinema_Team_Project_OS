import socket
import threading
import time


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
        "18:00": {
            "price": 40000, "seats": [0, 0, 0, 0, 0]
            },
        "20:00": {
            "price": 50000, "seats": [0, 0, 0, 0, 0]
            },
    },
    "formula 1": {
        "15:00": {
            "price": 45000, "seats": [0, 0, 0, 0, 0]
        }
    },
    "stattrack": {
        "16:00": {
            "price": 60000, "seats": [0, 0, 0, 0, 0]
        },
        "18:00": {
            "price": 70000, "seats": [0, 0, 0, 0, 0]
        }
    },
    "superman": {
        "18:00": {
            "price": 45000, "seats": [0, 0, 0, 0, 0]
        }
    },
     "harry potter": {
        "16:00": {
            "price": 50000, "seats": [0, 0, 0, 0, 0]
        },
        "20:00": {
            "price": 50000, "seats": [0, 0, 0, 0, 0]
        }
    },
     "people in black": {
        "12:00": {
            "price": 60000, "seats": [0, 0, 0, 0, 0]
        }
    },

}

last_server_response = ""
response_event = threading.Event()


def receive_messages(sock):
    global last_server_response
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\n[!] Disconnected from server.")
                break
            
            message = data.decode().strip()
            print(f"\n[SERVER] {message}")
            
            last_server_response = message
            response_event.set() 
            
        except Exception as e:
            print(f"\n[ERROR] Connection error: {e}")
            break


def main():
    server_ip = input("Enter server IP: ").strip() 
    server_port_input = input("Enter server port: ").strip()
    
    if not server_port_input:
        print("Port is required.")
        return
    
    try:
        server_port = int(server_port_input)
    except ValueError:
        print("Invalid port number.")
        return

    nickname = input("Enter your nickname: ").strip()
    if not nickname:
        print("Nickname cannot be empty.")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_ip, server_port))
        print(f"Connected to {server_ip}:{server_port}")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    sock.send(nickname.encode())

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    print("\n" + "="*40)
    print("       CINEMA BOOKING SYSTEM")
    print("="*40)

    while True:
        time.sleep(0.3)
        
        print("\n" + "-"*40)
        print("Select an option:")
        print("  1) Show movie list")
        print("  2) Show sessions for a movie")
        print("  3) Book a ticket")
        print("  4) Check balance")
        print("  5) Exit")
        print("-"*40)

        choice = input("\n> ").strip()

        if choice == "1":
            sock.send("LIST".encode())

        elif choice == "2":
            movie = input("Enter movie name: ").strip()
            if movie:
                lowerMovie = movie.lower()
                sock.send(f"GET|{lowerMovie}".encode())
            else:
                print("Movie name cannot be empty.")

        elif choice == "3":
            booking_cancelled = False
            movie = None
            time_val = None
            
            # 1. Выбор фильма
            while not booking_cancelled:
                print("\n" + "="*40)
                print("SELECT MOVIE")
                print("="*40)
                movie_input = input("Enter movie name or 'c' to cancel: ").strip()

                if movie_input.lower() == 'c':
                    print("Booking cancelled.")
                    booking_cancelled = True
                    break

                lowerMovie = movie_input.lower()
                if lowerMovie not in cinema:
                    print(f"Movie '{movie_input}' not found. Try again.")
                    print("\nAvailable movies:")
                    for m in cinema.keys():
                        print(f"  - {m.title()}")
                else:
                    movie = lowerMovie
                    break
            
            # 2. Выбор времени 
            while not booking_cancelled and movie:
                print("\n" + "="*40)
                print("SELECT TIME")
                print("="*40)
                print(f"Available times for '{movie_input.title()}':")
                for t in cinema[movie].keys():
                    price = cinema[movie][t]["price"]
                    print(f"  - {t} (Price: {price:,} UZS)")
                
                time_val = input("\nEnter session time (e.g., 16:00) or 'c' to cancel: ").strip()

                if time_val.lower() == 'c':
                    print("Booking cancelled.")
                    booking_cancelled = True
                    break

                if time_val not in cinema[movie]:
                    print(f"Time '{time_val}' not available. Try again.")
                    time_val = None
                else:
                    break
            
            # 3. Выбор места 
            if not booking_cancelled and movie and time_val:
                while True:
                    print("\n" + "="*40)
                    print("STEP 3: SELECT SEAT")
                    print("="*40)
                    
                    seats = cinema[movie][time_val]["seats"]
                    price = cinema[movie][time_val]["price"]
                    
                    print(f"Booking for '{movie_input.title()}' at {time_val}")
                    print(f"Price: {price:,} UZS per ticket")
                    print("\nSeat availability:")
                    print("  ", end="")
                    for i in range(len(seats)):
                        print(f"[{i}]", end=" ")
                    print()
                    print("  ", end="")
                    for seat_status in seats:
                        if seat_status == 0:
                            print(" ✓ ", end=" ")  # Free
                        else:
                            print(" ✗ ", end=" ")  # Taken
                    print("\n")

                    seat = input("Enter seat number (0-4) or 'c' to cancel: ").strip()
                    
                    if seat.lower() == 'c':
                        print("Booking cancelled.")
                        break

                    if not seat.isdigit() or int(seat) not in range(5):
                        print("Invalid seat number. Please enter 0-4.")
                        continue
                    
                    seat_num = int(seat)
                    
                    if seats[seat_num] == 1:
                        print(f"Seat {seat_num} is already taken. Please choose another.")
                        continue

                    response_event.clear()
                    sock.send(f"BOOK|{movie}|{time_val}|{seat}".encode())

                    print("\nChecking availability with server...")
                    
                    if response_event.wait(timeout=5.0):
                        if "Seat already taken" in last_server_response:
                            print("\nERROR: This seat is already taken on the server!")
                            print("Please choose another seat.")
                            cinema[movie][time_val]["seats"][seat_num] = 1
                        
                        elif "SUCCESS" in last_server_response:
                            print("\nSUCCESS! Ticket purchased.")
                            print(f"Movie: {movie_input.title()}")
                            print(f"Time: {time_val}")
                            print(f"Seat: {seat_num}")
                            print(f"Price: {price:,} UZS")
                            cinema[movie][time_val]["seats"][seat_num] = 1
                            break
                        
                        elif "Not enough balance" in last_server_response:
                            print("\nInsufficient funds to complete purchase.")
                            print("Please check your balance (option 4).")
                            break
                        
                        else:
                            print(f"\n⚠ Unexpected response from server.")
                            break
                    else:
                        print("\nServer timeout. Please try again later.")
                        break

        elif choice == "4":
            sock.send("BAL".encode())

        elif choice == "5":
            print("\n" + "="*40)
            print("Thank you for using Cinema Booking!")
            print("Goodbye!")
            print("="*40)
            sock.close()
            break
        
        elif choice == "!refill":
            sock.send("!refill".encode())
            
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()