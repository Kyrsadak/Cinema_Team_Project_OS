# Cinema_Team_Project_OS
Командный проект по предмету Операционная система в университете Inha in Tashkent. Проект сделанный с помощи python, в основном используется библиотеки Socket and Threading. Идея в том чтобы клиенты подключались и могли покупать билеты на кино и фильмы
## PROBLEM STATEMENT: 
- Students often struggle to understand how multi-threaded socket systems work in real-world applications. This project demonstrates a real-time multi-client cinema ticket booking system using Python, sockets, and threading. Multiple clients can connect to the server simultaneously and book movie tickets based on availability. The server manages the shared ticket database and handles each client in a separate thread, ensuring concurrency and realistic interaction.

## TERM PROJECT DESCRIPTION:
- The goal of this project is to develop a real-time multi-client cinema ticket booking system using Python, Socket Programming, and Multithreading. The system consists of one central server and multiple clients that can connect simultaneously.
The server maintains a movie schedule for each day of the week and stores the number of available tickets for every movie. When a client connects, the server creates a dedicated thread to handle that client independently, allowing multiple users to interact with the system at the same time without blocking each other.
Clients can view all available days, select a movie, and attempt to book a ticket. The server validates ticket availability, updates its shared ticket database, and sends confirmation or a denial message back to the client.
