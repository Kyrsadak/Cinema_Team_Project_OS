```python
# Импортируем необходимые библиотеки
import socket      # Для работы с сетевыми соединениями (TCP/IP)
import threading   # Для создания параллельных потоков (многопоточность)
import time        # Для работы с задержками времени


# ========== БАЗА ДАННЫХ КИНОТЕАТРА ==========
# Словарь cinema хранит всю информацию о фильмах, сеансах и местах
# Структура: {название_фильма: {время: {цена, места}}}
# Места представлены списком: 0 = свободно, 1 = занято
cinema = {
    "avatar 3": {
        "16:00": {"price": 50000, "seats": [0, 0, 0, 0, 0]},  # 5 мест для сеанса в 16:00
        "19:00": {"price": 60000, "seats": [0, 0, 0, 0, 0]}   # 5 мест для сеанса в 19:00
    },
    "interstellar": {
        "18:00": {"price": 40000, "seats": [0, 0, 0, 0, 0]}
    },
    "zootopia 2": {
        "18:00": {"price": 40000, "seats": [0, 0, 0, 0, 0]},
        "20:00": {"price": 50000, "seats": [0, 0, 0, 0, 0]},
    },
    "formula 1": {
        "15:00": {"price": 45000, "seats": [0, 0, 0, 0, 0]}
    },
    "stattrack": {
        "16:00": {"price": 60000, "seats": [0, 0, 0, 0, 0]},
        "18:00": {"price": 70000, "seats": [0, 0, 0, 0, 0]}
    },
    "superman": {
        "18:00": {"price": 45000, "seats": [0, 0, 0, 0, 0]}
    },
    "harry potter": {
        "16:00": {"price": 50000, "seats": [0, 0, 0, 0, 0]},
        "20:00": {"price": 50000, "seats": [0, 0, 0, 0, 0]}
    },
    "people in black": {
        "12:00": {"price": 60000, "seats": [0, 0, 0, 0, 0]}
    },
}

# ========== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ДЛЯ СИНХРОНИЗАЦИИ ==========
# last_server_response - хранит последнее сообщение от сервера
last_server_response = ""

# response_event - объект для синхронизации потоков
# Используется для ожидания ответа от сервера
response_event = threading.Event()


# ========== ФУНКЦИЯ ДЛЯ ПРИЁМА СООБЩЕНИЙ ОТ СЕРВЕРА ==========
def receive_messages(sock):
    """
    Эта функция работает в отдельном потоке и постоянно слушает сервер.
    Когда приходит сообщение, оно печатается и сохраняется.
    
    Параметры:
        sock - сокет соединения с сервером
    """
    global last_server_response  # Используем глобальную переменную
    
    # Бесконечный цикл для постоянного прослушивания сервера
    while True:
        try:
            # Пытаемся получить данные от сервера (максимум 1024 байта)
            data = sock.recv(1024)
            
            # Если данных нет, значит соединение разорвано
            if not data:
                print("\n[!] Disconnected from server.")
                break  # Выходим из цикла
            
            # Декодируем байты в строку и убираем пробелы по краям
            message = data.decode().strip()
            
            # Печатаем сообщение для пользователя
            print(f"\n[SERVER] {message}")
            
            # Сохраняем последнее сообщение в глобальную переменную
            last_server_response = message
            
            # Сигнализируем главному потоку, что пришёл ответ
            # Это разблокирует функцию wait() в главном потоке
            response_event.set() 
            
        except Exception as e:
            # Если произошла ошибка (например, проблемы с сетью)
            print(f"\n[ERROR] Connection error: {e}")
            break  # Выходим из цикла


# ========== ГЛАВНАЯ ФУНКЦИЯ ПРОГРАММЫ ==========
def main():
    """
    Главная функция, которая:
    1. Подключается к серверу
    2. Отображает меню
    3. Обрабатывает действия пользователя
    """
    
    # ===== ШАГ 1: ПОДКЛЮЧЕНИЕ К СЕРВЕРУ =====
    
    # Запрашиваем IP-адрес сервера у пользователя
    server_ip = input("Enter server IP: ").strip() 
    
    # Запрашиваем порт сервера
    server_port_input = input("Enter server port: ").strip()
    
    # Проверяем, что порт не пустой
    if not server_port_input:
        print("Port is required.")
        return  # Выходим из функции
    
    # Пытаемся преобразовать строку в число
    try:
        server_port = int(server_port_input)
    except ValueError:
        # Если не удалось преобразовать, выводим ошибку
        print("Invalid port number.")
        return

    # Запрашиваем никнейм пользователя
    nickname = input("Enter your nickname: ").strip()
    
    # Проверяем, что никнейм не пустой
    if not nickname:
        print("Nickname cannot be empty.")
        return

    # Создаём TCP сокет
    # AF_INET - это IPv4, SOCK_STREAM - это TCP протокол
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Пытаемся подключиться к серверу
    try:
        sock.connect((server_ip, server_port))  # Подключаемся к IP:PORT
        print(f"Connected to {server_ip}:{server_port}")
    except Exception as e:
        # Если не удалось подключиться, выводим ошибку
        print(f"Connection failed: {e}")
        return

    # Отправляем никнейм серверу (кодируем строку в байты)
    sock.send(nickname.encode())

    # ===== ШАГ 2: ЗАПУСК ПОТОКА ДЛЯ ПРИЁМА СООБЩЕНИЙ =====
    
    # Создаём и запускаем новый поток для функции receive_messages
    # daemon=True означает, что поток завершится при завершении программы
    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    # ===== ШАГ 3: ОТОБРАЖЕНИЕ ГЛАВНОГО МЕНЮ =====
    
    # Красивый заголовок программы
    print("\n" + "="*40)
    print("       CINEMA BOOKING SYSTEM")
    print("="*40)

    # ===== ШАГ 4: ГЛАВНЫЙ ЦИКЛ ПРОГРАММЫ =====
    
    # Бесконечный цикл для работы с меню
    while True:
        # Небольшая пауза, чтобы меню не смешивалось с сообщениями от сервера
        time.sleep(0.3)
        
        # Выводим меню с доступными опциями
        print("\n" + "-"*40)
        print("Select an option:")
        print("  1) Show movie list")           # Показать список фильмов
        print("  2) Show sessions for a movie")  # Показать сеансы для фильма
        print("  3) Book a ticket")              # Забронировать билет
        print("  4) Check balance")              # Проверить баланс
        print("  5) Exit")                       # Выйти из программы
        print("-"*40)

        # Читаем выбор пользователя и убираем пробелы
        choice = input("\n> ").strip()

        # ========== ОБРАБОТКА ВЫБОРА 1: ПОКАЗАТЬ СПИСОК ФИЛЬМОВ ==========
        if choice == "1":
            # Отправляем команду "LIST" серверу
            sock.send("LIST".encode())

        # ========== ОБРАБОТКА ВЫБОРА 2: ПОКАЗАТЬ СЕАНСЫ ДЛЯ ФИЛЬМА ==========
        elif choice == "2":
            # Запрашиваем название фильма
            movie = input("Enter movie name: ").strip()
            
            # Проверяем, что название не пустое
            if movie:
                # Переводим в нижний регистр для сравнения
                lowerMovie = movie.lower()
                # Отправляем команду "GET|название_фильма" серверу
                sock.send(f"GET|{lowerMovie}".encode())
            else:
                print("Movie name cannot be empty.")

        # ========== ОБРАБОТКА ВЫБОРА 3: БРОНИРОВАНИЕ БИЛЕТА ==========
        elif choice == "3":
            # Флаг для отслеживания отмены бронирования
            booking_cancelled = False
            
            # Переменные для хранения выбранного фильма и времени
            movie = None      # Название выбранного фильма
            time_val = None   # Выбранное время сеанса
            
            # ===== ШАГ 3.1: ВЫБОР ФИЛЬМА =====
            
            # Цикл продолжается, пока пользователь не выберет фильм или не отменит
            while not booking_cancelled:
                # Красивый заголовок для шага выбора фильма
                print("\n" + "="*40)
                print("SELECT MOVIE")
                print("="*40)
                
                # Запрашиваем название фильма или 'c' для отмены
                movie_input = input("Enter movie name or 'c' to cancel: ").strip()

                # Если пользователь ввёл 'c', отменяем бронирование
                if movie_input.lower() == 'c':
                    print("Booking cancelled.")
                    booking_cancelled = True  # Устанавливаем флаг отмены
                    break  # Выходим из цикла выбора фильма

                # Переводим название в нижний регистр для поиска в словаре
                lowerMovie = movie_input.lower()
                
                # Проверяем, есть ли такой фильм в нашей базе
                if lowerMovie not in cinema:
                    # Если фильма нет, выводим ошибку
                    print(f"Movie '{movie_input}' not found. Try again.")
                    
                    # Показываем список доступных фильмов
                    print("\nAvailable movies:")
                    for m in cinema.keys():
                        # .title() делает первую букву каждого слова заглавной
                        print(f"  - {m.title()}")
                else:
                    # Если фильм найден, сохраняем его и выходим из цикла
                    movie = lowerMovie
                    break
            
            # ===== ШАГ 3.2: ВЫБОР ВРЕМЕНИ СЕАНСА =====
            
            # Этот цикл выполняется только если:
            # - Бронирование не отменено (not booking_cancelled)
            # - И фильм выбран (movie не None)
            while not booking_cancelled and movie:
                # Заголовок для шага выбора времени
                print("\n" + "="*40)
                print("SELECT TIME")
                print("="*40)
                
                # Выводим список доступных сеансов для выбранного фильма
                print(f"Available times for '{movie_input.title()}':")
                
                # Проходим по всем временам сеансов для этого фильма
                for t in cinema[movie].keys():
                    # Получаем цену для каждого сеанса
                    price = cinema[movie][t]["price"]
                    # Выводим время и цену (с разделителями тысяч)
                    print(f"  - {t} (Price: {price:,} UZS)")
                
                # Запрашиваем время сеанса или 'c' для отмены
                time_val = input("\nEnter session time (e.g., 16:00) or 'c' to cancel: ").strip()

                # Если пользователь ввёл 'c', отменяем бронирование
                if time_val.lower() == 'c':
                    print("Booking cancelled.")
                    booking_cancelled = True  # Устанавливаем флаг отмены
                    break  # Выходим из цикла

                # Проверяем, есть ли такое время для выбранного фильма
                if time_val not in cinema[movie]:
                    # Если времени нет, выводим ошибку
                    print(f"Time '{time_val}' not available. Try again.")
                    # ВАЖНО! Сбрасываем time_val в None
                    # Это предотвращает переход к следующему шагу с неверным временем
                    time_val = None
                else:
                    # Если время корректное, выходим из цикла
                    break
            
            # ===== ШАГ 3.3: ВЫБОР МЕСТА =====
            
            # Этот блок выполняется только если:
            # - Бронирование не отменено (not booking_cancelled)
            # - Фильм выбран (movie не None)
            # - Время выбрано (time_val не None)
            if not booking_cancelled and movie and time_val:
                
                # Бесконечный цикл для выбора места
                # Будет повторяться, пока не выберем свободное место или не отменим
                while True:
                    # Заголовок для шага выбора места
                    print("\n" + "="*40)
                    print("STEP 3: SELECT SEAT")
                    print("="*40)
                    
                    # Получаем список мест для выбранного фильма и времени
                    # seats - это список типа [0, 1, 0, 0, 1]
                    seats = cinema[movie][time_val]["seats"]
                    
                    # Получаем цену билета
                    price = cinema[movie][time_val]["price"]
                    
                    # Выводим информацию о бронировании
                    print(f"Booking for '{movie_input.title()}' at {time_val}")
                    print(f"Price: {price:,} UZS per ticket")
                    
                    # ===== ВИЗУАЛИЗАЦИЯ МЕСТ =====
                    print("\nSeat availability:")
                    
                    # Первая строка: номера мест [0] [1] [2] [3] [4]
                    print("  ", end="")  # Отступ
                    for i in range(len(seats)):
                        print(f"[{i}]", end=" ")  # Печатаем номер места
                    print()  # Переход на новую строку
                    
                    # Вторая строка: статус мест ✓ или ✗
                    print("  ", end="")  # Отступ
                    for seat_status in seats:
                        if seat_status == 0:
                            print(" ✓ ", end=" ")  # ✓ = место свободно
                        else:
                            print(" ✗ ", end=" ")  # ✗ = место занято
                    print("\n")  # Две пустые строки

                    # Запрашиваем номер места или 'c' для отмены
                    seat = input("Enter seat number (0-4) or 'c' to cancel: ").strip()
                    
                    # Если пользователь хочет отменить
                    if seat.lower() == 'c':
                        print("Booking cancelled.")
                        break  # Выходим из цикла выбора места

                    # ===== ВАЛИДАЦИЯ НОМЕРА МЕСТА =====
                    
                    # Проверяем:
                    # 1. seat.isdigit() - является ли введённое значение числом
                    # 2. int(seat) not in range(5) - находится ли число в диапазоне 0-4
                    if not seat.isdigit() or int(seat) not in range(5):
                        print("Invalid seat number. Please enter 0-4.")
                        continue  # Возвращаемся в начало цикла
                    
                    # Преобразуем строку в число
                    seat_num = int(seat)
                    
                    # ===== ПРОВЕРКА ДОСТУПНОСТИ МЕСТА ЛОКАЛЬНО =====
                    
                    # Проверяем, не занято ли место в локальной базе
                    if seats[seat_num] == 1:
                        print(f"Seat {seat_num} is already taken. Please choose another.")
                        continue  # Возвращаемся в начало цикла

                    # ===== ОТПРАВКА ЗАПРОСА НА СЕРВЕР =====
                    
                    # Сбрасываем событие перед отправкой запроса
                    # Это нужно, чтобы wait() ждал именно новый ответ
                    response_event.clear()
                    
                    # Отправляем команду бронирования на сервер
                    # Формат: BOOK|название_фильма|время|номер_места
                    sock.send(f"BOOK|{movie}|{time_val}|{seat}".encode())

                    # Информируем пользователя, что проверяем доступность
                    print("\nChecking availability with server...")
                    
                    # ===== ОЖИДАНИЕ ОТВЕТА ОТ СЕРВЕРА =====
                    
                    # Ждём ответ от сервера максимум 5 секунд
                    # wait() блокирует выполнение до тех пор, пока:
                    # - response_event.set() не будет вызван в receive_messages()
                    # - ИЛИ пройдёт 5 секунд (timeout)
                    if response_event.wait(timeout=5.0):
                        # Если получили ответ, проверяем его содержимое
                        
                        # ===== ОБРАБОТКА РАЗЛИЧНЫХ ОТВЕТОВ СЕРВЕРА =====
                        
                        # Случай 1: Место уже занято на сервере
                        if "Seat already taken" in last_server_response:
                            print("\nERROR: This seat is already taken on the server!")
                            print("Please choose another seat.")
                            
                            # Обновляем локальную базу данных
                            # Помечаем место как занятое (1)
                            cinema[movie][time_val]["seats"][seat_num] = 1
                            # НЕ выходим из цикла - пользователь может выбрать другое место
                        
                        # Случай 2: Успешная покупка
                        elif "SUCCESS" in last_server_response:
                            print("\nSUCCESS! Ticket purchased.")
                            
                            # Выводим детали покупки
                            print(f"Movie: {movie_input.title()}")
                            print(f"Time: {time_val}")
                            print(f"Seat: {seat_num}")
                            print(f"Price: {price:,} UZS")
                            
                            # Обновляем локальную базу - помечаем место как занятое
                            cinema[movie][time_val]["seats"][seat_num] = 1
                            
                            # Выходим из цикла - бронирование завершено
                            break
                        
                        # Случай 3: Недостаточно средств
                        elif "Not enough balance" in last_server_response:
                            print("\nInsufficient funds to complete purchase.")
                            print("Please check your balance (option 4).")
                            
                            # Выходим из цикла - нужно пополнить баланс
                            break
                        
                        # Случай 4: Неожиданный ответ от сервера
                        else:
                            print(f"\n⚠ Unexpected response from server.")
                            break  # Выходим из цикла
                            
                    else:
                        # Если прошло 5 секунд и ответа не пришло
                        print("\nServer timeout. Please try again later.")
                        break  # Выходим из цикла

        # ========== ОБРАБОТКА ВЫБОРА 4: ПРОВЕРКА БАЛАНСА ==========
        elif choice == "4":
            # Отправляем команду "BAL" (balance) серверу
            sock.send("BAL".encode())

        # ========== ОБРАБОТКА ВЫБОРА 5: ВЫХОД ИЗ ПРОГРАММЫ ==========
        elif choice == "5":
            # Красивое прощальное сообщение
            print("\n" + "="*40)
            print("Thank you for using Cinema Booking!")
            print("Goodbye!")
            print("="*40)
            
            # Закрываем соединение с сервером
            sock.close()
            
            # Выходим из главного цикла while True
            break
        
        # ========== СЕКРЕТНАЯ КОМАНДА: ПОПОЛНЕНИЕ БАЛАНСА ==========
        elif choice == "!refill":
            # Отправляем команду пополнения на сервер
            sock.send("!refill".encode())
            
        # ========== ОБРАБОТКА НЕВЕРНОГО ВЫБОРА ==========
        else:
            print("Invalid option. Please try again.")


# ========== ТОЧКА ВХОДА В ПРОГРАММУ ==========
# Этот блок выполняется только если файл запущен напрямую
# (а не импортирован как модуль)
if __name__ == "__main__":
    main()  # Запускаем главную функцию
```

```python
##  ДОПОЛНИТЕЛЬНЫЕ ПОЯСНЕНИЯ

### Как работает многопоточность в этой программе:

1. **Главный поток** - работает в функции `main()`, отображает меню и обрабатывает команды пользователя
2. **Поток приёма** - работает в функции `receive_messages()`, постоянно слушает сервер
```
### Синхронизация потоков через `threading.Event()`:
```
Главный поток                    Поток приёма
     |                                |
     | sock.send("BOOK|...")          |
     |------------------------------>  |
     | response_event.clear()          |
     | response_event.wait(5.0) ⏸     |
     |                                 | data = sock.recv()
     |                                 | last_server_response = message
     |                                 | response_event.set() ✅
     | ▶️ продолжает работу           |
```

### Структура данных `cinema`:
```
cinema = {
    "название_фильма": {
        "время": {
            "price": 50000,
            "seats": [0, 1, 0, 1, 0]
                     ↑  ↑  ↑  ↑  ↑
                     0  1  2  3  4  ← номера мест
        }
    }
}
```